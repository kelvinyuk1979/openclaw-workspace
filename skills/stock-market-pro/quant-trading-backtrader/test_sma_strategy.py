#!/usr/bin/env python3
"""
量化策略回测测试 - SMA 交叉策略

策略逻辑：
- 快线（10 日 SMA）上穿慢线（30 日 SMA）→ 买入
- 快线下穿慢线 → 卖出

测试标的：AAPL（苹果公司）
测试时间：2020-01-01 到 2023-12-31
初始资金：$10,000
"""

import backtrader as bt
import datetime
import yfinance as yf


class SmaCrossoverStrategy(bt.Strategy):
    """SMA 交叉策略"""
    
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )
    
    def __init__(self):
        # 定义指标
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        
        # 打印策略信息
        print(f"\n📊 策略初始化完成")
        print(f"快线 SMA: {self.params.fast_period}日")
        print(f"慢线 SMA: {self.params.slow_period}日")
        print(f"止损：{self.params.stop_loss*100}%")
        print(f"止盈：{self.params.take_profit*100}%")
    
    def next(self):
        # 没有持仓时
        if not self.position:
            if self.crossover > 0:  # 快线上穿慢线（金叉）
                # 计算买入数量（使用 95% 资金，留 5% 缓冲）
                size = int(self.broker.getcash() * 0.95 / self.data.close[0])
                if size > 0:
                    self.buy(size=size)
                    print(f"\n✅ 买入 @ ${self.data.close[0]:.2f} - 数量：{size}股")
                    
                    # 设置止损止盈单
                    stop_price = self.data.close[0] * (1 - self.params.stop_loss)
                    limit_price = self.data.close[0] * (1 + self.params.take_profit)
                    
                    self.sell(exectype=bt.Order.Stop, price=stop_price)
                    self.sell(exectype=bt.Order.Limit, price=limit_price)
                    
        # 有持仓时
        else:
            if self.crossover < 0:  # 快线下穿慢线（死叉）
                self.close()
                print(f"\n❌ 卖出 @ ${self.data.close[0]:.2f} - 平仓")
    
    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Completed]:
            if order.isbuy():
                pass  # 买入已在 next() 中打印
            else:
                # 检查是止损还是止盈
                if order.exec.price < self.data.close[0]:
                    print(f"  🛑 止损触发 @ ${order.exec.price:.2f}")
                else:
                    print(f"  🎯 止盈触发 @ ${order.exec.price:.2f}")
    
    def notify_trade(self, trade):
        """交易通知"""
        if trade.isclosed:
            pnl = trade.pnl
            pnl_pct = (trade.pnl / trade.size) / trade.price * 100
            print(f"  💰 交易完成 - 盈亏：${pnl:.2f} ({pnl_pct:.2f}%)")


def run_backtest():
    """运行回测"""
    
    print("=" * 60)
    print("🔙 量化策略回测系统 - SMA 交叉策略测试")
    print("=" * 60)
    
    # 创建回测引擎
    cerebro = bt.Cerebro()
    
    # 添加策略
    cerebro.addstrategy(
        SmaCrossoverStrategy,
        fast_period=10,
        slow_period=30,
        stop_loss=0.05,
        take_profit=0.10
    )
    
    # 下载数据（使用 yfinance）
    print("\n📥 下载 AAPL 历史数据...")
    print("测试期间：2020-01-01 到 2023-12-31")
    
    data = yf.download('AAPL', start='2020-01-01', end='2023-12-31', progress=False)
    
    if data.empty:
        print("❌ 数据下载失败！")
        return
    
    print(f"✅ 数据下载完成 - {len(data)} 个交易日")
    
    # 转换数据格式
    data_bt = bt.feeds.PandasData(
        dataname=data,
        datetime='Date',
        open='Open',
        high='High',
        low='Low',
        close='Close',
        volume='Volume',
        openinterest=-1
    )
    
    # 添加数据
    cerebro.adddata(data_bt)
    
    # 设置资金
    initial_cash = 10000.0
    cerebro.broker.setcash(initial_cash)
    
    # 设置手续费（0.1%）
    cerebro.broker.setcommission(commission=0.001)
    
    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.02)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 打印初始信息
    print(f"\n💰 初始资金：${initial_cash:,.2f}")
    print("-" * 60)
    
    # 运行回测
    results = cerebro.run()
    
    # 获取最终资金
    final_value = cerebro.broker.getvalue()
    total_return = ((final_value - initial_cash) / initial_cash) * 100
    
    # 打印结果
    print("\n" + "=" * 60)
    print("📊 回测结果")
    print("=" * 60)
    
    print(f"\n💰 资金情况:")
    print(f"  初始资金：${initial_cash:,.2f}")
    print(f"  最终资金：${final_value:,.2f}")
    print(f"  总收益：${final_value - initial_cash:,.2f} ({total_return:.2f}%)")
    
    # 获取分析结果
    strat = results[0]
    
    print(f"\n📈 性能指标:")
    
    # 夏普比率
    sharpe = strat.analyzers.sharpe.get_analysis()
    if sharpe.get('sharperatio'):
        print(f"  夏普比率：{sharpe['sharperatio']:.2f}")
    
    # 最大回撤
    dd = strat.analyzers.drawdown.get_analysis()
    print(f"  最大回撤：{dd['max']['drawdown']:.2f}%")
    print(f"  最大回撤金额：${dd['max']['moneydown']:.2f}")
    
    # 收益率
    returns = strat.analyzers.returns.get_analysis()
    if returns.get('averagereturn'):
        avg_return = returns['averagereturn'] * 100
        print(f"  平均收益率：{avg_return:.2f}%")
    
    # 交易统计
    trades = strat.analyzers.trades.get_analysis()
    total_trades = trades['total']['total']
    print(f"\n📊 交易统计:")
    print(f"  总交易数：{total_trades}")
    
    if total_trades > 0:
        won_trades = trades['won']['total']
        lost_trades = trades['lost']['total']
        win_rate = (won_trades / total_trades) * 100
        
        print(f"  盈利交易：{won_trades}")
        print(f"  亏损交易：{lost_trades}")
        print(f"  胜率：{win_rate:.1f}%")
        
        # 盈亏比
        if lost_trades > 0:
            avg_win = trades['won']['pnl']['average']
            avg_loss = abs(trades['lost']['pnl']['average'])
            profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
            print(f"  盈亏比：{profit_factor:.2f}")
    
    # 年化收益率
    years = (data.index[-1] - data.index[0]).days / 365.25
    if years > 0:
        annual_return = ((final_value / initial_cash) ** (1/years) - 1) * 100
        print(f"\n📅 年化收益率：{annual_return:.2f}%")
        print(f"📅 测试时长：{years:.2f}年")
    
    print("\n" + "=" * 60)
    
    # 评估
    print("\n🎯 策略评估:")
    
    if annual_return > 20:
        print("  ✅ 年化收益 > 20% - 优秀")
    elif annual_return > 10:
        print("  ⚠️  年化收益 10-20% - 良好")
    else:
        print("  ❌ 年化收益 < 10% - 需优化")
    
    if dd['max']['drawdown'] < 20:
        print("  ✅ 最大回撤 < 20% - 风险控制良好")
    else:
        print("  ⚠️  最大回撤 > 20% - 风险较高")
    
    if sharpe.get('sharperatio') and sharpe['sharperatio'] > 1.0:
        print("  ✅ 夏普比率 > 1.0 - 风险调整收益好")
    else:
        print("  ⚠️  夏普比率 < 1.0 - 需改进")
    
    print("\n" + "=" * 60)
    print("✅ 回测完成！")
    print("=" * 60)
    
    # 可选：绘制图表
    # cerebro.plot()


if __name__ == '__main__':
    run_backtest()
