#!/usr/bin/env python3
"""
Polymarket Auto-Trader Health Monitor
Checks system health and logs status.
Run via cron every hour: 0 * * * * /opt/trader/bin/python3 /opt/trader/app/health_check.py
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

import requests as http_requests
from web3 import Web3

WORKSPACE = Path(__file__).resolve().parent
LOG_PATH = WORKSPACE / "trades.jsonl"
HEALTH_PATH = WORKSPACE / "health_status.json"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

def check_api_connectivity():
    """Check if Polymarket APIs are accessible."""
    try:
        resp = http_requests.get("https://gamma-api.polymarket.com/markets?limit=1", timeout=10)
        if resp.status_code == 200:
            return True, "Gamma API OK"
        return False, f"Gamma API error: {resp.status_code}"
    except Exception as e:
        return False, f"Gamma API unreachable: {e}"

def check_wallet_balance():
    """Check USDC.e balance."""
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        return None, "PRIVATE_KEY not set"
    
    try:
        w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com', request_kwargs={'timeout': 10}))
        acct = w3.eth.account.from_key(private_key)
        abi = [{"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}]
        usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
        bal = usdc.functions.balanceOf(acct.address).call()
        return bal / 1e6, f"${bal/1e6:.2f} USDC.e"
    except Exception as e:
        return None, f"Balance check failed: {e}"

def check_recent_trades():
    """Check if trades were placed recently."""
    if not LOG_PATH.exists():
        return "no_trades", "No trade history"
    
    try:
        lines = LOG_PATH.read_text().strip().split("\n")
        if not lines:
            return "no_trades", "No trades recorded"
        
        last_trade = json.loads(lines[-1])
        last_ts = datetime.fromisoformat(last_trade["ts"].replace("Z", "+00:00"))
        hours_ago = (datetime.now(last_ts.tzinfo) - last_ts).total_seconds() / 3600
        
        if hours_ago < 2:
            return "active", f"Last trade {hours_ago:.1f}h ago"
        elif hours_ago < 24:
            return "inactive", f"Last trade {hours_ago:.1f}h ago"
        else:
            return "stale", f"Last trade {hours_ago/24:.1f} days ago"
    except Exception as e:
        return "error", f"Read error: {e}"

def main():
    print("=" * 50)
    print("🏥 Polymarket Auto-Trader Health Check")
    print("=" * 50)
    
    checks = {}
    alerts = []
    
    # API Check
    api_ok, api_msg = check_api_connectivity()
    checks["api"] = {"ok": api_ok, "message": api_msg}
    print(f"\n{'✅' if api_ok else '❌'} API: {api_msg}")
    if not api_ok:
        alerts.append("API unreachable")
    
    # Wallet Balance
    balance, bal_msg = check_wallet_balance()
    checks["balance"] = {"value": balance, "message": bal_msg}
    print(f"{'✅' if balance and balance > 10 else '⚠️'}  Balance: {bal_msg}")
    if balance and balance < 10:
        alerts.append(f"Low balance: ${balance:.2f}")
    
    # Recent Activity
    status, activity_msg = check_recent_trades()
    checks["activity"] = {"status": status, "message": activity_msg}
    emoji = {"active": "✅", "inactive": "⚠️", "stale": "❌", "no_trades": "📭", "error": "❌"}.get(status, "❌")
    print(f"{emoji} Activity: {activity_msg}")
    if status in ["stale", "error"]:
        alerts.append(f"Trading inactive: {activity_msg}")
    
    # Save status
    health_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "alerts": alerts,
        "healthy": len(alerts) == 0
    }
    HEALTH_PATH.write_text(json.dumps(health_data, indent=2))
    
    print(f"\n💾 Status saved to: {HEALTH_PATH}")
    
    if alerts:
        print(f"\n⚠️  ALERTS ({len(alerts)}):")
        for alert in alerts:
            print(f"  - {alert}")
        return 1
    else:
        print("\n✅ All checks passed!")
        return 0

if __name__ == "__main__":
    from datetime import timezone
    sys.exit(main())
