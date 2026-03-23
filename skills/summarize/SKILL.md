---
name: summarize
description: 智能文本摘要工具，支持文章、文档、会议记录、对话等多种内容的快速总结。
emoji: 📝
---

# Summarize - 智能摘要技能

## 功能概述

快速生成各种文本内容的高质量摘要，支持多种摘要模式和长度。

## 支持的输入类型

### 1. 文章/网页摘要
- 新闻文章
- 博客文章
- 技术文档
- 研究报告
- 网页内容

### 2. 文档摘要
- PDF 文档
- Word 文档
- Markdown 文件
- 文本文件

### 3. 对话/会议摘要
- 会议记录
- 对话转录
- 聊天记录
- 访谈内容

### 4. 视频/音频转录摘要
- YouTube 视频字幕
- 播客转录
- 会议录音转录

## 摘要模式

### 📌 要点式摘要（Bullet Summary）
提取关键要点，适合快速浏览。

```markdown
## 核心要点

- 要点 1
- 要点 2
- 要点 3
```

### 📄 段落式摘要（Paragraph Summary）
连贯的段落总结，适合阅读理解。

```markdown
## 摘要

[连贯的摘要段落，200-300 字]
```

### 🔢 数字摘要（1-3-5 格式）
- 1 句话总结
- 3 个核心要点
- 5 个关键细节

### 📊 结构化摘要（Structured Summary）
包含多个维度的完整摘要。

```markdown
## 📝 [标题] 摘要

### 一句话总结
[1 句话核心内容]

### 核心要点
- 要点 1
- 要点 2
- 要点 3

### 关键数据/事实
- 数据 1
- 数据 2

### 行动建议/下一步
- 建议 1
- 建议 2

### 相关方/人物
- [相关方 1]
- [相关方 2]
```

### ⏱️ TL;DR（Too Long; Didn't Read）
超简短摘要，1-2 句话。

## 使用方法

### 基础用法

```python
# 文本摘要
summarize(text, mode="bullet", length="medium")

# URL 摘要
summarize_url(url, mode="structured")

# 文档摘要
summarize_file(filepath, mode="paragraph")
```

### 参数说明

| 参数 | 选项 | 说明 |
|------|------|------|
| mode | bullet/paragraph/structured/tldr/135 | 摘要模式 |
| length | short/medium/long | 摘要长度 |
| language | zh/en/auto | 输出语言 |
| focus | general/technical/financial/etc | 关注领域 |

## 输出格式示例

### 新闻文章摘要

```markdown
## 📰 [文章标题] 摘要

### TL;DR
[1 句话总结]

### 核心要点
- **要点 1**: [描述]
- **要点 2**: [描述]
- **要点 3**: [描述]

### 关键信息
- 📅 时间：[日期]
- 📍 地点：[地点]
- 👥 人物：[相关方]

### 影响/意义
[简要说明]
```

### 技术文档摘要

```markdown
## 📚 [文档标题] 技术摘要

### 概述
[技术/产品的简要描述]

### 核心特性
- 特性 1
- 特性 2
- 特性 3

### 技术细节
- [关键参数/规格]
- [兼容性信息]
- [性能数据]

### 使用场景
- 场景 1
- 场景 2

### 相关链接
- [文档链接]
- [GitHub 仓库]
```

### 会议记录摘要

```markdown
## 📋 会议纪要摘要

### 会议信息
- 📅 日期：YYYY-MM-DD
- 👥 参会人：[名单]
- 🎯 主题：[会议主题]

### 核心讨论
- 议题 1：[讨论要点]
- 议题 2：[讨论要点]

### 决策事项
- ✅ [决策 1]
- ✅ [决策 2]

### 行动项（Action Items）
- [ ] [任务 1] - @负责人 - 截止日期
- [ ] [任务 2] - @负责人 - 截止日期

### 下次会议
- 📅 时间：[日期]
- 📍 地点：[地点]
```

## 最佳实践

### 1. 摘要长度选择

| 内容类型 | 推荐长度 | 模式 |
|----------|----------|------|
| 新闻文章 | short | bullet/tldr |
| 技术文档 | medium | structured |
| 研究报告 | long | structured/paragraph |
| 会议记录 | medium | structured |
| 对话转录 | medium | bullet |

### 2. 质量检查

- ✅ 保留核心信息
- ✅ 去除冗余细节
- ✅ 保持客观中立
- ✅ 标注关键数据
- ✅ 包含行动项（如适用）

### 3. 避免的问题

- ❌ 丢失关键上下文
- ❌ 添加主观判断
- ❌ 过度简化复杂内容
- ❌ 忽略重要限定条件

## 高级功能

### 多文档对比摘要

```markdown
## 📊 多文档对比摘要

### 文档 A
[摘要内容]

### 文档 B
[摘要内容]

### 共同点
- [共同点 1]
- [共同点 2]

### 差异点
- [差异 1]
- [差异 2]
```

### 系列内容摘要

对系列文章/视频/播客进行整体摘要。

### 时间线摘要

按时间顺序整理事件发展。

## 集成示例

### 与 AI 简报集成

```python
# 在 AI 简报中使用摘要
def generate_ai_brief():
    tweets = collect_ai_tweets()
    for tweet in tweets:
        if len(tweet.text) > 280:
            summary = summarize(tweet.text, mode="tldr")
            add_to_brief(summary)
```

### 与股票分析集成

```python
# 摘要财报/新闻
def analyze_stock_news(news_articles):
    for article in news_articles:
        summary = summarize(article, mode="bullet", focus="financial")
        add_to_stock_report(summary)
```

## 注意事项

1. **准确性优先**：摘要应忠实于原文，不曲解原意
2. **标注来源**：始终保留原始来源信息
3. **敏感信息**：注意过滤隐私/敏感内容
4. **语言适配**：根据输入语言自动选择输出语言
5. **专业术语**：保留关键专业术语，必要时添加解释

## 扩展方向

- 🔗 自动提取相关链接
- 📈 情感分析集成
- 🏷️ 自动标签生成
- 📊 数据可视化摘要
- 🌐 多语言摘要
