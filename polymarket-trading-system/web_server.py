#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 统一交易系统 - Web 控制面板
Flask 轻量级看板，展示实时数据
"""

from flask import Flask, render_template, jsonify
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / 'config' / 'unified_config.json'
SCAN_LOG = SCRIPT_DIR / 'logs' / 'latest_scan.json'
SIMULATION_FILE = SCRIPT_DIR / 'simulation.json'


def load_json(path: Path, default=None):
    """加载 JSON 文件"""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default or {}


@app.route('/')
def dashboard():
    """主面板"""
    config = load_json(CONFIG_FILE)
    scan_data = load_json(SCAN_LOG, {"results": {}})
    sim_data = load_json(SIMULATION_FILE, {
        "balance": 10000,
        "starting_balance": 10000,
        "trades": [],
        "positions": {}
    })
    
    # 计算汇总
    balance = sim_data.get('balance', 10000)
    starting = sim_data.get('starting_balance', 10000)
    pnl = balance - starting
    pnl_pct = (pnl / starting * 100) if starting > 0 else 0
    
    return render_template('dashboard.html',
        config=config,
        scan_data=scan_data,
        sim_data=sim_data,
        balance=balance,
        pnl=pnl,
        pnl_pct=pnl_pct,
        last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/api/status')
def api_status():
    """API - 系统状态"""
    scan_data = load_json(SCAN_LOG, {"results": {}})
    sim_data = load_json(SIMULATION_FILE, {"balance": 10000})
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "balance": sim_data.get('balance', 10000),
        "strategies": {
            "quant_core": len(scan_data.get('results', {}).get('quant', {}).get('signals', [])),
            "weather_arb": len(scan_data.get('results', {}).get('weather', {}).get('signals', [])),
            "event_trading": len(scan_data.get('results', {}).get('event', {}).get('signals', []))
        }
    })


@app.route('/api/signals')
def api_signals():
    """API - 所有信号"""
    scan_data = load_json(SCAN_LOG, {"results": {}})
    return jsonify(scan_data.get('results', {}))


@app.route('/api/trades')
def api_trades():
    """API - 交易记录"""
    sim_data = load_json(SIMULATION_FILE, {"trades": []})
    return jsonify(sim_data.get('trades', []))


if __name__ == "__main__":
    print("=" * 50)
    print("🌐 Polymarket Web 控制面板")
    print("=" * 50)
    print("📍 访问地址：http://localhost:5000")
    print("📊 API 端点：")
    print("   - /api/status   系统状态")
    print("   - /api/signals  所有信号")
    print("   - /api/trades   交易记录")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5002, debug=False)
