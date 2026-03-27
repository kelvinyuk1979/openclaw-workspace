#!/usr/bin/env python3
"""
Telegram Alert System for Polymarket Auto-Trader
Sends alerts for trades, errors, and daily summaries.
"""
import os
import json
import requests
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parent
CONFIG_PATH = WORKSPACE / "telegram_config.json"

class TelegramAlert:
    def __init__(self):
        self.config = self.load_config()
        self.token = self.config.get("bot_token")
        self.chat_id = self.config.get("chat_id")
        self.enabled = bool(self.token and self.chat_id)
    
    def load_config(self):
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
        return {}
    
    def save_config(self, token, chat_id):
        config = {"bot_token": token, "chat_id": chat_id}
        CONFIG_PATH.write_text(json.dumps(config, indent=2))
        self.token = token
        self.chat_id = chat_id
        self.enabled = True
    
    def send(self, message, parse_mode="Markdown"):
        """Send a message to Telegram."""
        if not self.enabled:
            print("⚠️  Telegram not configured, skipping alert")
            return False
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message[:4000],  # Telegram limit
            "parse_mode": parse_mode
        }
        
        try:
            resp = requests.post(url, json=data, timeout=10)
            if resp.status_code == 200:
                print(f"✅ Alert sent to Telegram")
                return True
            else:
                print(f"❌ Telegram API error: {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Failed to send Telegram alert: {e}")
            return False
    
    def send_trade_alert(self, market, side, shares, price, edge, status):
        """Send alert when a trade is placed."""
        emoji = "✅" if status == "filled" else "⏳"
        side_emoji = "🟢" if side == "YES" else "🔴"
        
        message = f"""
{emoji} *New Trade Alert*

{side_emoji} *Side:* {side}
📊 *Market:* {market[:50]}
💰 *Shares:* {shares}
💵 *Price:* ${price:.2f}
📈 *Edge:* {edge*100:.1f}%
🔖 *Status:* {status}

_Time: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
        return self.send(message)
    
    def send_error_alert(self, error_message):
        """Send alert on critical errors."""
        message = f"""
🚨 *Critical Error Alert*

❌ *Error:*
```
{error_message[:200]}
```

_Time: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
        return self.send(message)
    
    def send_daily_summary(self, trades_count, pnl, llm_cost, balance):
        """Send daily summary report."""
        pnl_emoji = "🟢" if pnl >= 0 else "🔴"
        
        message = f"""
📊 *Daily Trading Summary*

📈 *Trades Today:* {trades_count}
💰 *P&L:* {pnl_emoji} ${pnl:+.2f}
💸 *LLM Cost:* ${llm_cost:.2f}
💵 *Balance:* ${balance:.2f}

_Time: {datetime.now().strftime("%Y-%m-%d")}
"""
        return self.send(message)
    
    def send_health_alert(self, alerts):
        """Send health check alerts."""
        if not alerts:
            return
        
        message = "🏥 *Health Check Alert*\n\n"
        for alert in alerts:
            message += f"⚠️  {alert}\n"
        message += f"\n_Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}_"
        
        return self.send(message)

def setup_telegram():
    """Interactive setup for Telegram."""
    print("=" * 50)
    print("Telegram Alert Setup")
    print("=" * 50)
    print()
    print("Step 1: Create a Telegram Bot")
    print("1. Open Telegram, search for @BotFather")
    print("2. Send /newbot")
    print("3. Enter bot name: Polymarket Trader")
    print("4. Enter username: poly_trader_alert_bot")
    print("5. Copy the Bot Token")
    print()
    
    token = input("Enter Bot Token: ").strip()
    
    print()
    print("Step 2: Get Chat ID")
    print("1. Search for your bot in Telegram, click Start")
    print("2. Visit: https://api.telegram.org/bot{}/getUpdates".format(token))
    print("3. Find 'chat':{'id':123456789}")
    print()
    
    chat_id = input("Enter Chat ID: ").strip()
    
    # Save config
    alert = TelegramAlert()
    alert.save_config(token, chat_id)
    
    # Test message
    print()
    print("Testing...")
    if alert.send("✅ Polymarket Trader alert system configured successfully!"):
        print("✅ Setup complete! You'll receive alerts in Telegram.")
    else:
        print("❌ Test failed. Check token and chat ID.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_telegram()
    else:
        print("Usage: python3 telegram_alert.py setup")
        print("       (to configure Telegram alerts)")
