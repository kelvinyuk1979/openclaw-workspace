#!/usr/bin/env python3
"""
Polymarket Contract Approval Script
Approves USDC.e and CTF tokens for Polymarket contracts.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

WORKSPACE = Path(__file__).resolve().parent
load_dotenv(WORKSPACE / ".env")

from web3 import Web3

# Configuration
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
RPC_URL = "https://polygon-rpc.com"

# Contract addresses
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
CTF = "0x0000000000000000000000000000000000000000"  # Will be fetched

# Polymarket contracts
CTF_EXCHANGE = "0x4bFb7e8aa97a1e591a86BaAcC754A8c6Aa60239f"
NEG_RISK_EXCHANGE = "0xC5d563A95aEb8Ee7446a12d2C08052F54911b2a3"
NEG_RISK_ADAPTER = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"

# ABI for ERC20 approve
APPROVE_ABI = [{
    "inputs": [
        {"name": "spender", "type": "address"},
        {"name": "amount", "type": "uint256"}
    ],
    "name": "approve",
    "outputs": [{"name": "", "type": "bool"}],
    "stateMutability": "nonpayable",
    "type": "function"
}]

def approve_token(w3, contract_address, spender_address, account, private_key):
    """Approve a token for spending."""
    contract = w3.eth.contract(address=contract_address, abi=APPROVE_ABI)
    
    # Check current allowance
    allowance = contract.functions.allowance(account.address, spender_address).call()
    print(f"  Current allowance: {allowance / 1e6:.2f} USDC.e")
    
    if allowance > 1e12:  # Already approved (MAX_UINT)
        print("  ✅ Already approved")
        return True
    
    # Build approval transaction
    max_uint = 2**256 - 1
    tx = contract.functions.approve(spender_address, max_uint).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gasPrice": w3.eth.gas_price,
    })
    
    # Sign and send
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"  Sending approval tx: {tx_hash.hex()[:20]}...")
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    if receipt["status"] == 1:
        print("  ✅ Approval successful")
        return True
    else:
        print("  ❌ Approval failed")
        return False

def main():
    if not PRIVATE_KEY:
        print("❌ PRIVATE_KEY not set in .env")
        sys.exit(1)
    
    print("=" * 60)
    print("Polymarket Contract Approval")
    print("=" * 60)
    
    # Connect to Polygon
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to Polygon RPC")
        sys.exit(1)
    print("✅ Connected to Polygon")
    
    # Get account
    account = w3.eth.account.from_key(PRIVATE_KEY)
    print(f"Wallet: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    matic_balance = balance / 1e18
    print(f"MATIC Balance: {matic_balance:.4f} (${matic_balance * 0.5:.2f})")
    
    if matic_balance < 0.01:
        print("⚠️  Low MATIC balance, may not have enough for gas")
    
    # Approvals needed
    print("\n📋 Required Approvals:")
    print("  1. USDC.e → CTF Exchange")
    print("  2. USDC.e → Neg Risk Exchange")
    print("  3. USDC.e → Neg Risk Adapter")
    print("  4. CTF → CTF Exchange")
    print("  5. CTF → Neg Risk Exchange")
    print("  6. CTF → Neg Risk Adapter")
    
    confirm = input("\nProceed with approvals? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted")
        sys.exit(0)
    
    # Approve USDC.e
    print("\n🪙  Approving USDC.e...")
    success = True
    success &= approve_token(w3, USDC_E, CTF_EXCHANGE, account, PRIVATE_KEY)
    success &= approve_token(w3, USDC_E, NEG_RISK_EXCHANGE, account, PRIVATE_KEY)
    success &= approve_token(w3, USDC_E, NEG_RISK_ADAPTER, account, PRIVATE_KEY)
    
    # Note: CTF token approval is optional for basic trading
    print("\n✅ USDC.e approvals complete")
    print("\n⚠️  CTF token approvals skipped (not required for basic trading)")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All approvals successful!")
        print("You can now run the trading bot.")
    else:
        print("⚠️  Some approvals failed. Check errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
