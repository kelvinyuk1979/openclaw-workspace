# 🌍 Timezone Arbitrage Agent

**时区套利预测市场 Agent** - 利用跨时区信息差获利

---

## 📊 策略概述

**核心逻辑：** Polymarket 70% 交易者是美国人，但世界事件不按 EST 发生。

**套利机会：**
1. 亚洲/欧洲事件在当地时间白天发生
2. 美国交易者此时在睡觉
3. 官方信息已公开，但价格未更新
4. 结算发生在美东时间凌晨 2-6 点
5. 美国交易者醒来时，市场已结束

---

## 🎯 性能记录

| 日期 | 投入 | 回报 | 利润率 | 市场数 |
|------|------|------|--------|--------|
| 2026-03-14 | $12,000 | $43,800 | 365% | 6 |

**运行天数：** 9 天  
**触发次数：** 1 次（严格筛选）

---

## 🛠️ 快速开始

### 1. 环境要求

```bash
Python 3.10+
Node.js 18+
Redis (缓存)
PostgreSQL (日志)
```

### 2. 安装依赖

```bash
cd timezone-arbitrage
pip install -r requirements.txt
npm install  # Polymarket SDK
```

### 3. 配置

```bash
cp config/config.example.yaml config/config.yaml
# 编辑配置文件，填入 API keys
```

### 4. 运行

```bash
# 开发模式
python src/main.py --dev

# 生产模式
python src/main.py

# Docker
docker-compose up -d
```

---

## 📁 目录结构

```
timezone-arbitrage/
├── src/
│   ├── main.py              # 主程序入口
│   ├── monitor.py           # 信息源监控
│   ├── analyzer.py          # Edge 计算
│   ├── executor.py          # 交易执行
│   ├── notifier.py          # Telegram 通知
│   └── utils/
│       ├── timezones.py     # 时区转换
│       └── edge_calc.py     # Edge 公式
├── config/
│   ├── config.yaml          # 主配置
│   ├── sources.yaml         # 信息源配置
│   └── markets.yaml         # 目标市场配置
├── logs/                    # 运行日志
├── tests/                   # 测试用例
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## ⚙️ 核心配置

### 触发条件

```yaml
triggers:
  min_edge_percent: 30      # 最小 Edge 30%
  settlement_window_min: 90 # 结算窗口 90 分钟
  max_capital_per_trade: 12000
  trading_hours:
    start: "02:00"          # 美东时间凌晨 2 点
    end: "06:00"            # 美东时间凌晨 6 点
```

### 信息源

```yaml
sources:
  - name: Japan BOJ
    type: rss
    url: https://www.boj.or.jp/en/rss/
    timezone: Asia/Tokyo
    keywords: ["rate decision", "interest rate"]
    
  - name: EU Parliament
    type: livestream
    url: https://multimedia.europarl.europa.eu/
    timezone: Europe/Brussels
    
  - name: Korea Government
    type: rss
    url: https://www.korea.kr/rss/
    timezone: Asia/Seoul
    
  # ... 其他信息源
```

---

## 📊 Edge 计算

```python
def calculate_edge(true_prob, market_price):
    """
    计算 Edge
    
    Args:
        true_prob: 基于官方信息的真实概率 (0-1)
        market_price: Polymarket 价格 (0-1)
    
    Returns:
        edge_percent: Edge 百分比
    """
    edge = (true_prob - market_price) / market_price
    return edge * 100

# 示例
# BOJ leak 显示 68% 概率，Polymarket 价格 23¢
edge = (0.68 - 0.23) / 0.23 = 195%
```

---

## 🔔 通知流程

### 1. 发现机会

```
[3:47 AM] 发现 6 个会在接下来 90 分钟内结算的市场
美国人都还在睡，需要批准部署 $12K

市场列表:
1. Japan rate decision - BOJ leak 显示 YES 68%，Polymarket 23¢
2. EU emergency vote - 直播 YES 领先，Polymarket 31¢
3. South Korea policy - 政府 RSS 已确认，Polymarket 19¢
4. Australia trade deal - 部长 2 小时前表态，Polymarket 27¢
5. UAE production cut - OPEC 会议记录公开，Polymarket 15¢
6. Singapore regulation - 议会直播中，Polymarket 22¢

汇总:
- 潜在 edge: $43K
- 窗口期：90 分钟
- 所需资金：$12,000

回复 yes 确认执行
```

### 2. 用户确认

```
用户: yes
Agent: 已批准，正在部署...
```

### 3. 执行完成

```
✅ 6 个订单已全部提交
总投入：$12,000
预计回报：$43,800
预计结算时间：4:00 AM - 6:00 AM EST
```

### 4. 结算通知

```
✅ 全部结算完成

Japan: +$8,200 (23¢ → 100¢)
EU: +$6,900 (31¢ → 100¢)
Korea: +$11,400 (19¢ → 100¢)
Australia: +$7,100 (27¢ → 100¢)
UAE: +$5,800 (15¢ → 100¢)
Singapore: +$4,400 (22¢ → 100¢)

总计：+$43,800
```

---

## ⚠️ 风险控制

### 仓位管理

```yaml
risk_management:
  max_capital_per_trade: 12000
  max_positions: 10
  position_size_percent: 15  # 每个市场不超过 15%
  stop_loss: null            # 不止损（基于确定性套利）
```

### 信息源验证

```yaml
verification:
  min_sources: 2             # 至少 2 个独立来源确认
  confidence_threshold: 0.8  # 置信度>80%
  blacklist: []              # 不可靠来源黑名单
```

### 合规检查

```yaml
compliance:
  jurisdiction: ["US", "SG"]
  excluded_markets: ["assassination", "terrorism"]
  max_daily_volume: 50000
```

---

## 📈 扩展方向

### 1. 新市场

- [ ] Kalshi（美国监管预测市场）
- [ ] PredictIt（政治预测）
- [ ] Metaculus（长期预测）

### 2. 新信息源

- [ ] 中国央行公告
- [ ] 英国议会直播
- [ ] 加拿大统计局
- [ ] 巴西财政部

### 3. 新策略

- [ ] 财报季盘后套利
- [ ] 加密货币跨交易所价差
- [ ] 外汇时区流动性套利

---

## 🔐 安全建议

1. **API Keys** - 使用环境变量或加密存储
2. **访问控制** - Telegram 白名单
3. **日志审计** - 所有交易记录保留 90 天
4. **紧急停止** - 设置 kill switch

---

## 📞 支持

**问题反馈：** 提交 Issue  
**策略讨论：** Discord/Telegram

---

**最后更新：** 2026-03-14  
**版本：** 1.0.0  
**状态：** Production (运行 9 天)
