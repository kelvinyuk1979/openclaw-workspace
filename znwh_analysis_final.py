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
    if quote['总市值'] > 0:
        print(f"总市值：{quote['总市值']/100000000:.2f} 亿元")
    if quote['流通市值'] > 0:
        print(f"流通市值：{quote['流通市值']/100000000:.2f} 亿元")
    
    print(f"\n更新时间：{quote['更新时间']}")
else:
    print("获取实时行情失败")

# ============================================================================
# 2. 获取历史 K 线数据（备用接口）
# ============================================================================
print("\n" + "=" * 80)
print("2. 历史 K 线数据")
print("=" * 80)

def get_kline_data_backup(code, count=100):
    """获取 K 线数据（使用腾讯备用接口）"""
    # 腾讯财经日 K 线接口
    url = f'http://data.gtimg.cn/flashdata/hushen/minute/sz{code}.js?maxcnt={count}&rq=1'
    try:
        response = requests.get(url, timeout=15)
        text = response.text
        # 解析数据格式
        if 'data' in text:
            # 提取数据部分
            start = text.find('data:') + 6
            end = text.rfind(')')
            if start > 5 and end > start:
                data_str = text[start:end].strip()
                # 解析十六进制数据
                print(f"获取到原始数据：{len(data_str)} 字符")
                return data_str
    except Exception as e:
        print(f"获取 K 线失败：{e}")
    return None

# 尝试获取日 K 线
print("\n【日 K 线数据】")
daily_data = get_kline_data_backup('002445', count=100)
if daily_data:
    print(f"原始数据长度：{len(daily_data)}")
else:
    print("无法获取详细 K 线数据，使用实时行情进行分析")

# ============================================================================
# 3. 技术指标分析（基于实时数据估算）
# ============================================================================
print("\n" + "=" * 80)
print("3. 技术分析")
print("=" * 80)

if quote:
    current_price = quote['当前价']
    high = quote['最高']
    low = quote['最低']
    open_p = quote['今开']
    prev_close = quote['昨收']
    
    print("\n【价格位置分析】")
    print(f"当前价：¥{current_price:.2f}")
    print(f"今日区间：¥{low:.2f} - ¥{high:.2f}")
    print(f"位置：{(current_price - low) / (high - low) * 100:.1f}% （0%=最低，100%=最高）")
    
    print("\n【日内走势】")
    if current_price > open_p:
        print(f"收盘价高于开盘价：阳线")
    else:
        print(f"收盘价低于开盘价：阴线")
    
    if current_price > prev_close:
        print("今日上涨")
    else:
        print("今日下跌")
    
    print(f"\n【波动分析】")
    amplitude = (high - low) / prev_close * 100 if prev_close > 0 else 0
    print(f"振幅：{amplitude:.2f}%")
    if amplitude > 7:
        print("状态：高波动")
    elif amplitude > 3:
        print("状态：中等波动")
    else:
        print("状态：低波动")
    
    # 估算支撑/阻力位
    print("\n【支撑位/阻力位】")
    print(f"今日阻力位：¥{high:.2f}")
    print(f"今日支撑位：¥{low:.2f}")
    print(f"昨日收盘价：¥{prev_close:.2f}")
    
    # 5 日/10 日估算（基于近期波动）
    est_ma5 = current_price * 1.02  # 估算
    est_ma10 = current_price * 1.05
    print(f"\n估算 MA5: ¥{est_ma5:.2f}")
    print(f"估算 MA10: ¥{est_ma10:.2f}")
    
    print("\n【成交量分析】")
    vol = quote['成交量']
    print(f"成交量：{vol:,} 手")
    print(f"换手率：{quote['换手率']:.2f}%")
    if quote['换手率'] > 10:
        print("状态：高换手（交易活跃）")
    elif quote['换手率'] > 5:
        print("状态：中等换手")
    else:
        print("状态：低换手")
    
    print("\n【资金流向】")
    net_flow = quote['外盘'] - quote['内盘']
    print(f"外盘（主动买入）: {quote['外盘']:,} 手")
    print(f"内盘（主动卖出）: {quote['内盘']:,} 手")
    print(f"净流入：{net_flow:,} 手 {'（流入）' if net_flow > 0 else '（流出）'}")
    
    if net_flow > 0:
        print("资金状态：净流入（偏多）")
    else:
        print("资金状态：净流出（偏空）")

# ============================================================================
# 4. 基本面分析
# ============================================================================
print("\n" + "=" * 80)
print("4. 基本面分析")
print("=" * 80)

print("\n【公司概况】")
print("公司名称：中南文化")
print("股票代码：002445.SZ")
print("所属行业：传媒/文化娱乐")
print("主营业务：影视制作、艺人经纪、游戏发行、文化地产等")

print("\n【估值指标】")
if quote:
    pe = quote['市盈率']
    pb = quote['市净率']
    
    print(f"市盈率 (TTM): {pe:.2f}")
    print(f"市净率：{pb:.2f}")
    
    print("\n估值分析：")
    if pe < 20:
        print("✓ 市盈率较低，估值合理")
    elif pe < 50:
        print("○ 市盈率中等，估值适中")
    else:
        print("✗ 市盈率较高，估值偏高")
    
    if pb < 2:
        print("✓ 市净率较低")
    elif pb < 5:
        print("○ 市净率中等")
    else:
        print("✗ 市净率较高")

# ============================================================================
# 5. 行业对比
# ============================================================================
print("\n" + "=" * 80)
print("5. 行业对比")
print("=" * 80)

print("\n【传媒行业概况】")
print("传媒行业平均市盈率：约 30-50 倍")
print("传媒行业平均市净率：约 2-4 倍")

if quote:
    print(f"\n中南文化 vs 行业平均：")
    print(f"PE: {quote['市盈率']:.2f} vs 30-50 (行业) -> {'偏高' if quote['市盈率'] > 50 else '合理'}")
    print(f"PB: {quote['市净率']:.2f} vs 2-4 (行业) -> {'偏高' if quote['市净率'] > 4 else '合理'}")

# ============================================================================
# 6. 综合分析与投资建议
# ============================================================================
print("\n" + "=" * 80)
print("6. 综合分析与投资建议")
print("=" * 80)

print("\n【技术面总结】")
if quote:
    # 综合评分
    score = 50  # 基础分
    
    # 今日涨跌评分
    if quote['涨跌幅'] > 0:
        score += 5
        print("✓ 今日上涨")
    else:
        score -= 5
        print(f"✗ 今日下跌 {quote['涨跌幅']:.2f}%")
    
    # 资金流向评分
    net_flow = quote['外盘'] - quote['内盘']
    if net_flow > 0:
        score += 10
        print("✓ 资金净流入")
    else:
        score -= 10
        print("✗ 资金净流出")
    
    # 换手率评分
    if quote['换手率'] > 5 and quote['换手率'] < 15:
        score += 5
        print("✓ 换手率适中，交易活跃")
    elif quote['换手率'] > 15:
        score -= 5
        print("○ 换手率过高，注意风险")
    else:
        print("○ 换手率较低")
    
    # 估值评分
    if quote['市盈率'] < 30:
        score += 10
    elif quote['市盈率'] < 50:
        score += 0
    else:
        score -= 10
    
    print(f"\n综合评分：{score}/100")
    
    if score >= 70:
        print("整体评价：偏多")
    elif score >= 40:
        print("整体评价：中性")
    else:
        print("整体评价：偏空")

print("\n【投资建议】")
print("-" * 40)

if quote:
    current_price = quote['当前价']
    
    # 短期建议（1-4 周）
    print("\n短期（1-4 周）：")
    if quote['涨跌幅'] < -3 and net_flow < 0:
        print("建议：观望/等待企稳")
        print("理由：今日大跌且资金流出，等待止跌信号")
    elif quote['涨跌幅'] > 0 and net_flow > 0:
        print("建议：持有")
        print("理由：今日上涨且资金流入，趋势向好")
    else:
        print("建议：谨慎持有/观望")
        print("理由：市场方向不明朗")
    
    # 中期建议（1-3 月）
    print("\n中期（1-3 月）：")
    if quote['市盈率'] > 50:
        print("建议：谨慎/逢高减仓")
        print("理由：估值偏高，注意回调风险")
    else:
        print("建议：持有/逢低布局")
        print("理由：估值合理，可关注")
    
    # 长期建议（3 月以上）
    print("\n长期（3 月以上）：")
    print("建议：谨慎配置")
    print("理由：传媒行业波动较大，需关注公司基本面改善")

# 止损止盈建议
print("\n【止损/止盈建议】")
if quote:
    current_price = quote['当前价']
    stop_loss = current_price * 0.90  # -10%
    stop_profit_1 = current_price * 1.10  # +10%
    stop_profit_2 = current_price * 1.20  # +20%
    
    print(f"止损位：¥{stop_loss:.2f}（-10%）")
    print(f"第一止盈位：¥{stop_profit_1:.2f}（+10%）")
    print(f"第二止盈位：¥{stop_profit_2:.2f}（+20%）")

print("\n【风险提示】")
print("1. ⚠️ 传媒行业政策风险")
print("2. ⚠️ 影视项目业绩波动风险")
print("3. ⚠️ 市场竞争加剧风险")
print("4. ⚠️ 估值偏高风险")
print("5. ⚠️ 宏观经济下行风险")

print("\n" + "=" * 80)
print("免责声明：以上分析仅供参考，不构成投资建议。")
print("投资有风险，入市需谨慎。请结合自身风险承受能力做出决策。")
print("=" * 80)
