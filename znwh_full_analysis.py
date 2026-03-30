#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中南文化 (002445.SZ) 股票完整分析报告
使用腾讯财经接口获取数据
"""

import requests
import json
from datetime import datetime, timedelta

print("=" * 80)
print("中南文化 (002445.SZ) 股票分析报告")
print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# 1. 获取实时行情（腾讯财经接口）
# ============================================================================
print("\n" + "=" * 80)
print("1. 实时行情数据")
print("=" * 80)

def parse_tencent_quote(code):
    """解析腾讯财经行情数据"""
    url = f'http://qt.gtimg.cn/q={code}'
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'gbk'
        text = response.text
        
        # 解析数据 v_sz002445="51~中南文化~002445~4.21~..."
        if '=' in text:
            data_str = text.split('=')[1].strip('"').strip('"')
            parts = data_str.split('~')
            
            if len(parts) >= 50:
                return {
                    '代码': parts[2],
                    '名称': parts[1],
                    '当前价': float(parts[3]) if parts[3] else 0,
                    '昨收': float(parts[4]) if parts[4] else 0,
                    '今开': float(parts[5]) if parts[5] else 0,
                    '成交量': int(parts[6]) if parts[6] else 0,
                    '外盘': int(parts[7]) if parts[7] else 0,
                    '内盘': int(parts[8]) if parts[8] else 0,
                    '买一价': float(parts[9]) if parts[9] else 0,
                    '买一量': int(parts[10]) if parts[10] else 0,
                    '卖一价': float(parts[11]) if parts[11] else 0,
                    '卖一量': int(parts[12]) if parts[12] else 0,
                    '涨跌额': float(parts[31]) if len(parts) > 31 and parts[31] else 0,
                    '涨跌幅': float(parts[32]) if len(parts) > 32 and parts[32] else 0,
                    '最高': float(parts[33]) if len(parts) > 33 and parts[33] else 0,
                    '最低': float(parts[34]) if len(parts) > 34 and parts[34] else 0,
                    '成交额': float(parts[36]) if len(parts) > 36 and parts[36] else 0,
                    '换手率': float(parts[43]) if len(parts) > 43 and parts[43] else 0,
                    '市盈率': float(parts[39]) if len(parts) > 39 and parts[39] else 0,
                    '总市值': float(parts[45]) if len(parts) > 45 and parts[45] else 0,
                    '流通市值': float(parts[46]) if len(parts) > 46 and parts[46] else 0,
                    '市净率': float(parts[52]) if len(parts) > 52 and parts[52] else 0,
                    '更新时间': parts[30] if len(parts) > 30 else ''
                }
    except Exception as e:
        print(f"获取行情失败：{e}")
    return None

quote = parse_tencent_quote('sz002445')
if quote:
    print(f"\n股票名称：{quote['名称']}")
    print(f"股票代码：{quote['代码']}")
    print(f"\n【价格信息】")
    print(f"当前价：¥{quote['当前价']:.2f}")
    print(f"涨跌额：{quote['涨跌额']:.2f}")
    print(f"涨跌幅：{quote['涨跌幅']:.2f}%")
    print(f"今开：¥{quote['今开']:.2f}")
    print(f"昨收：¥{quote['昨收']:.2f}")
    print(f"最高：¥{quote['最高']:.2f}")
    print(f"最低：¥{quote['最低']:.2f}")
    
    print(f"\n【成交信息】")
    print(f"成交量：{quote['成交量']:,} 手")
    print(f"成交额：{quote['成交额']:,.0f} 元")
    print(f"换手率：{quote['换手率']:.2f}%")
    
    print(f"\n【买卖盘口】")
    print(f"买一：¥{quote['买一价']:.2f} x {quote['买一量']:,} 手")
    print(f"卖一：¥{quote['卖一价']:.2f} x {quote['卖一量']:,} 手")
    print(f"外盘：{quote['外盘']:,} 手")
    print(f"内盘：{quote['内盘']:,} 手")
    
    print(f"\n【估值指标】")
    print(f"市盈率 (TTM): {quote['市盈率']:.2f}")
    print(f"市净率：{quote['市净率']:.2f}")
    print(f"总市值：{quote['总市值']/100000000:.2f} 亿元")
    print(f"流通市值：{quote['流通市值']/100000000:.2f} 亿元")
    
    print(f"\n更新时间：{quote['更新时间']}")
else:
    print("获取实时行情失败")

# ============================================================================
# 2. 获取历史 K 线数据
# ============================================================================
print("\n" + "=" * 80)
print("2. 历史 K 线数据")
print("=" * 80)

def get_kline_data(code, period='d', count=100):
    """获取 K 线数据（腾讯财经接口）"""
    # period: d=日 K, w=周 K, m=月 K
    url = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{period},,{count},qfq'
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'data' in data and code in data['data']:
            stock_data = data['data'][code]
            if period == 'd' and 'qfqday' in stock_data:
                return stock_data['qfqday']
            elif period == 'w' and 'week' in stock_data:
                return stock_data['week']
            elif period == 'm' and 'month' in stock_data:
                return stock_data['month']
    except Exception as e:
        print(f"获取 K 线失败：{e}")
    return None

# 获取日 K 线
print("\n【日 K 线数据】")
daily_k = get_kline_data('sz002445', period='d', count=120)
if daily_k and len(daily_k) > 0:
    print(f"数据条数：{len(daily_k)}")
    print("\n最近 10 个交易日：")
    print("日期        开盘    最高    最低    收盘   成交量")
    print("-" * 55)
    for day in daily_k[-10:]:
        # 格式：[日期，开盘，收盘，最高，最低，成交量，成交额，换手率]
        date = day[0]
        open_p = float(day[1])
        close_p = float(day[2])
        high_p = float(day[3])
        low_p = float(day[4])
        vol = int(day[5]) if len(day) > 5 else 0
        print(f"{date}  {open_p:.2f}   {high_p:.2f}   {low_p:.2f}   {close_p:.2f}   {vol:,}")
    
    # 保存到文件
    with open('/Users/kelvin/.openclaw/workspace/znwh_daily_k.txt', 'w', encoding='utf-8') as f:
        f.write("日期，开盘，收盘，最高，最低，成交量\n")
        for day in daily_k:
            f.write(f"{day[0]},{day[1]},{day[2]},{day[3]},{day[4]},{day[5]}\n")
    print("\n数据已保存到：znwh_daily_k.txt")
else:
    print("获取日 K 线失败")

# 获取周 K 线
print("\n【周 K 线数据】")
weekly_k = get_kline_data('sz002445', period='w', count=52)
if weekly_k and len(weekly_k) > 0:
    print(f"数据条数：{len(weekly_k)}")
    print("\n最近 10 周：")
    print("日期        开盘    最高    最低    收盘   成交量")
    print("-" * 55)
    for week in weekly_k[-10:]:
        date = week[0]
        open_p = float(week[1])
        close_p = float(week[2])
        high_p = float(week[3])
        low_p = float(week[4])
        vol = int(week[5]) if len(week) > 5 else 0
        print(f"{date}  {open_p:.2f}   {high_p:.2f}   {low_p:.2f}   {close_p:.2f}   {vol:,}")
else:
    print("获取周 K 线失败")

# ============================================================================
# 3. 技术指标分析
# ============================================================================
print("\n" + "=" * 80)
print("3. 技术指标分析")
print("=" * 80)

if daily_k and len(daily_k) > 20:
    # 提取收盘价数据
    closes = [float(day[2]) for day in daily_k]
    highs = [float(day[3]) for day in daily_k]
    lows = [float(day[4]) for day in daily_k]
    volumes = [int(day[5]) if len(day) > 5 else 0 for day in daily_k]
    
    current_price = closes[-1]
    
    # 计算均线
    def calc_ma(data, period):
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    ma5 = calc_ma(closes, 5)
    ma10 = calc_ma(closes, 10)
    ma20 = calc_ma(closes, 20)
    ma60 = calc_ma(closes, 60)
    ma120 = calc_ma(closes, 120)
    
    print("\n【均线系统】")
    print(f"当前价格：¥{current_price:.2f}")
    if ma5:
        print(f"MA5:  ¥{ma5:.2f}  {'价格在上' if current_price > ma5 else '价格在下'}")
    if ma10:
        print(f"MA10: ¥{ma10:.2f}  {'价格在上' if current_price > ma10 else '价格在下'}")
    if ma20:
        print(f"MA20: ¥{ma20:.2f}  {'价格在上' if current_price > ma20 else '价格在下'}")
    if ma60:
        print(f"MA60: ¥{ma60:.2f}  {'价格在上' if current_price > ma60 else '价格在下'}")
    if ma120:
        print(f"MA120: ¥{ma120:.2f}  {'价格在上' if current_price > ma120 else '价格在下'}")
    
    # 均线排列分析
    if ma5 and ma10 and ma20:
        if ma5 > ma10 > ma20:
            print("均线排列：多头排列（看涨信号）")
        elif ma5 < ma10 < ma20:
            print("均线排列：空头排列（看跌信号）")
        else:
            print("均线排列：混乱（震荡）")
    
    # 计算 RSI
    def calc_rsi(data, period=14):
        if len(data) < period + 1:
            return None
        gains = []
        losses = []
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    rsi14 = calc_rsi(closes, 14)
    print(f"\n【RSI 指标】")
    if rsi14:
        print(f"RSI(14): {rsi14:.2f}")
        if rsi14 > 70:
            print("状态：超买区（警惕回调风险）")
        elif rsi14 < 30:
            print("状态：超卖区（可能存在反弹机会）")
        else:
            print("状态：中性区域")
    
    # 计算 MACD
    def calc_ema(data, period):
        if len(data) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        for val in data[period:]:
            ema = (val - ema) * multiplier + ema
        return ema
    
    ema12 = calc_ema(closes, 12)
    ema26 = calc_ema(closes, 26)
    if ema12 and ema26:
        macd = ema12 - ema26
        print(f"\n【MACD 指标】")
        print(f"MACD: {macd:.4f}")
        print(f"状态：{'金叉（偏多）' if macd > 0 else '死叉（偏空）'}")
    
    # 支撑位/阻力位
    print("\n【支撑位/阻力位】")
    recent_high = max(highs[-20:])
    recent_low = min(lows[-20:])
    high_60 = max(highs[-60:]) if len(highs) >= 60 else max(highs)
    low_60 = min(lows[-60:]) if len(lows) >= 60 else min(lows)
    
    print(f"近期阻力位（20 日高点）: ¥{recent_high:.2f}")
    print(f"近期支撑位（20 日低点）: ¥{recent_low:.2f}")
    print(f"中期阻力位（60 日高点）: ¥{high_60:.2f}")
    print(f"中期支撑位（60 日低点）: ¥{low_60:.2f}")
    
    # 成交量分析
    print("\n【成交量分析】")
    avg_vol_5 = sum(volumes[-5:]) / 5
    avg_vol_20 = sum(volumes[-20:]) / 20
    current_vol = volumes[-1]
    
    print(f"当日成交量：{current_vol:,} 手")
    print(f"5 日均量：{avg_vol_5:,.0f} 手")
    print(f"20 日均量：{avg_vol_20:,.0f} 手")
    
    vol_ratio = current_vol / avg_vol_20 if avg_vol_20 > 0 else 0
    print(f"量比（当日/20 日均）: {vol_ratio:.2f}")
    if vol_ratio > 2:
        print("状态：放量明显")
    elif vol_ratio < 0.5:
        print("状态：缩量明显")
    else:
        print("状态：正常")

# ============================================================================
# 4. 基本面数据（腾讯财经 F10）
# ============================================================================
print("\n" + "=" * 80)
print("4. 基本面分析")
print("=" * 80)

def get_fundamental_data(code):
    """获取基本面数据"""
    url = f'http://web.ifzq.gtimg.cn/appstock/app/f10/summary/get?param={code}'
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        return data
    except Exception as e:
        print(f"获取基本面数据失败：{e}")
    return None

print("\n【公司概况】")
print("中南文化（002445.SZ）")
print("所属行业：传媒/文化娱乐")
print("主营业务：影视制作、艺人经纪、游戏发行、文化地产等")

print("\n【财务指标】")
# 从行情数据中获取的估值指标
if quote:
    print(f"市盈率 (TTM): {quote['市盈率']:.2f}")
    print(f"市净率：{quote['市净率']:.2f}")
    print(f"总市值：{quote['总市值']/100000000:.2f} 亿元")
    print(f"流通市值：{quote['流通市值']/100000000:.2f} 亿元")

# ============================================================================
# 5. 资金流向
# ============================================================================
print("\n" + "=" * 80)
print("5. 资金流向")
print("=" * 80)

def get_money_flow(code):
    """获取资金流向数据"""
    url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MoneyFlow.stock_{code}'
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return data
    except Exception as e:
        print(f"获取资金流向失败：{e}")
    return None

if quote:
    print(f"\n【今日资金】")
    print(f"外盘（主动买入）: {quote['外盘']:,} 手")
    print(f"内盘（主动卖出）: {quote['内盘']:,} 手")
    net_flow = quote['外盘'] - quote['内盘']
    print(f"净流入：{net_flow:,} 手 {'（流入）' if net_flow > 0 else '（流出）'}")

# ============================================================================
# 6. 综合分析
# ============================================================================
print("\n" + "=" * 80)
print("6. 综合分析与投资建议")
print("=" * 80)

print("\n【技术面总结】")
if daily_k and len(daily_k) > 20:
    # 综合评分
    score = 50  # 基础分
    
    # 均线评分
    if ma5 and ma10 and ma20:
        if ma5 > ma10 > ma20:
            score += 10
            print("✓ 均线多头排列")
        elif ma5 < ma10 < ma20:
            score -= 10
            print("✗ 均线空头排列")
    
    # RSI 评分
    if rsi14:
        if 30 < rsi14 < 70:
            score += 5
            print("✓ RSI 中性区域")
        elif rsi14 < 30:
            score += 10
            print("✓ RSI 超卖，可能反弹")
        else:
            score -= 10
            print("✗ RSI 超买，警惕回调")
    
    # MACD 评分
    if ema12 and ema26:
        if macd > 0:
            score += 5
            print("✓ MACD 金叉")
        else:
            score -= 5
            print("✗ MACD 死叉")
    
    # 成交量评分
    if vol_ratio > 1:
        score += 5
        print("✓ 成交量放大")
    else:
        score -= 5
        print("✗ 成交量萎缩")
    
    print(f"\n技术面综合评分：{score}/100")
    
    if score >= 70:
        print("技术面：偏多")
    elif score >= 40:
        print("技术面：中性")
    else:
        print("技术面：偏空")

print("\n【基本面总结】")
if quote:
    pe = quote['市盈率']
    pb = quote['市净率']
    
    if pe < 20:
        print("✓ 市盈率较低，估值合理")
    elif pe < 50:
        print("○ 市盈率中等")
    else:
        print("✗ 市盈率较高，估值偏高")
    
    if pb < 2:
        print("✓ 市净率较低")
    elif pb < 5:
        print("○ 市净率中等")
    else:
        print("✗ 市净率较高")

print("\n【投资建议】")
print("-" * 40)

# 短期建议（1-4 周）
print("\n短期（1-4 周）：")
if daily_k and len(daily_k) > 0:
    if current_price > ma20 and rsi14 and rsi14 < 70:
        print("建议：持有/逢低买入")
        print("理由：价格在 20 日均线上方，RSI 未超买")
    elif current_price < ma20:
        print("建议：观望/谨慎持有")
        print("理由：价格在 20 日均线下方，等待企稳信号")
    else:
        print("建议：观望")
        print("理由：技术指标中性，等待明确信号")

# 中期建议（1-3 月）
print("\n中期（1-3 月）：")
if ma60 and current_price > ma60:
    print("建议：持有")
    print("理由：价格在 60 日均线上方，中期趋势向好")
elif ma60 and current_price < ma60:
    print("建议：观望/逢低布局")
    print("理由：价格在 60 日均线下方，等待突破信号")
else:
    print("建议：观望")

# 长期建议（3 月以上）
print("\n长期（3 月以上）：")
if quote and quote['市盈率'] < 30:
    print("建议：可考虑长期配置")
    print("理由：估值合理，传媒行业长期向好")
else:
    print("建议：谨慎配置")
    print("理由：需关注公司基本面改善情况")

# 止损止盈建议
print("\n【止损/止盈建议】")
if daily_k and len(daily_k) > 0:
    stop_loss = current_price * 0.90  # -10%
    stop_profit_1 = current_price * 1.10  # +10%
    stop_profit_2 = current_price * 1.20  # +20%
    
    print(f"止损位：¥{stop_loss:.2f}（-10%）")
    print(f"第一止盈位：¥{stop_profit_1:.2f}（+10%）")
    print(f"第二止盈位：¥{stop_profit_2:.2f}（+20%）")
    
    print("\n【风险提示】")
    print("1. 传媒行业政策风险")
    print("2. 影视项目业绩波动风险")
    print("3. 市场竞争加剧风险")
    print("4. 宏观经济下行风险")
    print("\n*以上分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。*")

print("\n" + "=" * 80)
print("分析完成")
print("=" * 80)
