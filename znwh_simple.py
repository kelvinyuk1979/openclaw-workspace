#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中南文化 (002445.SZ) 股票分析 - 简化版
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

print("=" * 80)
print("中南文化 (002445.SZ) 股票分析")
print(f"分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# 1. 实时行情
print("\n【1. 实时行情】")
try:
    spot = ak.stock_zh_a_spot_em()
    znwh = spot[spot['代码'] == '002445']
    if not znwh.empty:
        row = znwh.iloc[0]
        print(f"股票代码：{row.get('代码', 'N/A')}")
        print(f"股票名称：{row.get('名称', 'N/A')}")
        print(f"最新价：{row.get('最新价', 'N/A')}")
        print(f"涨跌幅：{row.get('涨跌幅', 'N/A')}%")
        print(f"涨跌额：{row.get('涨跌额', 'N/A')}")
        print(f"成交量：{row.get('成交量', 'N/A')}")
        print(f"成交额：{row.get('成交额', 'N/A')}")
        print(f"振幅：{row.get('振幅', 'N/A')}%")
        print(f"最高：{row.get('最高', 'N/A')}")
        print(f"最低：{row.get('最低', 'N/A')}")
        print(f"今开：{row.get('今开', 'N/A')}")
        print(f"昨收：{row.get('昨收', 'N/A')}")
        print(f"市盈率 (动态): {row.get('市盈率 (动态)', 'N/A')}")
        print(f"市净率：{row.get('市净率', 'N/A')}")
        print(f"总市值：{row.get('总市值', 'N/A')}")
        print(f"流通市值：{row.get('流通市值', 'N/A')}")
except Exception as e:
    print(f"获取实时行情失败：{e}")

# 2. 历史 K 线
print("\n【2. 日 K 线数据 (最近 60 日)】")
try:
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
    
    daily = ak.stock_zh_a_hist(symbol="002445", period="daily", 
                               start_date=start_date, end_date=end_date, adjust="qfq")
    if len(daily) > 0:
        print(f"数据条数：{len(daily)}")
        print("\n最近 10 个交易日：")
        print(daily[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']].tail(10).to_string())
        
        # 保存到 CSV
        daily.to_csv('/Users/kelvin/.openclaw/workspace/znwh_daily.csv', index=False)
        print("\n数据已保存到：znwh_daily.csv")
        
        # 计算简单统计
        df = daily.copy()
        df['收盘'] = pd.to_numeric(df['收盘'], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        
        print(f"\n90 日最高价：{df['最高'].max()}")
        print(f"90 日最低价：{df['最低'].min()}")
        print(f"平均成交量：{df['成交量'].mean():,.0f}")
        
except Exception as e:
    print(f"获取日 K 失败：{e}")

# 3. 周 K 线
print("\n【3. 周 K 线数据】")
try:
    weekly = ak.stock_zh_a_hist(symbol="002445", period="weekly", adjust="qfq")
    if len(weekly) > 0:
        print(f"数据条数：{len(weekly)}")
        print("\n最近 10 周：")
        print(weekly[['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']].tail(10).to_string())
        weekly.to_csv('/Users/kelvin/.openclaw/workspace/znwh_weekly.csv', index=False)
except Exception as e:
    print(f"获取周 K 失败：{e}")

# 4. 财务指标
print("\n【4. 财务指标】")
try:
    indicator = ak.stock_financial_analysis_indicator(symbol="002445")
    print(indicator.to_string())
except Exception as e:
    print(f"获取财务指标失败：{e}")

# 5. 资金流向
print("\n【5. 资金流向】")
try:
    fund = ak.stock_individual_fund_flow(stock="002445", market="sz")
    print(fund.to_string())
except Exception as e:
    print(f"获取资金流向失败：{e}")

print("\n" + "=" * 80)
print("数据采集完成")
print("=" * 80)
