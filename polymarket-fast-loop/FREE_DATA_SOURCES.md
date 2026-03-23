# 🆓 Polymarket 免费数据源方案

**目标**: 不花钱获取实时市场数据

---

## ✅ 完全免费的方案

### 方案 1: Web Fetch 抓取官网（推荐⭐）

**原理**: 直接用 `web_fetch` 抓取 polymarket.com 网页内容

**优点**:
- ✅ 完全免费
- ✅ 无需 API Key
- ✅ 实时数据

**缺点**:
- ⚠️ 需要解析 HTML
- ⚠️ 网站改版会失效

**实现**:
```python
import requests
from bs4 import BeautifulSoup

# 抓取热门页面
url = "https://polymarket.com"
resp = requests.get(url)
html = resp.text

# 解析市场数据
# ...
```

**OpenClaw 调用**:
```python
web_fetch({
    "url": "https://polymarket.com/browse?category=trending"
})
```

---

### 方案 2: Google Gemini API（免费额度）

**原理**: 使用 Google 的 Gemini API，带 Google Search 功能

**免费额度**:
- 每月 60 次免费调用（Gemini 2.0 Flash）
- 无需信用卡

**申请**:
```
https://aistudio.google.com/apikey
```

**配置**:
```json
{
  "tools": {
    "web": {
      "search": {
        "provider": "gemini",
        "gemini": {
          "apiKey": "AIza..."
        }
      }
    }
  }
}
```

**优点**:
- ✅ 每月 60 次免费
- ✅ 包含 Google 搜索结果
- ✅ AI 合成答案

**缺点**:
- ⚠️ 次数有限

---

### 方案 3: PredictIt API（学术用途）

**原理**: PredictIt 提供公开 API（需申请）

**网址**:
```
https://www.predictit.org/api/
```

**优点**:
- ✅ 免费
- ✅ 实时数据
- ✅ 类似 Polymarket 的预测市场

**缺点**:
- ⚠️ 需要申请 API Key
- ⚠️ 主要是美国政治市场
- ⚠️ 数据格式复杂

**示例**:
```
https://www.predictit.org/api/marketdata/all/
```

---

### 方案 4: RSS 订阅 + 新闻监控

**原理**: 监控 Polymarket Twitter 和新闻

**免费源**:
- Twitter: @PolymarketOrg (公开)
- RSS: 预测市场相关新闻

**工具**:
```python
# Twitter RSS 桥
https://r.jina.ai/http://twitter.com/PolymarketOrg
```

**Jina AI Reader** (完全免费):
```
https://r.jina.ai/http://polymarket.com
```

这个服务可以：
- 免费抓取任何网页
- 返回纯文本内容
- 无需 API Key

**示例**:
```bash
curl https://r.jina.ai/http://polymarket.com
```

---

### 方案 5: 手动 + 半自动（最实际）

**流程**:
```
1. 你每天浏览 polymarket.com（1 分钟）
2. 截图或复制热门市场给我
3. 我帮你分析策略、赔率、风险
4. 你决定是否交易
```

**优点**:
- ✅ 完全免费
- ✅ 最准确
- ✅ 无需技术配置

**缺点**:
- ⚠️ 需要手动操作

---

## 🎯 推荐方案：Jina AI Reader

### 什么是 Jina AI？

完全免费的网页抓取服务：
- 网址：https://r.jina.ai
- 无需 API Key
- 无使用限制

### 使用方法

**命令行**:
```bash
curl https://r.jina.ai/http://polymarket.com
```

**Python**:
```python
import requests

# 抓取 Polymarket 首页
resp = requests.get("https://r.jina.ai/http://polymarket.com")
content = resp.text
print(content)

# 抓取特定市场
resp = requests.get("https://r.jina.ai/http://polymarket.com/market/XXX")
```

### 集成到日报

```python
def get_polymarket_trending():
    """使用 Jina AI 获取热门"""
    resp = requests.get("https://r.jina.ai/http://polymarket.com/browse?category=trending")
    return resp.text
```

---

## 📊 方案对比

| 方案 | 费用 | 实时性 | 难度 | 推荐度 |
|------|------|--------|------|--------|
| Jina AI Reader | 🆓 免费 | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Web Fetch | 🆓 免费 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Gemini API | 🆓 60 次/月 | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| PredictIt | 🆓 免费 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 手动浏览 | 🆓 免费 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ |
| Brave API | 💰 $5/1000 次 | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |

---

## 🚀 立即开始（零配置）

### 测试 Jina AI

```bash
# 测试抓取 Polymarket
curl "https://r.jina.ai/http://polymarket.com"

# 测试抓取热门页面
curl "https://r.jina.ai/http://polymarket.com/browse?category=trending"
```

### 集成到现有代码

修改 `monitor.py`:

```python
def get_markets_jina(self, limit: int = 20) -> List[Dict]:
    """使用 Jina AI 获取市场数据"""
    try:
        resp = requests.get(
            f"https://r.jina.ai/http://polymarket.com/browse?category=trending",
            timeout=10
        )
        content = resp.text
        
        # 解析返回的文本内容
        # 提取市场信息
        markets = parse_jina_content(content)
        
        return markets
    except Exception as e:
        logger.error(f"Jina AI 抓取失败：{e}")
        return []
```

---

## 💡 最佳实践

### 日常流程

```
早上 8:00:
1. 自动运行 Jina AI 抓取热门
2. 生成日报（市场概览 + 策略信号）
3. 发送给你

盘中监控:
1. 重大事件发生时
2. 手动触发抓取
3. 分析交易机会
```

### 代码示例

```python
# daily_report.py 修改
from jina_reader import fetch_url

def generate_market_overview():
    # 使用 Jina AI 代替 Gamma API
    content = fetch_url("https://polymarket.com/browse?category=trending")
    markets = parse_content(content)
    return markets
```

---

## ✅ 结论

**最佳免费方案**: Jina AI Reader

- 完全免费
- 无需配置
- 实时数据
- 简单易用

**下一步**: 我可以帮你修改代码，用 Jina AI 替代 Gamma API！

---

*最后更新*: 2026-03-13
