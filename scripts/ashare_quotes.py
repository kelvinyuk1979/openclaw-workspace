#!/usr/bin/env python3
"""A 股实时行情获取（腾讯行情 API）"""

import urllib.request
import json
from datetime import datetime

# 监控的 A 股池（蓝筹 + 热门赛道）
STOCK_POOL = {
    # 消费白马
    "sh600519": "贵州茅台",
    "sz000858": "五粮液",
    # 新能源
    "sz300750": "宁德时代",
    "sz002594": "比亚迪",
    # 金融
    "sh601318": "中国平安",
    "sh600036": "招商银行",
    # 医药
    "sh600276": "恒瑞医药",
    "sh603259": "药明康德",
    # 科技
    "sz300059": "东方财富",
    "sh688981": "中芯国际",
    # AI/半导体
    "sh688041": "海光信息",
    "sz002230": "科大讯飞",
    # 互联网
    "sh600745": "闻泰科技",
    "sz000977": "浪潮信息",
    # 指数
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
}

def fetch_quotes(codes):
    """从腾讯行情 API 获取实时数据"""
    url = f"http://qt.gtimg.cn/q={','.join(codes)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=10)
    raw = resp.read()
    
    # 尝试 gbk 解码
    try:
        text = raw.decode('gbk')
    except:
        text = raw.decode('utf-8', errors='ignore')
    
    results = []
    for line in text.strip().split(';'):
        if '~' not in line:
            continue
        parts = line.split('~')
        if len(parts) < 40:
            continue
        
        results.append({
            "name": parts[1],
            "code": parts[2],
            "price": float(parts[3]) if parts[3] else 0,
            "yesterday_close": float(parts[4]) if parts[4] else 0,
            "open": float(parts[5]) if parts[5] else 0,
            "volume": float(parts[6]) if parts[6] else 0,  # 手
            "amount": float(parts[37]) if len(parts) > 37 and parts[37] else 0,  # 万元
            "change_pct": float(parts[32]) if len(parts) > 32 and parts[32] else 0,
            "high": float(parts[33]) if len(parts) > 33 and parts[33] else 0,
            "low": float(parts[34]) if len(parts) > 34 and parts[34] else 0,
            "pe": float(parts[39]) if len(parts) > 39 and parts[39] else 0,
        })
    
    return results

def get_ashare_data():
    """获取 A 股数据并分析"""
    codes = list(STOCK_POOL.keys())
    quotes = fetch_quotes(codes)
    
    # 分离指数和个股
    indices = [q for q in quotes if q['code'].startswith('0') and len(q['code']) == 6 and q['code'][0] == '0']
    stocks = [q for q in quotes if q not in indices]
    
    # 按涨跌幅排序
    stocks.sort(key=lambda x: x['change_pct'], reverse=True)
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "indices": [q for q in quotes if q['code'] in ['000001', '399001', '399006']],
        "top_gainers": stocks[:5],
        "top_losers": stocks[-3:],
        "all_stocks": stocks
    }

if __name__ == "__main__":
    data = get_ashare_data()
    
    print(f"=== A 股行情 ({data['timestamp']}) ===\n")
    
    print("📊 指数:")
    for idx in data['indices']:
        print(f"  {idx['name']}: {idx['price']} ({idx['change_pct']:+.2f}%)")
    
    print(f"\n📈 涨幅前 5:")
    for s in data['top_gainers']:
        print(f"  {s['code']} {s['name']}: {s['price']}元 {s['change_pct']:+.2f}%")
    
    print(f"\n📉 跌幅前 3:")
    for s in data['top_losers']:
        print(f"  {s['code']} {s['name']}: {s['price']}元 {s['change_pct']:+.2f}%")
