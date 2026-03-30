#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中南文化 (002445.SZ) 股票分析脚本
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("中南文化 (002445.SZ) 股票分析报告")
print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ============================================================================
# 1. 获取基本信息
# ============================================================================
print("\n" + "=" * 80)
print("1. 公司基本信息")
print("=" * 80)

try:
    # 获取个股信息
    stock_info = ak.stock_individual_info_em(symbol="002445")
    print("\n公司信息：")
    print(stock_info)
except Exception as e:
    print(f"获取公司信息失败：{e}")

# ============================================================================
# 2. 获取实时行情
# ============================================================================
print("\n" + "=" * 80)
print("2. 实时行情")
print("=" * 80)

try:
    # A 股实时行情
    spot_data = ak.stock_zh_a_spot_em()
    znwh_data = spot_data[spot_data['代码'] == '002445']
    if not znwh_data.empty:
        print("\n实时行情数据：")
        for col in znwh_data.columns:
            print(f"{col}: {znwh_data[col].values[0]}")
except Exception as e:
    print(f"获取实时行情失败：{e}")

# ============================================================================
# 3. 获取历史 K 线数据（日 K、周 K）
# ============================================================================
print("\n" + "=" * 80)
print("3. 历史 K 线数据")
print("=" * 80)

try:
    # 日 K 线 - 最近 1 年
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    daily_k = ak.stock_zh_a_hist(symbol="002445", period="daily", 
                                  start_date=start_date, end_date=end_date, adjust="qfq")
    print(f"\n日 K 数据：{len(daily_k)} 条记录")
    print("\n最近 10 个交易日：")
    print(daily_k.tail(10)[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']])
    
    # 周 K 线
    weekly_k = ak.stock_zh_a_hist(symbol="002445", period="weekly", adjust="qfq")
    print(f"\n周 K 数据：{len(weekly_k)} 条记录")
    print("\n最近 10 周：")
    print(weekly_k.tail(10)[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']])
    
    # 保存到 CSV
    daily_k.to_csv('/Users/kelvin/.openclaw/workspace/znwh_daily_k.csv', index=False)
    weekly_k.to_csv('/Users/kelvin/.openclaw/workspace/znwh_weekly_k.csv', index=False)
    print("\nK 线数据已保存到：znwh_daily_k.csv, znwh_weekly_k.csv")
    
except Exception as e:
    print(f"获取 K 线数据失败：{e}")
    daily_k = None
    weekly_k = None

# ============================================================================
# 4. 技术指标分析
# ============================================================================
print("\n" + "=" * 80)
print("4. 技术指标分析")
print("=" * 80)

if daily_k is not None and len(daily_k) > 0:
    try:
        df = daily_k.copy()
        df['收盘'] = pd.to_numeric(df['收盘'], errors='coerce')
        df['最高'] = pd.to_numeric(df['最高'], errors='coerce')
        df['最低'] = pd.to_numeric(df['最低'], errors='coerce')
        df['开盘'] = pd.to_numeric(df['开盘'], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        # 计算均线
        df['MA5'] = df['收盘'].rolling(5).mean()
        df['MA10'] = df['收盘'].rolling(10).mean()
        df['MA20'] = df['收盘'].rolling(20).mean()
        df['MA60'] = df['收盘'].rolling(60).mean()
        df['MA120'] = df['收盘'].rolling(120).mean()
        df['MA250'] = df['收盘'].rolling(250).mean()
        
        # 计算 RSI
        def calculate_rsi(data, period=14):
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        df['RSI14'] = calculate_rsi(df['收盘'], 14)
        
        # 计算 MACD
        exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
        exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # 计算布林带
        df['BB_Middle'] = df['收盘'].rolling(20).mean()
        df['BB_Std'] = df['收盘'].rolling(20).std()
        df['BB_Upper'] = df['BB_Middle'] + 2 * df['BB_Std']
        df['BB_Lower'] = df['BB_Middle'] - 2 * df['BB_Std']
        
        # 获取最新数据
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        print("\n【均线系统】")
        print(f"当前价格：{latest['收盘']:.2f}")
        print(f"MA5:  {latest['MA5']:.2f}  {'价格在上' if latest['收盘'] > latest['MA5'] else '价格在下'}")
        print(f"MA10: {latest['MA10']:.2f}  {'价格在上' if latest['收盘'] > latest['MA10'] else '价格在下'}")
        print(f"MA20: {latest['MA20']:.2f}  {'价格在上' if latest['收盘'] > latest['MA20'] else '价格在下'}")
        print(f"MA60: {latest['MA60']:.2f}  {'价格在上' if latest['收盘'] > latest['MA60'] else '价格在下'}")
        print(f"MA120: {latest['MA120']:.2f}  {'价格在上' if latest['收盘'] > latest['MA120'] else '价格在下'}")
        print(f"MA250: {latest['MA250']:.2f}  {'价格在上' if latest['收盘'] > latest['MA250'] else '价格在下'}")
        
        # 均线排列分析
        ma_trend = "多头排列" if (latest['MA5'] > latest['MA10'] > latest['MA20']) else \
                   "空头排列" if (latest['MA5'] < latest['MA10'] < latest['MA20']) else "混乱"
        print(f"均线排列：{ma_trend}")
        
        print("\n【RSI 指标】")
        print(f"RSI(14): {latest['RSI14']:.2f}")
        if latest['RSI14'] > 70:
            print("状态：超买区，警惕回调风险")
        elif latest['RSI14'] < 30:
            print("状态：超卖区，可能存在反弹机会")
        else:
            print("状态：中性区域")
        
        print("\n【MACD 指标】")
        print(f"MACD: {latest['MACD']:.4f}")
        print(f"Signal: {latest['Signal']:.4f}")
        print(f"MACD 柱状图：{latest['MACD_Hist']:.4f}")
        if latest['MACD'] > latest['Signal']:
            print("状态：金叉，偏多信号")
        else:
            print("状态：死叉，偏空信号")
        
        print("\n【布林带】")
        print(f"上轨：{latest['BB_Upper']:.2f}")
        print(f"中轨：{latest['BB_Middle']:.2f}")
        print(f"下轨：{latest['BB_Lower']:.2f}")
        print(f"当前价格位置：{(latest['收盘'] - latest['BB_Lower']) / (latest['BB_Upper'] - latest['BB_Lower']) * 100:.1f}%")
        
        print("\n【支撑位/阻力位】")
        # 近期高点/低点
        recent_high = df['最高'].tail(20).max()
        recent_low = df['最低'].tail(20).min()
        print(f"近期阻力位（20 日高点）: {recent_high:.2f}")
        print(f"近期支撑位（20 日低点）: {recent_low:.2f}")
        
        # 60 日高点/低点
        high_60 = df['最高'].tail(60).max()
        low_60 = df['最低'].tail(60).min()
        print(f"中期阻力位（60 日高点）: {high_60:.2f}")
        print(f"中期支撑位（60 日低点）: {low_60:.2f}")
        
        print("\n【成交量分析】")
        avg_vol_5 = df['成交量'].tail(5).mean()
        avg_vol_20 = df['成交量'].tail(20).mean()
        latest_vol = df['成交量'].iloc[-1]
        print(f"当日成交量：{latest_vol:,.0f}")
        print(f"5 日均量：{avg_vol_5:,.0f}")
        print(f"20 日均量：{avg_vol_20:,.0f}")
        vol_ratio = latest_vol / avg_vol_20 if avg_vol_20 > 0 else 0
        print(f"量比（当日/20 日均）: {vol_ratio:.2f}")
        if vol_ratio > 2:
            print("状态：放量明显")
        elif vol_ratio < 0.5:
            print("状态：缩量明显")
        else:
            print("状态：正常")
        
    except Exception as e:
        print(f"技术分析计算失败：{e}")

# ============================================================================
# 5. 基本面分析
# ============================================================================
print("\n" + "=" * 80)
print("5. 基本面分析")
print("=" * 80)

try:
    # 获取财务指标
    financial_indicator = ak.stock_financial_analysis_indicator(symbol="002445")
    print("\n主要财务指标：")
    print(financial_indicator)
except Exception as e:
    print(f"获取财务指标失败：{e}")
    financial_indicator = None

try:
    # 获取财务报表摘要
    financial_abstract = ak.stock_financial_abstract_ths(symbol="002445")
    print("\n财务报表摘要：")
    print(financial_abstract)
except Exception as e:
    print(f"获取财务报表失败：{e}")

try:
    # 获取估值指标
    stock_value_em = ak.stock_value_em(symbol="002445")
    print("\n估值指标：")
    print(stock_value_em)
except Exception as e:
    print(f"获取估值指标失败：{e}")

# ============================================================================
# 6. 资金流向
# ============================================================================
print("\n" + "=" * 80)
print("6. 资金流向")
print("=" * 80)

try:
    fund_flow = ak.stock_individual_fund_flow(stock="002445", market="sz")
    print("\n资金流向：")
    print(fund_flow)
except Exception as e:
    print(f"获取资金流向失败：{e}")

# ============================================================================
# 7. 行业对比
# ============================================================================
print("\n" + "=" * 80)
print("7. 行业板块对比")
print("=" * 80)

try:
    # 获取行业板块
    industry_list = ak.stock_board_industry_name_em()
    print("\n行业板块列表（前 20）：")
    print(industry_list.head(20))
    
    # 中南文化所属行业（传媒/文化）
    # 获取传媒行业成分股
    try:
        media_stocks = ak.stock_board_industry_cons_em(symbol="传媒")
        print("\n传媒行业成分股（前 20）：")
        print(media_stocks.head(20))
    except:
        print("无法获取传媒行业成分股")
        
except Exception as e:
    print(f"获取行业数据失败：{e}")

# ============================================================================
# 8. 龙虎榜数据
# ============================================================================
print("\n" + "=" * 80)
print("8. 龙虎榜数据")
print("=" * 80)

try:
    # 获取最近龙虎榜
    today = datetime.now().strftime('%Y%m%d')
    for i in range(10):
        check_date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        try:
            lhb = ak.stock_lhb_detail_em(date=check_date)
            if not lhb.empty:
                znwh_lhb = lhb[lhb.apply(lambda x: '002445' in str(x), axis=any)]
                if not znwh_lhb.empty:
                    print(f"\n{check_date} 龙虎榜数据：")
                    print(znwh_lhb)
                    break
        except:
            continue
    else:
        print("最近 10 日无龙虎榜记录")
except Exception as e:
    print(f"获取龙虎榜失败：{e}")

print("\n" + "=" * 80)
print("数据采集完成！")
print("=" * 80)
