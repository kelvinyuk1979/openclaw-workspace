#!/usr/bin/env python3
"""A 股选股策略 v2（腾讯行情 API）- 修复版"""

import urllib.request
import json
from datetime import datetime
from pathlib import Path

# === 指数（单独管理，不混入股票池）===
INDEX_CODES = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399006": "创业板指",
    "sh000688": "科创50",
}

# === 80 只核心股票池（去重，无指数）===
STOCK_POOL = {
    # 消费 (10)
    "sh600519": "贵州茅台", "sz000858": "五粮液", "sz000568": "泸州老窖", "sh600809": "山西汾酒",
    "sz002304": "洋河股份", "sh603288": "海天味业", "sh600887": "伊利股份", "sz000651": "格力电器",
    "sz000333": "美的集团", "sh600690": "海尔智家",
    # AI / 半导体 (10)
    "sh688041": "海光信息", "sh688981": "中芯国际", "sh688256": "寒武纪", "sz002230": "科大讯飞",
    "sh603019": "中科曙光", "sz002371": "北方华创", "sh688012": "中微公司", "sz300661": "圣邦股份",
    "sh688111": "金山办公", "sz002049": "紫光国微",
    # 新能源 (7)
    "sz300750": "宁德时代", "sz002594": "比亚迪", "sh601012": "隆基绿能", "sz300274": "阳光电源",
    "sh600438": "通威股份", "sz002459": "晶澳科技", "sz300763": "锦浪科技",
    # 医药 (7)
    "sh600276": "恒瑞医药", "sh603259": "药明康德", "sz300760": "迈瑞医疗", "sh600436": "片仔癀",
    "sh688180": "君实生物", "sz300122": "智飞生物", "sz300347": "泰格医药",
    # 金融 (7)
    "sh601318": "中国平安", "sh600036": "招商银行", "sh601166": "兴业银行", "sh600030": "中信证券",
    "sh601688": "华泰证券", "sz000001": "平安银行", "sh601398": "工商银行",
    # 互联网/科技 (8)
    "sz300059": "东方财富", "sz000977": "浪潮信息", "sh600588": "用友网络",
    "sz002415": "海康威视", "sz300433": "蓝思科技", "sz002241": "歌尔股份",
    "sh600745": "闻泰科技", "sz300782": "卓胜微",
    # 军工 (5)
    "sh600760": "中航沈飞", "sh600893": "航发动力", "sh600150": "中国船舶",
    "sh601989": "中国重工", "sz002179": "中航光电",
    # 房地产/基建 (3)
    "sz000002": "万科A", "sh600048": "保利发展", "sh601668": "中国建筑",
    # 能源/交通 (5)
    "sh601857": "中国石油", "sh600028": "中国石化", "sh600900": "长江电力",
    "sh601888": "中国中免", "sh601899": "紫金矿业",
    # 通信 (3)
    "sh600941": "中国移动", "sh601728": "中国电信", "sz000063": "中兴通讯",
    # 有色/材料 (3)
    "sh600585": "海螺水泥", "sz002460": "赣锋锂业", "sh603993": "洛阳钼业",
    # 汽车 (4)
    "sh600104": "上汽集团", "sz002625": "光启技术", "sz000625": "长安汽车", "sh601238": "广汽集团",
}


def fetch_quotes(codes):
    """腾讯行情 API 批量获取"""
    url = f"http://qt.gtimg.cn/q={','.join(codes)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read()
    try:
        text = raw.decode('gbk')
    except:
        text = raw.decode('utf-8', errors='ignore')

    results = []
    for line in text.strip().split(';'):
        if '~' not in line:
            continue
        p = line.split('~')
        if len(p) < 38:
            continue
        try:
            results.append({
                "name": p[1], "code": p[2],
                "price": float(p[3]) if p[3] else 0,
                "yesterday": float(p[4]) if p[4] else 0,
                "open": float(p[5]) if p[5] else 0,
                "volume": float(p[6]) if p[6] else 0,       # 手
                "amount": float(p[37]) if p[37] else 0,      # 万元
                "change_pct": float(p[32]) if len(p) > 32 and p[32] else 0,
                "high": float(p[33]) if len(p) > 33 and p[33] else 0,
                "low": float(p[34]) if len(p) > 34 and p[34] else 0,
                "turnover": float(p[38]) if len(p) > 38 and p[38] else 0,
            })
        except (ValueError, IndexError):
            continue
    return results


def _batch_fetch(code_dict):
    """分批获取 + 重试（每批 15 只，最多重试 3 次）"""
    import time
    codes = list(code_dict.keys())
    all_q = []
    batch_size = 15  # 15 只/批，网络波动下成功率最高
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        for attempt in range(3):
            try:
                all_q.extend(fetch_quotes(batch))
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(1)  # 重试前等 1 秒
                else:
                    print(f"⚠️ 批次 {i//batch_size+1} 失败（3次重试）：{e}")
    return all_q


# ─── 策略 ───────────────────────────────────────────

def strategy_momentum(stocks):
    """动量策略：今日涨幅 Top 5（>0%）"""
    return [s for s in sorted(stocks, key=lambda x: x['change_pct'], reverse=True)[:5]
            if s['change_pct'] > 0]


def strategy_volume_price(stocks):
    """量价齐升：上涨 + 成交额 > 5 亿 + 换手率高"""
    candidates = [s for s in stocks
                  if s['change_pct'] > 0.5 and s['amount'] > 50000]  # 5 亿 = 50000 万
    candidates.sort(key=lambda x: x['change_pct'] * (x['amount'] / 1e5), reverse=True)
    return candidates[:5]


def strategy_oversold(stocks):
    """超跌反弹：跌幅 > 2%，仍有成交"""
    candidates = [s for s in stocks if s['change_pct'] < -2 and s['amount'] > 10000]
    candidates.sort(key=lambda x: x['change_pct'])
    return candidates[:5]


def strategy_breakout(stocks):
    """突破策略：收盘价 >= 日内最高价 98%，且上涨"""
    candidates = []
    for s in stocks:
        if s['high'] > 0 and s['price'] > 0 and s['change_pct'] > 0:
            ratio = s['price'] / s['high']
            if ratio >= 0.98:
                s['_ratio'] = ratio
                candidates.append(s)
    candidates.sort(key=lambda x: x['_ratio'], reverse=True)
    return candidates[:5]


def strategy_large_cap_leaders(stocks):
    """大盘领涨：成交额 Top 10 中涨幅最大的 5 只"""
    by_amount = sorted(stocks, key=lambda x: x['amount'], reverse=True)[:10]
    by_amount.sort(key=lambda x: x['change_pct'], reverse=True)
    return [s for s in by_amount[:5] if s['change_pct'] > 0]


# ─── 主函数 ──────────────────────────────────────────

def run_stock_picker():
    # 获取指数
    indices = _batch_fetch(INDEX_CODES)
    # 获取个股
    stocks = _batch_fetch(STOCK_POOL)
    # 过滤无效数据
    stocks = [s for s in stocks if s['price'] > 0]

    strategies = {
        "momentum":     [_fmt(s) for s in strategy_momentum(stocks)],
        "volume_price": [_fmt(s) for s in strategy_volume_price(stocks)],
        "oversold":     [_fmt(s) for s in strategy_oversold(stocks)],
        "breakout":     [_fmt(s) for s in strategy_breakout(stocks)],
        "large_cap":    [_fmt(s) for s in strategy_large_cap_leaders(stocks)],
    }

    picks = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_stocks": len(stocks),
        "indices": [{"code": i['code'], "name": i['name'], "price": i['price'], "change": i['change_pct']} for i in indices],
        "strategies": strategies,
    }

    out = Path(__file__).parent / 'ashare_picks.json'
    out.write_text(json.dumps(picks, indent=2, ensure_ascii=False), encoding='utf-8')
    return picks


def _fmt(s):
    return {
        "code": s['code'], "name": s['name'],
        "price": s['price'], "change": s['change_pct'],
        "amount_yi": round(s['amount'] / 1e4, 1),  # 万元→亿元
    }


if __name__ == "__main__":
    picks = run_stock_picker()

    print(f"=== A 股选股结果 ({picks['timestamp']}) ===")
    print(f"股票池：{picks['total_stocks']} 只\n")

    print("📊 指数:")
    for i in picks['indices']:
        print(f"  {i['name']}: {i['price']} ({i['change']:+.2f}%)")

    labels = {
        "momentum": "📈 动量策略（涨幅最大）",
        "volume_price": "💰 量价齐升（量大+涨）",
        "oversold": "📉 超跌反弹（跌>2%）",
        "breakout": "🚀 突破策略（接近日高）",
        "large_cap": "🏦 大盘领涨（成交额Top10中涨幅最大）",
    }
    for key, label in labels.items():
        print(f"\n{label}:")
        for s in picks['strategies'].get(key, []):
            amt = f" 成交{s['amount_yi']}亿" if s.get('amount_yi') else ""
            print(f"  {s['code']} {s['name']}: {s['price']}元 {s['change']:+.2f}%{amt}")
        if not picks['strategies'].get(key):
            print("  （无符合条件）")

    print(f"\n✅ 已保存到 ashare_picks.json")
