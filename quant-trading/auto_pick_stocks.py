#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短线选股策略 - 自动运行版
每天 9:00 自动执行，保存结果到文件
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 输出目录
OUTPUT_DIR = "/Users/kelvin/.openclaw/workspace/quant-trading/results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_stock_list_fallback():
    """获取股票列表（带 fallback）"""
    # 预设股票池（常见活跃股）
    return [
        '000001', '000002', '000063', '000100', '000157',
        '000333', '000538', '000568', '000596', '000625',
        '000651', '000725', '000776', '000858', '000895',
        '002001', '002007', '002027', '002049', '002142',
        '002230', '002241', '002304', '002352', '002415',
        '002594', '002714', '300014', '300059', '300122',
        '300124', '300274', '300308', '300413', '300433',
        '300498', '300522', '300601', '300628', '300750',
        '600000', '600009', '600016', '600028', '600030',
        '600031', '600036', '600048', '600050', '600104',
        '600276', '600309', '600346', '600436', '600519',
        '600585', '600588', '600690', '600745', '600809',
        '600887', '600900', '600905', '601012', '601066',
        '601088', '601127', '601138', '601225', '601288',
        '601318', '601398', '601601', '601628', '601633',
        '601668', '601688', '601728', '601857', '601888',
        '601899', '601919', '601988', '601995', '603259',
    ]

def get_realtime_data(symbol):
    """获取个股实时行情（带重试和速率限制）"""
    import time
    for attempt in range(3):
        try:
            data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=(datetime.now() - timedelta(days=5)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq"
            )
            if data is not None and len(data) > 0:
                # 成功后短暂延迟，避免触发速率限制
                time.sleep(0.5)
                return data
        except Exception as e:
            error_msg = str(e)
            # 速率限制错误，延长等待时间
            if 'Rate limit' in error_msg or '频繁' in error_msg:
                wait_time = 5 * (attempt + 1)  # 5s, 10s, 15s
                print(f"⚠️  速率限制，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            elif attempt < 2:
                time.sleep(2)
            continue
    return None

def calculate_indicators(df):
    """计算技术指标"""
    if df is None or len(df) < 20:
        return None
    
    df = df.copy()
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA10'] = df['收盘'].rolling(window=10).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    df['VOL_MA5'] = df['成交量'].rolling(window=5).mean()
    
    # MACD
    exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp1 - exp2
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    
    return df

def check_conditions(df):
    """检查选股条件"""
    if df is None or len(df) < 10:
        return False, {}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else None
    
    conditions = {}
    
    # 1. 成交量放大（较 5 日均量放大 50% 以上）
    if 'VOL_MA5' in latest:
        vol_surge = latest['成交量'] > latest['VOL_MA5'] * 1.5
        conditions['成交量放大'] = vol_surge
    else:
        return False, {}
    
    # 2. 均线多头排列
    ma_alignment = latest['收盘'] > latest['MA5'] > latest['MA10']
    conditions['均线多头'] = ma_alignment
    
    # 3. MACD 金叉或红柱放大
    if prev is not None and 'MACD' in latest:
        macd_ok = (latest['MACD'] > 0) and (latest['MACD'] > prev['MACD'])
        conditions['MACD 向好'] = macd_ok
    else:
        conditions['MACD 向好'] = False
    
    # 4. 股价在 5 日线上方
    conditions['股价>MA5'] = latest['收盘'] > latest['MA5']
    
    # 综合判断
    passed = sum(conditions.values()) >= 3
    
    return passed, conditions

def analyze_stocks(stock_codes):
    """分析股票池"""
    import time
    results = []
    
    print(f"🔍 开始分析 {len(stock_codes)} 只股票...")
    
    for i, code in enumerate(stock_codes):
        if i % 10 == 0:
            print(f"📊 进度：{i+1}/{len(stock_codes)}")
        
        # 每只股票之间延迟，避免触发速率限制
        if i > 0 and i % 5 == 0:
            print(f"⏸️  短暂休息 2 秒...")
            time.sleep(2)
        
        # 获取数据
        df = get_realtime_data(code)
        if df is None:
            continue
        
        # 计算指标
        df = calculate_indicators(df)
        if df is None:
            continue
        
        # 检查条件
        passed, conditions = check_conditions(df)
        if not passed:
            continue
        
        # 获取基本信息
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        # 计算涨跌幅
        change_pct = ((latest['收盘'] - prev['收盘']) / prev['收盘'] * 100) if len(df) > 1 else 0
        
        results.append({
            '代码': code,
            '最新价': round(latest['收盘'], 2),
            '涨跌幅': round(change_pct, 2),
            '成交量': latest['成交量'],
            'MA5': round(latest['MA5'], 2),
            'MA10': round(latest['MA10'], 2),
            'MACD': round(latest['MACD'], 4) if 'MACD' in latest else 0,
            '符合条件数': sum(conditions.values()),
        })
    
    return results

def save_results(results):
    """保存结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # CSV 格式
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('符合条件数', ascending=False)
        
        csv_file = f"{OUTPUT_DIR}/stock_pick_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        # JSON 格式（含详细信息）
        json_file = f"{OUTPUT_DIR}/stock_pick_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'total_analyzed': len(results),
                'picks': results
            }, f, ensure_ascii=False, indent=2)
        
        # 生成文本报告
        txt_file = f"{OUTPUT_DIR}/stock_pick_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("📈 短线选股结果\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"✅ 符合条件的股票：{len(results)} 只\n\n")
            
            if results:
                f.write("📊 推荐关注（按符合条件数排序）：\n")
                f.write("-" * 60 + "\n")
                for i, stock in enumerate(results[:10], 1):
                    f.write(f"{i}. {stock['代码']} - {stock['最新价']}元 ")
                    f.write(f"({stock['涨跌幅']:+.2f}%) ")
                    f.write(f"[{stock['符合条件数']}/4 条件]\n")
                f.write("-" * 60 + "\n\n")
            
            f.write("💰 资金管理建议：\n")
            f.write("  总资金：10,000 元\n")
            f.write("  分散：2-3 只股票\n")
            f.write("  单只：3,000-5,000 元\n")
            f.write("  止损：-2% 到 -3%\n")
            f.write("  止盈：+3% 到 +5%\n\n")
            
            f.write("⚠️ 风险提示：\n")
            f.write("  数据仅供参考，不构成投资建议\n")
            f.write("  市场有风险，投资需谨慎\n")
        
        print(f"\n✅ 结果已保存：")
        print(f"   📄 CSV: {csv_file}")
        print(f"   📋 JSON: {json_file}")
        print(f"   📝 TXT: {txt_file}")
    else:
        print("\n😔 今日无符合条件的股票")
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 短线选股策略 - 自动运行")
    print(f"📅 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取股票池
    stock_codes = get_stock_list_fallback()
    print(f"📋 股票池：{len(stock_codes)} 只")
    
    # 分析股票
    results = analyze_stocks(stock_codes)
    
    # 保存结果
    saved_results = save_results(results)
    
    print("\n" + "=" * 60)
    print("✅ 执行完成")
    print("=" * 60)
    
    return saved_results

if __name__ == "__main__":
    main()
