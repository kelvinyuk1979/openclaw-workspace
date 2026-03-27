#!/bin/bash
# Polymarket Auto-Trader VPS Setup Script
# Run on a non-US VPS (e.g., DigitalOcean Amsterdam, Hetzner Finland)

set -e

echo "=== Polymarket Auto-Trader Setup ==="
echo ""

# Install Python
echo "Installing Python..."
apt update && apt install -y python3 python3-venv python3-pip

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv /opt/trader
/opt/trader/bin/pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
/opt/trader/bin/pip install py-clob-client==0.9.2 python-dotenv==1.0.1 web3==7.6.0 requests==2.32.3 anthropic==0.18.0

# Create app directory
mkdir -p /opt/trader/app
mkdir -p /opt/trader/logs

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Copy your .env file to /opt/trader/app/.env"
echo "   PRIVATE_KEY=<your-polygon-wallet-private-key>"
echo "   LLM_API_KEY=<your-anthropic-api-key>"
echo ""
echo "2. Run approval script:"
echo "   /opt/trader/bin/python3 /opt/trader/app/approve_contracts.py"
echo ""
echo "3. Copy trading scripts to /opt/trader/app/"
echo ""
echo "4. Set up cron:"
echo "   crontab -e"
echo "   */10 * * * * cd /opt/trader/app && /opt/trader/bin/python3 run_trade.py >> /opt/trader/logs/cron.log 2>&1"
echo ""
echo "5. Monitor:"
echo "   tail -f /opt/trader/logs/cron.log"
echo "   /opt/trader/bin/python3 /opt/trader/app/pnl_tracker.py"
