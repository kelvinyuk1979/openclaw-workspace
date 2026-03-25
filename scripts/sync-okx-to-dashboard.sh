#!/bin/bash
# OKX 检查后自动同步数据到看板

python3 << 'PYEOF'
import json
from pathlib import Path

okx_dir = Path.home() / '.openclaw' / 'workspace' / 'skills' / 'stock-market-pro' / 'quant-trading-system'
dashboard_dir = Path.home() / '.openclaw' / 'workspace' / 'unified-trading-dashboard'

try:
    account = json.loads((okx_dir / 'data' / 'account.json').read_text())
    signals = json.loads((okx_dir / 'logs' / 'latest_signals.json').read_text())
    positions = json.loads((okx_dir / 'data' / 'positions.json').read_text())
    
    okx_status = {
        "balance": account.get('balance', 0),
        "initial": account.get('initial_capital', 0),
        "pnl": account.get('total_pnl', 0),
        "pnl_pct": round((account.get('total_pnl', 0) / account.get('initial_capital', 1)) * 100, 2),
        "positions": account.get('positions', []),
        "positions_raw": positions,
        "signals": signals.get('signals', [])
    }
    
    dashboard_dir.mkdir(exist_ok=True)
    (dashboard_dir / 'data').mkdir(exist_ok=True)
    
    (dashboard_dir / 'data' / 'okx_status.json').write_text(
        json.dumps(okx_status, indent=2, ensure_ascii=False)
    )
    print("✅ 数据同步成功")
except Exception as e:
    print(f"❌ 同步失败：{e}")
PYEOF
