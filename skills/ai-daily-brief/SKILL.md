---
name: ai-daily-brief
description: 全球 AI 圈每日简报工具，追踪最有影响力的机构和个人动态，生成 AI 行业早报。
emoji: 🤖
---

# 全球 AI 圈每日简报

## 核心目标

追踪全球 AI 领域最有影响力的机构和个人，每日生成简报，让用户零信息差了解 AI 圈动态。

## 追踪清单

### 🏢 核心机构账号

| 机构 | Twitter/X | 重要性 | 关注重点 |
|------|-----------|--------|----------|
| OpenAI | @OpenAI | ⭐⭐⭐⭐⭐ | GPT/Sora/o 系列模型发布 |
| Google DeepMind | @GoogleDeepMind | ⭐⭐⭐⭐⭐ | Gemini/Veo/AlphaFold |
| NVIDIA AI | @NVIDIAAI | ⭐⭐⭐⭐⭐ | GPU 算力与 AI 基础设施 |
| Anthropic | @AnthropicAI | ⭐⭐⭐⭐⭐ | Claude 系列、AI 安全 |
| Meta AI | @MetaAI | ⭐⭐⭐⭐ | LLaMA 开源生态 |
| DeepSeek | @deepseek_ai | ⭐⭐⭐⭐ | 开源大模型搅局者 |
| 阿里通义 | @Alibaba_Owen | ⭐⭐⭐⭐ | Qwen 系列、多模态 |
| Midjourney | @midjourney | ⭐⭐⭐⭐ | AI 图像生成风向标 |
| Moonshot | @Kimi_Moonshot | ⭐⭐⭐ | 长上下文与推理 |
| MiniMax | @MiniMax_AI | ⭐⭐⭐ | 视频 + 语音 + 文本全模态 |
| 字节跳动 | @BytedanceTalk | ⭐⭐⭐ | Seedance/Seedream 视频模型 |
| Groq | @GroqInc | ⭐⭐⭐ | LPU 推理芯片 |
| Hailuo AI | @Hailuo_AI | ⭐⭐⭐ | MiniMax 视频生成 |
| MIT CSAIL | @MIT_CSAIL | ⭐⭐⭐ | 学术前沿研究 |
| IBM Data | @IBMData | ⭐⭐ | 企业 AI 应用 |

### 👤 核心人物（15 位最有影响力）

| 人物 | Twitter/X | 身份 | 关注重点 |
|------|-----------|------|----------|
| Sam Altman | @sama | OpenAI CEO | 行业震动级推文 |
| Elon Musk | @elonmusk | xAI 创始人/X 平台 | Grok 模型、AI 观点 |
| Mark Zuckerberg | @zuck | Meta CEO | LLaMA 开源战略 |
| Dario Amodei | @DarioAmodei | Anthropic CEO | Claude、AI 安全 |
| Daniela Amodei | @danielaamodei | Anthropic 总裁 | AI 安全与产品化 |
| Ilya Sutskever | @ilyasut | SSI 创始人/前 OpenAI 首席科学家 | AGI 研究 |
| Andrej Karpathy | @karpathy | AI 工程师/教育家 | 深度好文、AI 教程 |
| Yann LeCun | @ylecun | Meta AI 首席科学家/图灵奖得主 | AGI 观点、技术评论 |
| Demis Hassabis | @demishassabis | Google DeepMind CEO | AlphaFold、AGI 研究 |
| Jeff Dean | @jeffdean | Google DeepMind 首席科学家 | AI 基础设施 |
| Andrew Ng | @AndrewYNg | AI 教育布道者 | 行业趋势判断 |
| Fei-Fei Li | @drfeifei | ImageNet 之母/World Labs 创始人 | AI+ 空间智能 |
| Thomas Wolf | @Thom_Wolf | Hugging Face 联创 | 开源 AI 生态 |
| Greg Brockman | @gdb | OpenAI 联创 | 技术与产品视角 |
| Peter Steinberger | @steipete | OpenClaw 创始人/现 OpenAI | 开发者视角 |

### 📊 补充影响者

| 人物 | Twitter/X | 身份 | 关注重点 |
|------|-----------|------|----------|
| Gary Marcus | @GaryMarcus | AI 批评者 | AI 泡沫预警 |
| Junyang Lin | @JustinLin610 | Qwen 团队负责人 | 大模型技术细节 |
| Eliezer Yudkowsky | @ESYudkowsky | AI 安全"末日预言家" | AI 安全极端观点 |
| Erik Brynjolfsson | @erikbryn | 斯坦福经济学家 | AI 社会影响 |
| Allie K. Miller | @alliekmiller | AI 投资人 | 产业落地趋势 |
| Bojan Tunguz | @tunguz | NVIDIA 数据科学家 | 实战 ML 干货 |
| Ronald van Loon | @Ronald_vanLoon | AI 影响力榜单常客 | 行业综合动态 |

### 🤖 聚合账号

| 账号 | Twitter/X | 类型 |
|------|-----------|------|
| DeepLearn0e7 | @DeepLearn0e7 | AI 全球影响者 |
| nigewillson | @nigewillson | AI 伦理与治理 |
| petitegeek | @petitegeek | 机器人学/具身智能 |
| YuHelenYu | @YuHelenYu | 数字化转型与 AI 商业化 |
| Tamara McCleary | @TamaraMcCleary | 企业 AI 应用与战略 |

## 简报生成流程

### 1. 数据收集（每日）

```python
# 伪代码示例
def collect_ai_news():
    sources = [
        # 机构账号
        "@OpenAI", "@GoogleDeepMind", "@NVIDIAAI", "@AnthropicAI",
        "@MetaAI", "@deepseek_ai", "@Alibaba_Owen", "@midjourney",
        
        # 核心人物
        "@sama", "@elonmusk", "@zuck", "@DarioAmodei",
        "@karpathy", "@ylecun", "@demishassabis", "@AndrewYNg",
        "@drfeifei", "@Thom_Wolf", "@gdb", "@steipete"
    ]
    
    for account in sources:
        tweets = get_recent_tweets(account, hours=24)
        if is_significant(tweets):
            add_to_brief(account, tweets)
```

### 2. 筛选标准

**纳入简报的内容：**
- ✅ 新产品/模型发布
- ✅ 重大技术突破
- ✅ 重要合作/投资
- ✅ 行业趋势判断
- ✅ 争议性观点（引发讨论）
- ✅ 开源项目更新
- ✅ 重要人事变动

**忽略的内容：**
- ❌ 日常营销内容
- ❌ 转发无评论
- ❌ 与 AI 无关的个人动态
- ❌ 重复信息

### 3. 简报格式

```markdown
# 🤖 全球 AI 圈每日简报
**日期：** YYYY-MM-DD
**覆盖：** 15+ 核心人物 | 20+ 核心机构

---

## 🔥 今日头条（Top 3）

1. **[重磅]** [标题] - @来源
   [简要描述]

2. **[动态]** [标题] - @来源
   [简要描述]

3. **[观点]** [标题] - @来源
   [简要描述]

---

## 🏢 机构动态

### OpenAI
- [动态 1]
- [动态 2]

### Google DeepMind
- [动态 1]

### Anthropic
- [动态 1]

### NVIDIA
- [动态 1]

### 其他
- [Meta/DeepSeek/阿里等动态]

---

## 👤 大佬观点

### Sam Altman (@sama)
- [观点/动态]

### Elon Musk (@elonmusk)
- [观点/动态]

### Andrej Karpathy (@karpathy)
- [技术分享/观点]

### Yann LeCun (@ylecun)
- [AGI 观点/评论]

### 其他
- [其他大佬的重要发言]

---

## 📈 趋势观察

- [今日 AI 圈热点话题]
- [技术方向变化]
- [投资/合作动向]

---

## 📅  upcoming

- [即将发布的产品/活动]
- [重要会议/截止日期]

---

*简报生成时间：HH:MM | 数据源：Twitter/X 核心账号*
```

## 实现方案

### 方案 A：Twitter API（推荐）

```python
import tweepy

client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def get_tweets(username, count=10):
    user = client.get_user(username=username)
    tweets = client.get_users_tweets(
        id=user.data.id,
        max_results=count,
        tweet_fields=['created_at', 'text', 'public_metrics'],
        exclude=['retweets', 'replies']
    )
    return tweets
```

### 方案 B：RSS/网页抓取（备选）

如果 Twitter API 受限，使用：
- Nitter 实例（Twitter 镜像）
- 各公司官方博客 RSS
- Hacker News AI 标签
- Reddit r/MachineLearning

### 方案 C：人工 curated（最低成本）

每日手动检查核心账号，整理重要动态。

## 注意事项

1. **时效性**：简报应在每日早晨 8-9 点生成
2. **简洁性**：每条动态不超过 2-3 句话
3. **重要性排序**：重磅新闻放前面
4. **来源标注**：每条都要标注@来源
5. **中文输出**：英文内容需翻译/摘要为中文
6. **不构成建议**：仅信息汇总，不做投资/技术建议

## 扩展功能（可选）

- 🔔 突发新闻即时推送（重大发布时）
- 📊 周度/月度汇总报告
- 🏷️ 按主题分类（模型/应用/投资/安全）
- 📈 影响力评分（追踪谁的声音最重要）
