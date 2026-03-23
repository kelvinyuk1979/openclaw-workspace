# 📈 A 股统一交易系统

整合技术面、基本面、情绪面三策略的 A 股量化交易平台。

---

## 📊 策略组成

| 策略 | 资金来源 | 核心指标 | 扫描频率 |
|------|----------|----------|----------|
| **技术面** | 40% | MA/MACD/RSI/KDJ/BOLL | 30 分钟（交易时间） |
| **基本面** | 35% | PE/ROE/收入增长/利润增长 | 手动 |
| **情绪面** | 25% | 新闻情绪/资金流/社交评分 | 手动 |

---

## 🚀 快速开始

### 1. 扫描测试

```bash
cd a-share-trading-system
python3 scan_only.py
```

### 2. 发送邮件报告

```bash
python3 main.py
```

### 3. 定时任务

已配置系统 crontab：
- **扫描** - 每 30 分钟（交易时间 9-11 点，13-15 点）
- **邮件** - 每天 9:00 AM 和 3:30 PM

---

## 📁 项目结构

```
a-share-trading-system/
├── config/
│   └── unified_config.json    # 统一配置
├── strategies/
│   ├── technical/adapter.py   # 技术面策略
│   ├── fundamental/adapter.py # 基本面策略
│   └── sentiment/adapter.py   # 情绪面策略
├── reports/
│   └── daily_report.py        # 邮件报告
├── logs/                      # 运行日志
├── data/                      # 缓存数据
├── scan_only.py               # 高频扫描
├── main.py                    # 邮件报告
├── simulation.json            # 模拟账户
└── README.md                  # 本文档
```

---

## ⚙️ 配置说明

### 策略配置

```json
"strategies": {
  "technical": {
    "enabled": true,
    "allocation": 0.40,
    "scan_interval_minutes": 30
  }
}
```

### 风险控制

```json
"risk_control": {
  "max_total_exposure": 0.80,
  "stop_loss": -0.08,
  "take_profit": 0.15,
  "max_single_stock": 0.20
}
```

### 股票池

```json
"stock_pool": {
  "a_share": {
    "enabled": true,
    "markets": ["SH", "SZ", "BJ"],
    "exclude_st": true
  }
}
```

---

## 📧 邮件报告

**发送时间：** 每个交易日 9:00 AM 和 3:30 PM

**内容：**
- 账户概览（余额、盈亏、收益率）
- 三策略表现对比
- Top 信号列表
- 策略配置状态

---

## 📈 策略详情

### 技术面策略

**指标：**
- MA（5/10/20/60 日均线）
- MACD（金叉/死叉）
- RSI（超买/超卖）
- KDJ（随机指标）
- BOLL（布林带）

**信号：**
- RSI < 30 → 买入（超卖）
- RSI > 70 → 卖出（超买）
- MACD 金叉 → 买入
- MACD 死叉 → 卖出

### 基本面策略

**选股标准：**
- **价值股**：PE < 20 + ROE > 15%
- **成长股**：收入增长 > 30% + 利润增长 > 30%

**指标：**
- PE（市盈率）
- ROE（净资产收益率）
- 收入增长率
- 利润增长率

### 情绪面策略

**信号源：**
- 新闻情绪分析（正面/负面）
- 主力资金流向（流入/流出）
- 社交热度评分

**信号：**
- 新闻情绪 > 0.7 → 买入
- 新闻情绪 < 0.3 → 卖出
- 主力流入 > 1 亿 → 买入
- 主力流出 > 1 亿 → 卖出

---

## ⚠️ 风险提示

- **模拟交易** - 当前为模拟模式，不构成投资建议
- **历史数据** - 回测结果不代表未来表现
- **市场风险** - A 股波动大，可能损失本金
- **技术风险** - API 故障、网络问题等

---

## 📞 问题排查

### 邮件未收到
1. 检查垃圾邮件箱
2. 查看 `logs/cron.log`
3. 检查邮箱配置

### 扫描停止
1. 检查 `logs/scan.log`
2. 手动运行 `python3 scan_only.py`
3. 检查 crontab：`crontab -l`

---

**版本：** 1.0  
**最后更新：** 2026-03-19  
**联系：** 4352395@qq.com
