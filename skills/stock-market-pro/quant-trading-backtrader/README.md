# 🔙 量化策略回测系统 (Backtrader)

专业的量化策略回测框架 - 策略开发 + 历史回测 + 参数优化

## 快速开始

### 1. 安装依赖

```bash
pip install backtrader matplotlib pandas numpy
```

### 2. 创建策略

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    params = (('period', 15),)

    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close, period=self.params.period)

    def next(self):
        if self.sma > self.data.close:
            self.buy()
        else:
            self.sell()
```

### 3. 运行回测

```python
cerebro = bt.Cerebro()
cerebro.addstrategy(MyStrategy)
# 添加数据...
cerebro.run()
cerebro.plot()
```

## 核心功能

| 功能 | 说明 |
|------|------|
| 📊 **回测引擎** | 历史数据模拟交易 |
| 🧠 **策略开发** | 结构化 Strategy 类 |
| 📈 **技术指标** | SMA/EMA/RSI/MACD 等 |
| 🛡️ **风险管理** | 止损止盈、仓位管理 |
| 📉 **参数优化** | 自动寻找最优参数 |
| 📋 **性能报告** | 夏普比率、最大回撤、胜率 |

## 内置策略示例

### SMA 交叉策略

- 快线（10 日）上穿慢线（30 日）→ 买入
- 快线下穿慢线 → 卖出

### RSI 超买超卖

- RSI < 30（超卖）→ 买入
- RSI > 70（超买）→ 卖出

### 布林带策略

- 价格触及下轨 → 买入
- 价格触及上轨 → 卖出

## 性能指标

| 指标 | 目标值 |
|------|--------|
| 年化回报 | >20% |
| 夏普比率 | >1.0 |
| 最大回撤 | <20% |
| 胜率 | >45% |
| 盈亏比 | >1.5 |

## 最佳实践

### ✅ 必做

- 设置止损（5-8%）
- 样本外验证
- 考虑手续费
- 多市场环境测试

### ❌ 避免

- 未来函数
- 过度优化
- 幸存者偏差
- 忽略流动性

## 支持市场

- 🇺🇸 美股
- 🇨🇳 A 股（需数据源）
- 🪙 加密货币
- 💱 外汇
- 📦 期货

## 风险提示

⚠️ **回测不代表实盘表现**

- 历史数据不代表未来
- 实盘有滑点和心理因素
- 先用模拟盘验证

## 相关资源

- **官方文档:** https://www.backtrader.com/docu/
- **GitHub:** https://github.com/mementum/backtrader
- **ClawHub:** https://clawhub.ai/gmsx000-cloud/quant-trading-backtrader

---

**版本：** 1.0.0  
**作者：** gmsx000-cloud  
**移植日期：** 2026-03-14
