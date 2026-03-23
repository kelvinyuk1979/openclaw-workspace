---
name: quant-trading-backtrader
description: 基于 Backtrader 框架的量化策略回测系统，提供策略开发、历史回测、参数优化、风险管理功能
author: gmsx000-cloud (ported by OpenClaw)
version: 1.0.0
emoji: 🔙
tags: [quantitative, backtesting, strategy-development, backtrader, python]
---

# 🔙 量化策略回测系统

基于 Python Backtrader 框架的专业量化策略回测系统，提供策略开发、历史回测、参数优化、风险管理等完整功能。

## 核心功能

### 1. 回测引擎

- 基于历史数据模拟交易策略
- 支持多个数据源（股票、加密货币、期货、外汇）
- 支持不同时间框架（分钟、小时、日、周、月）
- 考虑手续费、滑点等实际交易成本

### 2. 策略开发

**结构化 Strategy 类：**
```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (
        ('period', 15),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )

    def __init__(self):
        # 定义指标
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)
        self.rsi = bt.indicators.RSI(self.data.close, period=14)

    def next(self):
        # 交易逻辑
        if not self.position:
            if self.rsi < 30:  # 超卖
                self.buy()
        else:
            if self.rsi > 70:  # 超买
                self.sell()
```

### 3. 风险管理

- **止损止盈** - 固定百分比或基于指标
- **仓位管理** - 固定金额、百分比、Kelly 公式
- **最大回撤控制** - 自动停止交易
- **分散投资** - 多标的组合

### 4. 数据处理

- CSV 数据导入（自定义格式）
- Pandas DataFrame 集成
- 实时数据接入（可选）
- 数据清洗和预处理

### 5. 报告分析

- 交易记录日志
- 盈亏分析（PNL）
- 组合价值曲线
- 性能指标（夏普比率、最大回撤、胜率等）

## 内置指标库

| 指标类型 | 指标 | 说明 |
|---------|------|------|
| **趋势** | SMA, EMA, MACD | 移动平均、指数平均、趋势动量 |
| **动量** | RSI, Stochastic | 相对强弱、随机指标 |
| **波动率** | Bollinger Bands, ATR | 布林带、平均真实波幅 |
| **成交量** | Volume, OBV | 成交量、能量潮 |

## 使用示例

### 示例 1：SMA 交叉策略

```python
import backtrader as bt
import datetime

class SmaCrossover(bt.Strategy):
    params = (
        ('fast', 10),
        ('slow', 30),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.params.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.params.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:  # 快线上穿慢线
                self.buy()
        elif self.crossover < 0:  # 快线下穿慢线
            self.sell()

# 创建回测引擎
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCrossover, fast=10, slow=30)

# 添加数据
data = bt.feeds.YahooFinanceData(
    dataname='AAPL',
    fromdate=datetime.datetime(2020, 1, 1),
    todate=datetime.datetime(2023, 12, 31)
)
cerebro.adddata(data)

# 设置资金
cerebro.broker.setcash(10000.0)
cerebro.broker.setcommission(commission=0.001)  # 0.1% 手续费

# 运行回测
print(f'初始资金：${cerebro.broker.getvalue():.2f}')
cerebro.run()
print(f'最终资金：${cerebro.broker.getvalue():.2f}')

# 绘制图表
cerebro.plot()
```

### 示例 2：RSI 超买超卖策略

```python
class RsiStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('oversold', 30),
        ('overbought', 70),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.params.oversold:
                self.buy()
                # 设置止损止盈
                self.sell(exectype=bt.Order.Stop,
                         price=self.data.close * (1 - self.params.stop_loss))
                self.sell(exectype=bt.Order.Limit,
                         price=self.data.close * (1 + self.params.take_profit))
        else:
            if self.rsi > self.params.overbought:
                self.close()

# 运行回测
cerebro = bt.Cerebro()
cerebro.addstrategy(RsiStrategy, rsi_period=14, oversold=30, overbought=70)
# ... 添加数据 ...
cerebro.run()
```

### 示例 3：参数优化

```python
# 优化策略参数
cerebro = bt.Cerebro(optreturn=False)
cerebro.addstrategy(SmaCrossover)

# 添加优化参数范围
cerebro.optstrategy(
    SmaCrossover,
    fast=range(5, 20, 5),    # 5, 10, 15
    slow=range(20, 60, 10)   # 20, 30, 40, 50
)

# 运行优化
results = cerebro.run()

# 分析最优参数
best_return = 0
best_params = None
for result in results:
    if cerebro.broker.getvalue() > best_return:
        best_return = cerebro.broker.getvalue()
        best_params = result[0].params

print(f'最优参数：fast={best_params.fast}, slow={best_params.slow}')
print(f'最终资金：${best_return:.2f}')
```

### 示例 4：多标的组合回测

```python
cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCrossover)

# 添加多个股票
stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
for stock in stocks:
    data = bt.feeds.YahooFinanceData(dataname=stock,
                                     fromdate=datetime.datetime(2020, 1, 1),
                                     todate=datetime.datetime(2023, 12, 31))
    cerebro.adddata(data)

# 设置仓位管理
cerebro.addsizer(bt.sizers.PercentSizer, percents=20)  # 每个标的 20%

cerebro.run()
```

## 性能指标

### 关键指标

| 指标 | 公式 | 目标值 |
|------|------|--------|
| **总回报** | (最终资金 - 初始资金) / 初始资金 | >20% 年化 |
| **年化回报** | 几何平均 | >20% |
| **夏普比率** | (回报 - 无风险利率) / 标准差 | >1.0 |
| **最大回撤** | 最大连续亏损 | <20% |
| **胜率** | 盈利交易数 / 总交易数 | >45% |
| **盈亏比** | 平均盈利 / 平均亏损 | >1.5 |
| **索提诺比率** | 下行风险调整回报 | >1.5 |

### 性能分析报告

```python
# 添加分析器
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

# 运行回测
results = cerebro.run()

# 打印分析结果
print(f'夏普比率：{results[0].analyzers.sharpe.get_analysis()["sharperatio"]:.2f}')
print(f'最大回撤：{results[0].analyzers.drawdown.get_analysis()["max"]["drawdown"]:.2f}%')
print(f'总交易数：{results[0].analyzers.trades.get_analysis()["total"]["total"]}')
print(f'胜率：{results[0].analyzers.trades.get_analysis()["won"]["total"] / results[0].analyzers.trades.get_analysis()["total"]["total"] * 100:.1f}%')
```

## 最佳实践

### 1. 避免过拟合

- **前向分析** - 用过去数据训练，未来数据测试
- **参数稳健性** - 参数在多个市场有效
- **样本外测试** - 保留部分数据用于验证

### 2. 风险控制

- **必设止损** - 每笔交易都要有止损
- **仓位管理** - 单笔不超过总资金的 5-10%
- **分散投资** - 多标的、多策略分散
- **最大回撤限制** - 达到阈值停止交易

### 3. 数据质量

- **数据清洗** - 处理缺失值、异常值
- **复权处理** - 考虑分红、拆股
- **足够长度** - 至少 3-5 年历史数据
- **代表性** - 包含不同市场环境（牛熊震荡）

### 4. 回测陷阱

| 陷阱 | 说明 | 避免方法 |
|------|------|---------|
| 未来函数 | 使用未来数据 | 检查指标计算 |
| 幸存者偏差 | 只用现存股票 | 包含已退市股票 |
| 过度优化 | 参数过度拟合 | 样本外验证 |
| 忽略成本 | 不考虑手续费 | 设置合理佣金 |
| 流动性假设 | 假设都能成交 | 考虑成交量限制 |

## 安装配置

### 1. 安装依赖

```bash
pip install backtrader matplotlib pandas numpy
```

### 2. 基础模板

```python
# strategy_template.py
import backtrader as bt
import datetime

class MyStrategy(bt.Strategy):
    params = (
        ('param1', 15),
        ('param2', 0.05),
    )

    def __init__(self):
        # 初始化指标
        pass

    def next(self):
        # 交易逻辑
        pass

    def notify_order(self, order):
        # 订单通知
        pass

    def notify_trade(self, trade):
        # 交易通知
        pass

# 运行回测
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy)
    # ... 添加数据、设置资金 ...
    cerebro.run()
    cerebro.plot()
```

## 扩展功能

### 1. 实时交易

- 连接交易所 API
- 实时数据接入
- 自动下单执行
- 仓位监控

### 2. 机器学习集成

- 用 ML 预测价格方向
- 特征工程
- 模型训练和验证
- 信号生成

### 3. 多策略组合

- 同时运行多个策略
- 策略权重分配
- 风险平价
- 动态再平衡

## 风险提示

⚠️ **回测不代表实盘表现**

- 历史数据不代表未来
- 回测忽略滑点和冲击成本
- 实盘心理因素影响执行
- 先用模拟盘验证

## 相关资源

- **Backtrader 文档:** https://www.backtrader.com/docu/
- **GitHub:** https://github.com/mementum/backtrader
- **ClawHub:** https://clawhub.ai/gmsx000-cloud/quant-trading-backtrader
- **社区论坛:** https://community.backtrader.com/

---

**版本：** 1.0.0  
**原始作者：** gmsx000-cloud  
**移植：** OpenClaw Workspace  
**日期：** 2026-03-14
