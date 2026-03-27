#!/bin/bash
# Discord Webhook Alert for Polymarket Trader
# Usage: ./discord_alert.sh "Your message here"

DISCORD_WEBHOOK_URL="YOUR_WEBHOOK_URL_HERE"

send_discord() {
    local message="$1"
    
    curl -H "Content-Type: application/json" \
         -d "{\"content\": \"$message\"}" \
         "$DISCORD_WEBHOOK_URL"
}

# Test
send_discord "✅ Polymarket Trader alert test successful!"
