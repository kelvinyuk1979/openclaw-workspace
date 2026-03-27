#!/usr/bin/env python3
"""
Polymarket Auto-Trader - LIVE TRADING via direct CLOB API
Scans markets, evaluates with LLM, sizes positions with Kelly criterion, executes trades.
"""
import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
os.chdir(WORKSPACE)
from dotenv import load_dotenv
load_dotenv(WORKSPACE / ".env")

import requests as http_requests
from web3 import Web3
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(WORKSPACE / "trades.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("trader")

# Configuration
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
LLM_API_KEY = os.environ.get("LLM_API_KEY")
BUDGET_PATH = WORKSPACE / "budget_spent.txt"
LOG_PATH = WORKSPACE / "trades.jsonl"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
MIN_SHARES = 5.1  # Polymarket minimum is 5
EDGE_THRESHOLD = 0.05  # 5% minimum edge
MAX_LLM_BUDGET = 5.0  # Max $5 per cycle for LLM inference

# Contract addresses for approvals
NEG_RISK_ADAPTER = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"

if not PRIVATE_KEY or not LLM_API_KEY:
    log.error("Missing PRIVATE_KEY or LLM_API_KEY in .env")
    sys.exit(1)

class Budget:
    """Track LLM inference spending."""
    def __init__(self):
        self.spent = 0.0
        if BUDGET_PATH.exists():
            try:
                self.spent = float(BUDGET_PATH.read_text().strip())
            except:
                pass
    
    def record(self, input_tokens, output_tokens):
        """Record LLM usage cost (Haiku pricing)."""
        cost = (input_tokens / 1e6) * 0.25 + (output_tokens / 1e6) * 1.25
        self.spent += cost
        BUDGET_PATH.write_text(f"{self.spent:.6f}")
        return cost
    
    @property
    def remaining(self):
        return max(0, MAX_LLM_BUDGET - self.spent)
    
    def reset_if_needed(self):
        """Reset budget daily."""
        last_reset_path = WORKSPACE / "budget_last_reset.txt"
        today = datetime.now().strftime("%Y-%m-%d")
        if last_reset_path.exists():
            last_reset = last_reset_path.read_text().strip()
            if last_reset != today:
                self.spent = 0.0
                BUDGET_PATH.write_text("0.0")
                last_reset_path.write_text(today)
                log.info("Budget reset for new day")
        else:
            last_reset_path.write_text(today)

def get_bankroll():
    """Get actual USDC.e balance from chain."""
    try:
        w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com', request_kwargs={'timeout': 15}))
        acct = w3.eth.account.from_key(PRIVATE_KEY)
        abi = [{
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }]
        usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
        bal = usdc.functions.balanceOf(acct.address).call()
        return bal / 1e6
    except Exception as e:
        log.warning(f"Failed to get balance: {e}")
        return 0

def evaluate_market(market, client):
    """Use LLM to estimate true probability."""
    prompt = f"""Estimate TRUE probability (0.0-1.0) that YES shares win.

Market Question: {market['question']}
Description: {market['description'][:400]}
Current YES Price: ${market['prices'][0]:.3f} (implies {market['prices'][0]*100:.1f}% probability)
Resolution Date: {market['end_date']}

Consider:
1. Recent news and events
2. Base rates and historical patterns
3. Time remaining until resolution
4. Any asymmetric information

Reply ONLY with a number between 0.0 and 1.0 (e.g., 0.65)."""

    try:
        resp = http_requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": LLM_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 20,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = resp.json()
        usage = data.get("usage", {})
        cost = budget.record(usage.get("input_tokens", 300), usage.get("output_tokens", 10))
        
        text = data["content"][0]["text"].strip()
        for word in text.split():
            try:
                value = float(word.strip(".,;:()"))
                if 0 <= value <= 1:
                    return value, cost
            except:
                continue
        return None, cost
    except Exception as e:
        log.warning(f"LLM evaluation failed: {e}")
        return None, 0

def place_order(client, market, side, token_idx, fair_value, market_price, bankroll, edge):
    """Place a limit order on CLOB."""
    # Kelly criterion calculation
    if side == "YES":
        prob = fair_value
        price = market_price
    else:  # NO
        prob = 1.0 - fair_value
        price = 1.0 - market_price
    
    # Kelly formula: f = (bp - q) / b where b = (1-p)/p
    b = (1 - price) / price
    kelly_f = (b * prob - (1 - prob)) / b
    
    # Use half-Kelly, cap at 25% of bankroll
    frac = min(kelly_f * 0.5, 0.25)
    if frac <= 0:
        return None
    
    size_usdc = frac * bankroll
    shares = round(size_usdc / price, 1)
    
    # Enforce minimum shares
    if shares < MIN_SHARES:
        shares = MIN_SHARES
        size_usdc = shares * price
    
    # Cap at 30% of bankroll for single position
    if size_usdc > bankroll * 0.30:
        log.info(f"Skipping {market['question'][:50]} - position size too large")
        return None
    
    # Round price
    price_rounded = round(price, 2)
    price_rounded = max(0.01, min(0.99, price_rounded))
    
    token_id = market["tokens"][token_idx]
    
    log.info(f"Placing order: {side} {shares} shares @ ${price_rounded} on '{market['question'][:50]}'")
    
    try:
        order_args = OrderArgs(
            token_id=token_id,
            price=price_rounded,
            size=shares,
            side=BUY
        )
        signed = client.create_order(order_args)
        resp = client.post_order(signed, OrderType.GTC)
        
        order_id = resp.get("orderID", "unknown") if isinstance(resp, dict) else str(resp)
        status = resp.get("status", "unknown") if isinstance(resp, dict) else "unknown"
        
        log.info(f"Order placed: {order_id} (status: {status})")
        
        # Log trade
        trade_record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "market": market["question"],
            "side": side,
            "shares": shares,
            "price": price_rounded,
            "size_usdc": round(size_usdc, 2),
            "fair_value": round(fair_value, 4),
            "edge": round(edge, 4),
            "order_id": order_id,
            "status": status
        }
        
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(trade_record) + "\n")
        
        return trade_record
    except Exception as e:
        log.error(f"Order failed: {e}")
        return None

def main():
    log.info("=" * 60)
    log.info("Polymarket Auto-Trader starting...")
    log.info("=" * 60)
    
    # Initialize budget
    budget.reset_if_needed()
    log.info(f"LLM Budget: ${budget.spent:.4f} spent, ${budget.remaining:.4f} remaining")
    
    # Get bankroll
    bankroll = get_bankroll()
    log.info(f"Bankroll (USDC.e on-chain): ${bankroll:.2f}")
    
    if bankroll < 10:
        log.error("Insufficient bankroll (<$10 USDC.e). Exiting.")
        sys.exit(1)
    
    # Authenticate with CLOB
    log.info("Authenticating with CLOB...")
    try:
        client = ClobClient(
            "https://clob.polymarket.com",
            key=PRIVATE_KEY,
            chain_id=137,
            signature_type=0  # EOA wallet, not proxy
        )
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        log.info("CLOB authentication successful")
    except Exception as e:
        log.error(f"CLOB auth failed: {e}")
        sys.exit(1)
    
    # Scan markets
    log.info("Scanning markets...")
    all_markets = []
    for offset in range(0, 500, 100):
        try:
            resp = http_requests.get(
                "https://gamma-api.polymarket.com/markets",
                params={"limit": 100, "offset": offset, "active": "true", "closed": "false"},
                timeout=30
            )
            batch = resp.json()
            if not batch:
                break
            for m in batch:
                try:
                    prices = json.loads(m.get("outcomePrices", "[]"))
                    tokens = json.loads(m.get("clobTokenIds", "[]"))
                    if len(prices) >= 2 and len(tokens) >= 2:
                        p0 = float(prices[0])
                        # Filter: only trade markets with reasonable prices (5%-95%)
                        if p0 < 0.05 or p0 > 0.95:
                            continue
                        all_markets.append({
                            "question": m.get("question", ""),
                            "description": m.get("description", "")[:400],
                            "prices": [float(p) for p in prices],
                            "tokens": tokens,
                            "volume": float(m.get("volume", 0)),
                            "end_date": m.get("endDate", "")[:10]
                        })
                except:
                    continue
        except Exception as e:
            log.warning(f"Failed to fetch markets batch: {e}")
            break
    
    all_markets.sort(key=lambda x: x["volume"], reverse=True)
    log.info(f"Found {len(all_markets)} tradeable markets")
    
    # Load existing positions to avoid duplicates
    existing_markets = set()
    if LOG_PATH.exists():
        for line in LOG_PATH.read_text().strip().split("\n"):
            try:
                d = json.loads(line)
                existing_markets.add(d.get("market", ""))
            except:
                pass
    log.info(f"Skipping {len(existing_markets)} already-traded markets")
    
    # Prioritize short-term markets (end within 30 days)
    now = datetime.now(timezone.utc)
    short_term = []
    long_term = []
    for m in all_markets:
        try:
            end_date = datetime.fromisoformat(m["end_date"] + "T00:00:00+00:00")
            days_left = (end_date - now).days
            if days_left <= 30:
                short_term.append(m)
            else:
                long_term.append(m)
        except:
            long_term.append(m)
    
    # Process short-term first, then some long-term
    markets_to_eval = short_term + long_term[:max(0, 40 - len(short_term))]
    log.info(f"Evaluating {len(markets_to_eval)} markets ({len(short_term)} short-term)")
    
    # Evaluate and find opportunities
    opportunities = []
    total_eval_cost = 0
    eval_count = 0
    
    for m in markets_to_eval:
        if budget.remaining < 0.01:
            log.info("LLM budget exhausted, stopping evaluation")
            break
        if m["question"] in existing_markets:
            continue
        
        fair, cost = evaluate_market(m, client)
        total_eval_cost += cost
        eval_count += 1
        
        if fair is None:
            continue
        
        market_price = m["prices"][0]
        edge = abs(fair - market_price)
        
        if edge > EDGE_THRESHOLD:
            side = "YES" if fair > market_price else "NO"
            log.info(f"EDGE FOUND: {side} on '{m['question'][:50]}' | market={market_price:.3f} fair={fair:.3f} edge={edge:.3f}")
            opportunities.append((m, fair, edge, side))
    
    log.info(f"Found {len(opportunities)} opportunities. Eval cost: ${total_eval_cost:.4f} ({eval_count} markets)")
    
    # Place orders (max 8 trades per cycle)
    trades_placed = 0
    for market, fair, edge, side in sorted(opportunities, key=lambda x: -x[2])[:8]:
        market_price = market["prices"][0]
        token_idx = 0 if side == "YES" else 1
        
        result = place_order(client, market, side, token_idx, fair, market_price, bankroll, edge)
        if result:
            trades_placed += 1
            existing_markets.add(market["question"])
    
    # Summary
    log.info("=" * 60)
    log.info(f"COMPLETE: {trades_placed} trades placed")
    log.info(f"Bankroll: ${bankroll:.2f} | LLM spent: ${budget.spent:.4f}")
    log.info("=" * 60)

if __name__ == "__main__":
    budget = Budget()
    main()
