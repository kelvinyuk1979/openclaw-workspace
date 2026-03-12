#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短线选股策略 - 日额度 1 万
作者：OpenClaw + AkShare
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def get_stock_list():
    """获取 A 股股票列表"""
    print("📋 获取股票列表...")
    
    # 尝试多个数据源
    try:
        # 方案 1：东方财富
        stock_list = ak.stock_zh_a_spot_em()
        return stock_list[['代码', '名称']]
    except Exception as e1:
        try:
            # 方案 2：同花顺
            stock_list = ak.stock_info_a_code_name()
            return stock_list
        except Exception as e2:
            # 方案 3：手动列出常见股票
            print("⚠️ 自动获取失败，使用预设股票池...")
            stock_codes = [
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
            return pd.DataFrame({'code': stock_codes, 'name': [''] * len(stock_codes)})

def get_realtime_data(symbol):
    """获取个股实时行情"""
    try:
        data = ak.stock_zh_a_spot_em(symbol=symbol)
        return data
    except Exception as e:
        return None

def get_historical_data(symbol, days=30):
    """获取历史 K 线数据"""
    try:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        return data
    except Exception as e:
        return None

def calculate_indicators(df):
    """计算技术指标"""
    if df is None or len(df) < 20:
        return None
    
    # 计算均线
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA10'] = df['收盘'].rolling(window=10).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    
    # 计算成交量均值
    df['VOL_MA5'] = df['成交量'].rolling(window=5).mean()
    
    # 计算 MACD
    exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp1 - exp2
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    
    return df

def check_volume_surge(df):
    """检查成交量是否放大（较 5 日均量放大 50% 以上）"""
    if len(df) < 6:
        return False
    
    latest_vol = df.iloc[-1]['成交量']
    avg_vol_5 = df.iloc[-2:-7:-1]['成交量'].mean()
    
    return latest_vol > avg_vol_5 * 1.5

def check_ma_alignment(df):
    """检查均线多头排列"""
    if len(df) < 20:
        return False
    
    latest = df.iloc[-1]
    return (latest['收盘'] > latest['MA5'] > latest['MA10'])

def check_macd_golden_cross(df):
    """检查 MACD 金叉或红柱放大"""
    if len(df) < 15:
        return False
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 金叉：DIF 上穿 DEA
    golden_cross = (prev['DIF'] <= prev['DEA']) and (latest['DIF'] > latest['DEA'])
    
    # 红柱放大
    red_bar_increase = (latest['MACD'] > 0) and (latest['MACD'] > prev['MACD'])
    
    return golden_cross or red_bar_increase

def get_fund_flow(symbol):
    """获取资金流向"""
    try:
        # 判断市场
        if symbol.startswith('6'):
            market = "sh"
        else:
            market = "sz"
        
        flow_data = ak.stock_individual_fund_flow(stock=symbol, market=market)
        
        if flow_data is not None and len(flow_data) > 0:
            # 获取主力净流入
            main_flow = flow_data.iloc[0]['主力净流入净额']
            return main_flow
        return 0
    except Exception as e:
        return 0

def screen_stocks(stock_codes, max_results=20):
    """筛选符合短线条件的股票"""
    results = []
    
    print(f"🔍 开始筛选 {len(stock_codes)} 只股票...")
    
    for i, code in enumerate(stock_codes):
        if i % 50 == 0:
            print(f"📊 进度：{i}/{len(stock_codes)}")
        
        # 获取历史数据
        df = get_historical_data(code, days=30)
        if df is None or len(df) < 20:
            continue
        
        # 计算指标
        df = calculate_indicators(df)
        if df is None:
            continue
        
        # 获取实时行情
        realtime = get_realtime_data(code)
        if realtime is None or len(realtime) == 0:
            continue
        
        latest_price = realtime.iloc[0]['最新价']
        volume = realtime.iloc[0]['成交量']
        amount = realtime.iloc[0]['成交额']
        
        # 排除条件：成交额 < 1 亿
        if amount < 100000000:
            continue
        
        # 条件 1：成交量放大
        if not check_volume_surge(df):
            continue
        
        # 条件 2：均线多头排列
        if not check_ma_alignment(df):
            continue
        
        # 条件 3：MACD 金叉或红柱放大
        if not check_macd_golden_cross(df):
            continue
        
        # 条件 4：资金净流入
        fund_flow = get_fund_flow(code)
        if fund_flow <= 0:
            continue
        
        # 符合条件，加入结果
        results.append({
            '代码': code,
            '名称': realtime.iloc[0]['名称'],
            '最新价': latest_price,
            '涨跌幅': realtime.iloc[0]['涨跌幅'],
            '成交量': volume,
            '成交额 (亿)': round(amount / 100000000, 2),
            '主力净流入 (万)': round(fund_flow / 10000, 2),
            'MA5': round(df.iloc[-1]['MA5'], 2),
            'MA10': round(df.iloc[-1]['MA10'], 2),
        })
        
        if len(results) >= max_results:
            break
    
    return pd.DataFrame(results)

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 短线选股策略 - 日额度 1 万")
    print("=" * 60)
    
    # 获取股票列表
    stock_list = get_stock_list()
    
    # 排除 ST 股和科创板（可选）
    stock_codes = [
        code for code in stock_list['code'] 
        if not code.startswith('ST') and not code.startswith('688')
    ]
    
    print(f"📋 待筛选股票数量：{len(stock_codes)}")
    
    # 筛选股票
    results = screen_stocks(stock_codes, max_results=20)
    
    # 显示结果
    print("\n" + "=" * 60)
    print("✅ 筛选结果")
    print("=" * 60)
    
    if len(results) > 0:
        print(results.to_string(index=False))
        
        # 保存结果
        output_file = f"short_term_pick_{datetime.now().strftime('%Y%m%d')}.csv"
        results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 结果已保存到：{output_file}")
        
        # 投资建议
        print("\n" + "=" * 60)
        print("📊 投资建议")
        print("=" * 60)
        print("💰 总资金：10,000 元")
        print("📌 建议分散：2-3 只股票")
        print("💵 单只仓位：3,000-5,000 元")
        print("🛑 止损：-2% 到 -3%")
        print("✅ 止盈：+3% 到 +5%")
        print("⚠️  投资有风险，决策需谨慎！")
    else:
        print("😔 今日无符合条件的股票")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
