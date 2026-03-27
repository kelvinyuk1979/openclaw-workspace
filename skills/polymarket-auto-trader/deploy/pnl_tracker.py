#!/usr/bin/env python3
"""
Polymarket P&L Tracker
Displays current positions, unrealized P&L, and trade history.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

import requests as http_requests
from web3 import Web3

WORKSPACE = Path(__file__).resolve().parent
LOG_PATH = WORKSPACE / "trades.jsonl"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

def get_wallet_address():
    """Get wallet address from private key."""
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        # Try to read from .env file
        env_path = WORKSPACE / ".env"
        if env_path.exists():
            for line in env_path.read_text().split("\n"):
                if line.startswith("PRIVATE_KEY="):
                    private_key = line.split("=", 1)[1].strip()
                    break
    
    if not private_key:
        print("❌ PRIVATE_KEY not found. Set it in .env or environment.")
        return None
    
    try:
        w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
        acct = w3.eth.account.from_key(private_key)
        return acct.address
    except Exception as e:
        print(f"❌ Failed to derive address: {e}")
        return None

def get_usdc_balance(address):
    """Get USDC.e balance."""
    try:
        w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com'))
        abi = [{
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }]
        usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
        bal = usdc.functions.balanceOf(address).call()
        return bal / 1e6
    except Exception as e:
        print(f"⚠️  Failed to get balance: {e}")
        return 0

def get_polymarket_positions(address):
    """Fetch current positions from Polymarket Data API."""
    try:
        resp = http_requests.get(
            f"https://data-api.polymarket.com/v2/positions/current",
            params={"user": address},
            timeout=30
        )
        data = resp.json()
        return data.get("positions", [])
    except Exception as e:
        print(f"⚠️  Failed to fetch positions: {e}")
        return []

def load_trade_history():
    """Load local trade history."""
    if not LOG_PATH.exists():
        return []
    
    trades = []
    for line in LOG_PATH.read_text().strip().split("\n"):
        try:
            trades.append(json.loads(line))
        except:
            pass
    return trades

def calculate_pnl():
    """Calculate realized and unrealized P&L."""
    address = get_wallet_address()
    if not address:
        return
    
    print("\n" + "=" * 60)
    print(f"📊 Polymarket P&L Report")
    print(f"Wallet: {address[:10]}...{address[-8:]}")
    print("=" * 60)
    
    # On-chain balance
    balance = get_usdc_balance(address)
    print(f"\n💰 USDC.e Balance: ${balance:.2f}")
    
    # Current positions
    positions = get_polymarket_positions(address)
    if positions:
        print(f"\n📈 Current Positions ({len(positions)}):")
        total_invested = 0
        total_current = 0
        for pos in positions[:10]:  # Show first 10
            market = pos.get("market", {}).get("question", "Unknown")[:50]
            outcome = pos.get("outcome", "")
            shares = float(pos.get("size", 0))
            avg_price = float(pos.get("averagePrice", 0))
            current_price = float(pos.get("currentPrice", 0))
            invested = shares * avg_price
            current = shares * current_price
            pnl = current - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_current += current
            
            emoji = "🟢" if pnl >= 0 else "🔴"
            print(f"  {emoji} {market}")
            print(f"      {outcome}: {shares} shares @ ${avg_price:.2f} → ${current_price:.2f}")
            print(f"      P&L: ${pnl:+.2f} ({pnl_pct:+.1f}%)")
        
        total_pnl = total_current - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        print(f"\n  Total Invested: ${total_invested:.2f}")
        print(f"  Current Value:  ${total_current:.2f}")
        print(f"  Unrealized P&L: ${total_pnl:+.2f} ({total_pnl_pct:+.1f}%)")
    else:
        print("\n📭 No current positions")
    
    # Trade history
    trades = load_trade_history()
    if trades:
        print(f"\n📜 Trade History ({len(trades)} trades):")
        
        # Group by market
        market_trades = {}
        for t in trades:
            market = t.get("market", "Unknown")
            if market not in market_trades:
                market_trades[market] = []
            market_trades[market].append(t)
        
        for market, market_trade_list in list(market_trades.items())[:5]:
            print(f"\n  {market[:50]}")
            for t in market_trade_list:
                ts = t.get("ts", "")[:19].replace("T", " ")
                side = t.get("side", "")
                shares = t.get("shares", 0)
                price = t.get("price", 0)
                size = t.get("size_usdc", 0)
                status = t.get("status", "unknown")
                print(f"    {ts} | {side} {shares}sh @ ${price:.2f} (${size:.2f}) | {status}")
    else:
        print("\n📜 No trade history")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    calculate_pnl()
