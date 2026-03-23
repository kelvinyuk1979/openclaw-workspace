#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一交易系统 - Web 控制面板
展示：Polymarket + A 股 + OKX 三个系统
"""

from flask import Flask, render_template, jsonify
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

WORKSPACE = Path(__file__).parent.parent
POLYMARKET_DIR = WORKSPACE / 'polymarket-trading-system'
ASHARE_DIR = WORKSPACE / 'a-share-trading-system'
OKX_DIR = WORKSPACE / 'okx-trading-system'


def load_json(path: Path, default=None):
    """加载 JSON 文件"""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default or {}


@app.route('/')
def dashboard():
    """主面板"""
    # Polymarket 数据
    poly_config = load_json(POLYMARKET_DIR / 'config' / 'unified_config.json')
    poly_scan = load_json(POLYMARKET_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    poly_sim = load_json(POLYMARKET_DIR / 'simulation.json', {"balance": 10000})
    
    # A 股数据
    ashare_config = load_json(ASHARE_DIR / 'config' / 'unified_config.json')
    ashare_scan = load_json(ASHARE_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    ashare_sim = load_json(ASHARE_DIR / 'simulation.json', {"balance": 100000})
    
    # OKX 数据
    okx_config = load_json(OKX_DIR / 'config' / 'config.json')
    okx_signals = load_json(OKX_DIR / 'logs' / 'latest_signals.json', {"signals": []})
    okx_account = load_json(OKX_DIR / 'data' / 'account.json', {"balance": 10000, "total_pnl": 0})
    okx_positions = load_json(OKX_DIR / 'data' / 'positions.json', {})
    
    return render_template('unified_dashboard.html',
        poly_config=poly_config,
        poly_scan=poly_scan,
        poly_sim=poly_sim,
        ashare_config=ashare_config,
        ashare_scan=ashare_scan,
        ashare_sim=ashare_sim,
        okx_config=okx_config,
        okx_signals=okx_signals,
        okx_account=okx_account,
        okx_positions=okx_positions,
        last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/api/polymarket/status')
def api_polymarket_status():
    """API - Polymarket 状态"""
    scan_data = load_json(POLYMARKET_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    sim_data = load_json(POLYMARKET_DIR / 'simulation.json', {"balance": 10000})
    
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


@app.route('/api/ashare/status')
def api_ashare_status():
    """API - A 股状态"""
    scan_data = load_json(ASHARE_DIR / 'logs' / 'latest_scan.json', {"results": {}})
    sim_data = load_json(ASHARE_DIR / 'simulation.json', {"balance": 100000})
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "balance": sim_data.get('balance', 100000),
        "strategies": {
            "technical": len(scan_data.get('results', {}).get('technical', {}).get('signals', [])),
            "fundamental": len(scan_data.get('results', {}).get('fundamental', {}).get('signals', [])),
            "sentiment": len(scan_data.get('results', {}).get('sentiment', {}).get('signals', []))
        }
    })


@app.route('/api/okx/status')
def api_okx_status():
    """API - OKX 状态"""
    signals_data = load_json(OKX_DIR / 'logs' / 'latest_signals.json', {"signals": []})
    account_data = load_json(OKX_DIR / 'data' / 'account.json', {"balance": 10000, "total_pnl": 0})
    positions_data = load_json(OKX_DIR / 'data' / 'positions.json', {})
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "balance": account_data.get('balance', 10000),
        "pnl": account_data.get('total_pnl', 0),
        "positions_count": len(positions_data),
        "signals": len(signals_data.get('signals', []))
    })


@app.route('/api/overview')
def api_overview():
    """API - 三个系统总览"""
    poly_sim = load_json(POLYMARKET_DIR / 'simulation.json', {"balance": 10000, "starting_balance": 10000})
    ashare_sim = load_json(ASHARE_DIR / 'simulation.json', {"balance": 100000, "starting_balance": 100000})
    okx_account = load_json(OKX_DIR / 'data' / 'account.json', {"balance": 10000, "initial_capital": 10000})
    
    poly_pnl = poly_sim.get('balance', 10000) - poly_sim.get('starting_balance', 10000)
    ashare_pnl = ashare_sim.get('balance', 100000) - ashare_sim.get('starting_balance', 100000)
    okx_pnl = okx_account.get('total_pnl', 0)
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "polymarket": {
            "balance": poly_sim.get('balance', 10000),
            "pnl": poly_pnl,
            "currency": "USDC"
        },
        "ashare": {
            "balance": ashare_sim.get('balance', 100000),
            "pnl": ashare_pnl,
            "currency": "CNY"
        },
        "okx": {
            "balance": okx_account.get('balance', 10000),
            "pnl": okx_pnl,
            "currency": "USDT"
        }
    })


if __name__ == "__main__":
    print("=" * 60)
    print("🌐 统一交易系统 Web 控制面板")
    print("=" * 60)
    print("📍 访问地址：http://localhost:5002")
    print("📊 系统：")
    print("   - Polymarket (预测市场)")
    print("   - A 股 (沪深京)")
    print("📡 API 端点：")
    print("   - /api/overview      总览")
    print("   - /api/polymarket/status  Polymarket 状态")
    print("   - /api/ashare/status      A 股状态")
    print("=" * 60)
    # 使用 threaded=True 和 debug=False 确保稳定运行
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
