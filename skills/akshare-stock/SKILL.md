---
name: akshare-stock
description: 全球股票量化数据分析工具，基于 AkShare 库获取 A 股、港股、美股行情、财务数据、板块信息等。用于股票查询、行情数据、财务分析、选股等问题。
---

# 全球股票量化 - AkShare 数据接口

## 支持市场

- **A 股**：沪深京全部股票
- **港股**：HKEX 主板、创业板
- **美股**：NYSE、NASDAQ、AMEX

## 快速开始

安装依赖：
```bash
pip install akshare
```

## 支持的功能

### 1. 实时行情查询

```python
import akshare as ak

# A 股实时行情
stock_zh_a_spot_em()

# 港股实时行情
stock_hk_spot_em()

# 美股实时行情
stock_us_spot_em()

# 个股实时行情
stock_zh_a_hist(symbol="000001", adjust="qfq")
stock_hk_hist(symbol="00700", adjust="qfq")  # 腾讯控股
stock_us_hist(symbol="AAPL", adjust="qfq")  # 苹果
```

### 2. 历史 K 线数据

```python
import akshare as ak

# A 股日 K 线
stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20241231", adjust="qfq")

# 港股日 K 线
stock_hk_hist(symbol="00700", period="daily", start_date="20240101", end_date="20241231", adjust="qfq")

# 美股日 K 线
stock_us_hist(symbol="AAPL", period="daily", start_date="20240101", end_date="20241231", adjust="qfq")

# 周 K/月 K
stock_zh_a_hist(symbol="000001", period="weekly")  # 周 K
stock_zh_a_hist(symbol="000001", period="monthly")  # 月 K
```

### 3. 财务数据

```python
import akshare as ak

# 财务报表（A 股）
stock_financial_abstract_ths(symbol="000001", indicator="按报告期")

# 主要财务指标（A 股）
stock_financial_analysis_indicator(symbol="000001")

# 港股财务数据
stock_hk_financial_analysis(symbol="00700")

# 美股财务数据（通过 Yahoo Finance 接口）
stock_us_financial(symbol="AAPL")
```

### 4. 板块/行业分析

```python
import akshare as ak

# 行业板块行情（A 股）
stock_board_industry_name_em()

# 概念板块行情（A 股）
stock_board_concept_name_em()

# 板块内个股
stock_board_industry_cons_em(symbol="半导体")

# 港股板块
stock_hk_board()

# 美股板块
stock_us_sector()
```

### 5. 资金流向

```python
import akshare as ak

# A 股个股资金流向
stock_individual_fund_flow(stock="000001", market="sh")

# 大单净流入
stock_individual_fund_flow(stock="000001", market="sh", symbol="大单净流入")

# 港股资金流向
stock_hk_fund_flow(symbol="00700")

# 美股资金流向
stock_us_fund_flow(symbol="AAPL")
```

### 6. 龙虎榜（A 股）

```python
import akshare as ak

# 每日龙虎榜
stock_lhb_detail_em(date="20240930")

# 机构调研
stock_zlzj_em()
```

### 7. 新股/IPO

```python
import akshare as ak

# A 股新股申购
stock_new_ipo_em()

# 港股新股
stock_hk_ipo()

# 美股 IPO
stock_us_ipo()
```

### 8. 融资融券

```python
import akshare as ak

# A 股融资融券
stock_margin_sse(symbol="600000")

# 融资融券明细
stock_rzrq_detail_em(symbol="600000", date="20240930")
```

## 常用股票代码

### A 股
- **平安银行**: 000001
- **贵州茅台**: 600519
- **宁德时代**: 300750
- **比亚迪**: 002594
- **招商银行**: 600036

### 港股
- **腾讯控股**: 00700
- **阿里巴巴**: 09988
- **美团**: 03690
- **小米集团**: 01810
- **汇丰控股**: 00005

### 美股
- **苹果**: AAPL
- **微软**: MSFT
- **英伟达**: NVDA
- **特斯拉**: TSLA
- **亚马逊**: AMZN
- **谷歌**: GOOGL
- **Meta**: META

## 华尔街风格股票分析框架

### 核心分析维度

1. **商业模式** - 公司如何赚钱，收入来源
2. **竞争优势/护城河** - 品牌、网络效应、切换成本、成本优势、专利
3. **行业趋势** - 市场规模、增速、技术变革方向
4. **财务健康** - 收入增长、净利润、自由现金流、利润率、债务水平、ROE
5. **主要风险** - 经济周期、行业颠覆、竞争加剧、监管政策、财务风险
6. **估值分析** - PE/PB/PS 对比、DCF 估值、行业平均、低估/高估判断
7. **情景分析** - 乐观/中性/悲观假设下的目标价
8. **催化剂** - 12-24 个月内的关键事件

### 分析输出格式

```markdown
## 📊 [股票名称] ([代码]) - 深度分析

### 商业模式
[简述公司如何赚钱]

### 竞争优势（护城河评分：X/10）
- 品牌实力：
- 网络效应：
- 切换成本：
- 成本优势：
- 技术壁垒：

### 财务健康度
| 指标 | 数值 | 趋势 |
|------|------|------|
| 收入增长 (5 年 CAGR) | X% | ↑/↓ |
| 净利润率 | X% | ↑/↓ |
| 自由现金流 | $X 亿 | ↑/↓ |
| 负债率 | X% | - |
| ROE | X% | ↑/↓ |

### 估值对比
| 公司 | PE | PB | PS |
|------|-----|-----|-----|
| 目标公司 | X | X | X |
| 行业平均 | X | X | X |
| 竞争对手 A | X | X | X |

### 主要风险（按严重程度排序）
1. ⚠️ [最高风险]
2. ⚠️ [中等风险]
3. ⚠️ [低风险]

### 多头 vs 空头辩论
**🐂 多头观点：**
- [核心论据 1]
- [核心论据 2]

**🐻 空头观点：**
- [核心论据 1]
- [核心论据 2]

### 投资建议
- **短期（1 年）**：买入/持有/回避
- **长期（5 年+）**：买入/持有/回避
- **目标价**：$X（12 个月）
- **催化剂**：[关键事件]
```

## 备选方案：Baostock（A 股）

如果 AkShare 安装失败，可使用 baostock（更轻量）:

```python
import baostock as bs

# 登录
lg = bs.login()
print(lg.error_msg)

# 获取历史 K 线
rs = bs.query_history_k_data_plus('sh.600519',
    'date,code,open,high,low,close,volume',
    start_date='20250101',
    end_date='20251231')

data_list = []
while rs.next:
    data_list.append(rs.get_row_data())
    
bs.logout()
```

## 注意事项

1. 数据仅供学术研究，**不构成投资建议**
2. 接口可能因目标网站变动而失效
3. 建议添加异常处理和重试机制
4. 跨市场数据注意时区和货币单位
5. 港股代码格式：00700（6 位数字）
6. 美股代码格式：AAPL（字母代码）
