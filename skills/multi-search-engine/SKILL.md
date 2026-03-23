---
name: multi-search-engine
description: 多搜索引擎并行查询工具，同时搜索 Google、Bing、DuckDuckGo、百度等引擎，获取更全面的结果。
emoji: 🔍
---

# Multi-Search-Engine - 多搜索引擎技能

## 功能概述

并行查询多个搜索引擎，获取更全面、多样化的搜索结果，避免单一引擎的信息茧房。

## 支持的搜索引擎

### 🔎 国际引擎

| 引擎 | API/接口 | 特点 |
|------|----------|------|
| Google | Custom Search API / 网页抓取 | 最全面，质量高 |
| Bing | Bing Search API | 微软生态，视频搜索强 |
| DuckDuckGo | HTML 抓取 | 隐私保护，无追踪 |
| Brave Search | API | 隐私友好，独立索引 |

### 🇨🇳 国内引擎

| 引擎 | 接口 | 特点 |
|------|------|------|
| 百度 | 网页抓取 | 中文内容最全 |
| 必应中国 | API | 中英文兼顾 |
| 搜狗 | 网页抓取 | 微信内容独家 |
| 360 搜索 | 网页抓取 | 安全导向 |

## 使用场景

### ✅ 适合使用多引擎搜索的情况

- **深度研究** - 需要全面信息覆盖
- **事实验证** - 交叉验证信息准确性
- **竞品分析** - 不同引擎结果差异大
- **SEO 研究** - 了解各引擎排名差异
- **敏感话题** - 避免单一引擎审查/偏见
- **多语言内容** - 各引擎语言覆盖不同

### ❌ 不需要多引擎的情况

- 简单事实查询（天气、定义等）
- 已知精确 URL 的访问
- 本地化服务查询（地图、餐厅）

## 使用方法

### 基础查询

```python
# 并行搜索多个引擎
results = multi_search(
    query="AI 大模型最新进展",
    engines=["google", "bing", "baidu"],
    limit_per_engine=10,
    deduplicate=True
)
```

### 参数说明

| 参数 | 选项 | 默认值 | 说明 |
|------|------|--------|------|
| query | string | 必填 | 搜索关键词 |
| engines | list | ["google", "bing"] | 使用的引擎列表 |
| limit_per_engine | int | 10 | 每个引擎返回结果数 |
| deduplicate | bool | True | 是否去重 |
| language | string | "zh" | 结果语言偏好 |
| region | string | "CN" | 地区偏好 |
| time_range | string | "any" | 时间范围 |

### 时间范围选项

- `any` - 不限时间
- `24h` - 过去 24 小时
- `7d` - 过去 7 天
- `30d` - 过去 30 天
- `1y` - 过去 1 年

## 输出格式

### 标准格式

```markdown
## 🔍 搜索结果：[查询词]

### 汇总统计
- **搜索引擎**: Google, Bing, Baidu
- **总结果数**: 45
- **去重后**: 32
- **搜索时间**: 2.3 秒

### 🥇 高相关性结果 (Top 10)

1. **[标题]** - 来源引擎：Google, Bing
   - URL: https://...
   - 摘要：[内容摘要]
   - 发布时间：2026-03-14
   - 相关性评分：95/100

2. **[标题]** - 来源引擎：Baidu
   - URL: https://...
   - 摘要：[内容摘要]
   - 发布时间：2026-03-13
   - 相关性评分：90/100

### 📊 引擎对比

| 排名 | Google | Bing | Baidu |
|------|--------|------|-------|
| 1 | [标题 1] | [标题 1] | [标题 1] |
| 2 | [标题 2] | [标题 2] | [标题 2] |
| 3 | [标题 3] | [标题 3] | [标题 3] |

### 🏷️ 发现的主题分类
- [主题 1]: X 条结果
- [主题 2]: Y 条结果
- [主题 3]: Z 条结果
```

### 去重策略

```python
def deduplicate_results(results):
    """
    去重策略：
    1. URL 标准化（去除追踪参数）
    2. 标题相似度比较
    3. 内容指纹对比
    4. 保留多引擎共同出现的结果（优先级高）
    """
```

## 实现方案

### 方案 A：官方 API（推荐）

```python
# Google Custom Search API
from googleapiclient.discovery import build

def search_google(query, api_key, cse_id):
    service = build("customsearch", "v1", developerKey=api_key)
    results = service.cse().list(q=query, cx=cse_id).execute()
    return results['items']

# Bing Search API
from azure.cognitiveservices.search.websearch import WebSearchClient

def search_bing(query, subscription_key):
    client = WebSearchClient(endpoint, CognitiveServicesCredentials(key))
    results = client.web.search(query=query)
    return results.web_pages.value
```

### 方案 B：网页抓取（备选）

```python
import requests
from bs4 import BeautifulSoup

def search_duckduckgo(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for result in soup.select('.result'):
        results.append({
            'title': result.select_one('.result__title').text,
            'url': result.select_one('.result__url').text,
            'snippet': result.select_one('.result__snippet').text
        })
    return results
```

### 方案 C：SerpAPI 聚合（最简便）

```python
from serpapi import GoogleSearch, BingSearch

def multi_search_serpapi(query, engines):
    results = {}
    for engine in engines:
        if engine == "google":
            search = GoogleSearch({"q": query, "api_key": SERPAPI_KEY})
            results[engine] = search.get_dict()['organic_results']
        elif engine == "bing":
            search = BingSearch({"q": query, "api_key": SERPAPI_KEY})
            results[engine] = search.get_dict()['organic_results']
    return results
```

## 高级功能

### 1. 智能引擎选择

根据查询类型自动选择最佳引擎组合：

```python
def select_engments(query):
    if any(keyword in query for keyword in ["技术", "代码", "API"]):
        return ["google", "bing", "github"]
    elif any(keyword in query for keyword in ["新闻", "时事"]):
        return ["google", "bing", "baidu", "duckduckgo"]
    elif any(keyword in query for keyword in ["学术", "论文", "研究"]):
        return ["google_scholar", "semantic_scholar", "arxiv"]
    else:
        return ["google", "bing", "baidu"]
```

### 2. 结果融合排序

```python
def fuse_rankings(results):
    """
    Borda Count 融合排序：
    - 每个引擎的排名转换为分数
    - 多引擎共同出现的结果获得额外加分
    - 最终按总分排序
    """
    fused = {}
    for engine, engine_results in results.items():
        for rank, item in enumerate(engine_results):
            url = normalize_url(item['url'])
            if url not in fused:
                fused[url] = {'item': item, 'score': 0, 'engines': []}
            # Borda 分数
            fused[url]['score'] += (len(engine_results) - rank)
            fused[url]['engines'].append(engine)
    
    # 多引擎加分
    for url, data in fused.items():
        if len(data['engines']) > 1:
            data['score'] *= 1.2  # 20% 加分
    
    return sorted(fused.values(), key=lambda x: x['score'], reverse=True)
```

### 3. 结果分类聚类

```python
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

def cluster_results(results, n_clusters=5):
    """
    将搜索结果按主题聚类
    """
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    snippets = [r['snippet'] for r in results]
    embeddings = model.encode(snippets)
    
    kmeans = KMeans(n_clusters=n_clusters)
    labels = kmeans.fit_predict(embeddings)
    
    clustered = {}
    for i, label in enumerate(labels):
        if label not in clustered:
            clustered[label] = []
        clustered[label].append(results[i])
    
    return clustered
```

### 4. 事实交叉验证

```python
def cross_verify_facts(claims, results):
    """
    跨引擎验证事实准确性
    """
    verification = {}
    for claim in claims:
        supporting = 0
        contradicting = 0
        for result in results:
            if supports_claim(claim, result['snippet']):
                supporting += 1
            elif contradicts_claim(claim, result['snippet']):
                contradicting += 1
        
        verification[claim] = {
            'confidence': supporting / (supporting + contradicting + 1),
            'supporting_sources': supporting,
            'contradicting_sources': contradicting
        }
    
    return verification
```

## 集成示例

### 与 AI 简报集成

```python
def research_for_ai_brief(topic):
    """
    为 AI 简报做深度研究
    """
    results = multi_search(
        query=topic,
        engines=["google", "bing", "duckduckgo"],
        time_range="24h",
        limit_per_engine=20
    )
    
    # 提取关键信息
    summary = generate_summary(results)
    sources = extract_unique_sources(results)
    
    return {
        'summary': summary,
        'sources': sources,
        'confidence': calculate_confidence(results)
    }
```

### 与股票分析集成

```python
def research_stock(symbol):
    """
    研究股票相关信息
    """
    queries = [
        f"{symbol} 最新财报",
        f"{symbol} 分析师评级",
        f"{symbol} 竞争对手分析",
        f"{symbol} 风险提示"
    ]
    
    all_results = {}
    for query in queries:
        all_results[query] = multi_search(
            query=query,
            engines=["google", "bing", "baidu"],
            limit_per_engine=10
        )
    
    return synthesize_stock_research(all_results)
```

## 配置示例

### 配置文件 (~/.openclaw/config/search.json)

```json
{
  "engines": {
    "google": {
      "enabled": true,
      "api_key": "${GOOGLE_API_KEY}",
      "cse_id": "${GOOGLE_CSE_ID}",
      "weight": 1.0
    },
    "bing": {
      "enabled": true,
      "api_key": "${BING_API_KEY}",
      "weight": 0.9
    },
    "baidu": {
      "enabled": true,
      "use_scraper": true,
      "weight": 0.8
    },
    "duckduckgo": {
      "enabled": true,
      "use_scraper": true,
      "weight": 0.7
    }
  },
  "defaults": {
    "limit_per_engine": 10,
    "deduplicate": true,
    "time_range": "any"
  },
  "rate_limits": {
    "requests_per_minute": 30,
    "delay_between_requests_ms": 500
  }
}
```

## 最佳实践

### 1. 查询优化

```python
# 好的查询
"AI 大模型 2026 年 最新进展 site:arxiv.org"
"腾讯控股 2026 Q1 财报 营收 利润"

# 避免的查询
"AI"  # 太宽泛
"最好的股票"  # 主观
```

### 2. 结果验证

- ✅ 交叉验证关键信息
- ✅ 检查来源可信度
- ✅ 注意发布时间
- ✅ 识别广告/推广内容

### 3. 性能优化

- 并行请求多个引擎
- 缓存常用查询结果
- 设置合理的超时时间
- 实现失败重试机制

## 注意事项

1. **API 限制** - 各引擎有调用频率限制
2. **地理差异** - 相同查询不同地区结果可能不同
3. **个性化偏差** - 登录状态影响搜索结果
4. **法律合规** - 遵守各引擎服务条款
5. **隐私保护** - 避免搜索敏感个人信息

## 扩展方向

- 🔬 学术搜索集成（Google Scholar, Semantic Scholar）
- 📰 新闻搜索专用模式
- 🛒 电商搜索（Amazon, 淘宝等）
- 📱 社交媒体搜索（Twitter, 微博等）
- 🎬 多媒体搜索（图片、视频、播客）
