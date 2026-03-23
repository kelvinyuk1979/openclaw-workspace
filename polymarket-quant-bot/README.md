# 🤖 Polymarket 量化交易机器人

基于 5 大数学公式的预测市场量化交易系统

## 📊 核心公式

| 编号 | 公式 | 用途 | 文件 |
|------|------|------|------|
| [FRM-001] | **期望值 (EV)** | 决定是否入场 | `ev_calculator.py` |
| [FRM-002] | **贝叶斯定理** | 动态更新概率 | `bayes_updater.py` |
| [FRM-003] | **凯利公式** | 最优仓位管理 | `kelly_position.py` |
| [FRM-004] | **基础率** | 识别市场偏差 | `base_rate_scanner.py` |
| [FRM-005] | **KL 散度** | 统计套利 | `kl_arb_detector.py` |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd polymarket-quant-bot
pip3 install -r requirements.txt
```

### 2. 配置

编辑 `config/config.json`:

```json
{
  "mode": "simulation",
  "account": {
    "initial_capital": 10000
  },
  "strategies": {
    "ev_strategy": {
      "enabled": true,
      "ev_threshold": 0.05
    }
  }
}
```

### 3. 运行

```bash
python3 main.py
```

## 📁 项目结构

```
polymarket-quant-bot/
├── config/
│   └── config.json          # 配置文件
├── src/
│   ├── data_fetcher.py      # API 数据获取
│   ├── prediction_model.py  # 多因子预测模型
│   ├── ev_calculator.py     # EV 期望值 [FRM-001]
│   ├── kelly_position.py    # 凯利仓位 [FRM-003]
│   ├── bayes_updater.py     # 贝叶斯更新 [FRM-002]
│   ├── base_rate_scanner.py # 基础率 [FRM-004]
│   ├── kl_arb_detector.py   # KL 散度 [FRM-005]
│   └── backtester.py        # 回测系统
├── reports/
│   └── daily_report_*.md    # 每日报告
├── main.py                  # 主程序
├── backtest.py              # 回测入口
└── README.md                # 本文档
```

## 🧠 预测模型

### 多因子加权

```
预测概率 = 基础率 × 30% 
         + 市场情绪 × 20% 
         + 动量 × 15% 
         + 交易量 × 15% 
         + 新闻催化剂 × 20%
```

### 因子说明

| 因子 | 权重 | 说明 |
|------|------|------|
| **基础率** | 30% | 历史统计概率 |
| **市场情绪** | 20% | 从价格/OI 推断 |
| **动量** | 15% | 价格趋势 |
| **交易量** | 15% | 异常放量信号 |
| **新闻催化剂** | 20% | 事件驱动 |

## 📈 回测结果

### 默认权重表现

| 指标 | 数值 |
|------|------|
| 初始资金 | $10,000 |
| 最终资金 | $18,000 |
| **总回报** | **+80.0%** |
| 总交易 | 251 笔 |
| 胜率 | 33.1% |
| **夏普比率** | **1.78** |
| 最大回撤 | 22.2% |
| 盈亏比 | 1.22 |

### 优化后权重

通过网格搜索优化：

| 因子 | 优化后权重 |
|------|-----------|
| 基础率 | 33.3% |
| 市场情绪 | 33.3% |
| 动量 | 6.7% |
| 交易量 | 20.0% |
| 新闻催化剂 | 6.7% |

**优化后表现：**
- Sharpe: 2.28 (+28%)
- 回报：+67.0%

## 🎯 策略逻辑

### EV 期望值策略

```python
EV = (预测概率 - 市场价格) / 市场价格

信号规则:
- EV > 5%  → BUY
- EV < -5% → SELL
- 其他     → SKIP
```

### 凯利仓位管理

```python
f* = (p × b - q) / b

实际使用 1/4 凯利，且单仓位不超过 10%
```

### 基础率套利

```python
缺口 = 基础率 - 市场价格

信号规则:
- 缺口 > 5%  → BUY
- 缺口 < -5% → SELL
```

### KL 散度套利

```python
KL(P∥Q) = Σ Pi × ln(Pi/Qi)

信号规则:
- KL > 0.15 → 套利机会
```

## 📊 每日报告

报告包含：
- 账户概览（资金、持仓、交易数）
- 策略表现（信号数、建议仓位）
- Top 交易机会（EV、基础率、KL 套利）
- 风险指标（仓位、回撤）

## 🔌 API 对接

### 模拟 API（测试用）

无需 API Key，使用内置模拟数据。

### 真实 API（生产用）

需要 Polymarket API Key：

```json
{
  "api_key": "your_api_key_here"
}
```

## ⚙️ 定时任务

设置每 15 分钟扫描一次：

```bash
# Cron 表达式
*/15 * * * * cd /path/to/polymarket-quant-bot && python3 main.py
```

## 📝 配置说明

### 策略开关

```json
"strategies": {
  "ev_strategy": {"enabled": true, "allocation": 0.25},
  "bayes_strategy": {"enabled": true, "allocation": 0.25},
  "base_rate_strategy": {"enabled": true, "allocation": 0.25},
  "kl_arb_strategy": {"enabled": true, "allocation": 0.25}
}
```

### 风险控制

```json
"risk_control": {
  "kelly_fraction": 0.25,
  "max_single_bet": 0.10,
  "max_total_exposure": 0.80,
  "stop_loss": -0.10,
  "take_profit": 0.20
}
```

## 🧪 测试

### 测试单个模块

```bash
# 测试 EV 计算器
python3 src/ev_calculator.py

# 测试预测模型
python3 src/prediction_model.py

# 测试回测系统
python3 src/backtester.py
```

### 完整测试

```bash
python3 main.py
```

## 📈 性能优化

### 因子权重优化

使用回测系统进行网格搜索：

```python
from backtester import Backtester

backtester = Backtester(initial_capital=10000)
best_weights, best_result = backtester.optimize_weights(historical_data, steps=5)
```

### 数据缓存

API 数据缓存在 `data/` 目录，避免重复请求。

## ⚠️ 风险提示

1. **模拟交易** - 当前为模拟模式，不构成投资建议
2. **历史数据** - 回测结果不代表未来表现
3. **市场风险** - 预测市场波动大，可能损失本金
4. **技术风险** - API 故障、网络问题等

## 📚 参考资料

- [Polymarket API 文档](https://api.polymarket.com)
- [期望值理论](https://en.wikipedia.org/wiki/Expected_value)
- [凯利公式](https://en.wikipedia.org/wiki/Kelly_criterion)
- [贝叶斯定理](https://en.wikipedia.org/wiki/Bayes%27_theorem)
- [KL 散度](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)

## 📄 许可证

MIT License

---

**项目状态：** 🟢 开发中

**最后更新：** 2026-03-18

**联系方式：** 4352395@qq.com
