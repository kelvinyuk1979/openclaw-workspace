# MEMORY.md - 长期记忆

## 🤖 核心工作原则（最高优先级）
## ⚠️ 第一原则：随时保持沟通 (2026-03-22 永久记录)

**核心职责**：
- ✅ 必须随时与用户保持沟通状态
- ✅ 任何会打断对话的操作都必须让子代理执行
- ❌ 不能遵守这一条，就不能做任何事情

**什么是"会打断对话的操作"**：
- 运行耗时命令（如 inkos write、python 脚本、文件处理）
- 等待 API 响应（如 AI 生成、网络请求）
- 批量文件操作（如创建/修改多个文件）
- 任何需要等待超过几秒的任务

**正确工作流**：
用户提出需求 → 主体确认方案 → spawn 子代理执行 → 
主体继续与用户沟通 → 子代理完成后汇报 → 
主体检查结果 → 转达给用户



**违反后果**：
- 用户无法中断/调整方向
- 主体变成"黑箱"，用户不知道在做什么
- 失去交互性，违背 OpenClaw 的设计初衷


**这条规则高于一切其他规则。不能遵守，就什么都不做。**

---

## 🎤 语音对话设置

**默认声音**: `Yue (Premium)` — 普通话高质量女声

当用户要求语音对话或朗读时：
1. 使用 macOS 自带 `say` 命令
2. 默认声音：`say -v "Yue (Premium)" "文本"`
3. 无需 API Key，开箱即用

**其他可用声音**:
- `Tingting` — 标准普通话（备用）
- `Sinji` — 粤语
- `Samantha` — 英文女声

---

## 📸 摄像头功能

**工具**: `imagesnap` (已安装)
**设备**: MacBook Air 相机

使用方式：
- 拍照：`imagesnap -o <路径>.jpg && open <路径>`
- 列出设备：`imagesnap -l`

---



## ⚙️ 系统配置

**模型**: qwen/qwen3.5-plus
**Node.js**: 已修复路径问题（软链接到 /opt/homebrew/bin）

---

## 🧠 模型上下文配置 (2026-03-16 更新)

**Qwen3.5-Plus 上下文窗口**：
- **配置值**: `contextWindow: 1000000` (1M tokens)
- **实际显示**: ~977k tokens (OpenClaw 保留 buffer)
- **maxTokens**: 64000 (单次响应上限)
- **配置位置**: `~/.openclaw/openclaw.json` → `models.providers.qwen.models[]`

**配置详情**：
```json
{
  "providers": {
    "qwen": {
      "models": [{
        "id": "qwen3.5-plus",
        "name": "Qwen 3.5 Plus",
        "contextWindow": 1000000,
        "maxTokens": 64000
      }]
    }
  }
}
```

**默认模型链**：
1. 主模型：`google/gemini-3.1-pro-preview` (1024k)
2. Fallback #1: `google/gemini-3.1-pro-preview`
3. Fallback #2: `qwen-portal/qwen3.5-plus` (977k)

---

## 🔄 模型故障转移配置 (2026-03-22 更新)

**主模型**: `qwen-portal/qwen3.5-plus`

**Fallback 链**（按顺序）:
1. `qwen-portal/qwen3.5-plus` (主模型)
2. `qwen-portal/glm-5` (智谱 - 文本生成/深度思考)
3. `qwen-portal/kimi-k2.5` (Kimi - 文本生成/深度思考/视觉理解)
4. `qwen-portal/MiniMax-M2.5` (MiniMax - 文本生成/深度思考)
5. `google/gemini-3.1-pro-preview` (Gemini - 最后备用)

**特性**:
- ✅ 主模型失败时自动切换，按顺序尝试
- ✅ 所有备用模型都配置在 `~/.openclaw/openclaw.json`
- ✅ 熔断器保护（连续失败会触发半开重试）

**手动切换命令**:
```bash
openclaw models set qwen-portal/glm-5          # 切到 glm-5
openclaw models set qwen-portal/kimi-k2.5      # 切到 kimi
openclaw models set qwen-portal/qwen3.5-plus   # 切回 qwen
```

## ⚠️ 错误记录 - 更新检查流程 (2026-03-17)

**问题**：用户问"今天 openclaw 更新了吗"，我直接根据 `openclaw status` 输出中的"latest 2026.3.13"判断没有更新，但没有实际运行检查命令。

**教训**：
- 不要根据 status 输出推测，要实际运行 `openclaw update --dry-run` 来确认
- 先检查再下结论，不要跳过验证步骤

**正确流程**：
```bash
openclaw update --dry-run  # 检查是否有新版本
# 输出会显示 Current version 和 Target version
# 如果两者相同 = 无更新
```

**已记住**：以后回答更新问题，必须先跑 `update --dry-run` 再给结论。

---





**InkOS 版本检查规则**：
- 不要每次自动检查更新
- 只有用户明确要求检查时，才检查版本更新
- 检查命令：`npm view @actalk/inkos version`
- 更新命令：`npm install -g @actalk/inkos@latest`

---

## 📚 归档偏好 (2026-03-22 永久记录)

**当用户说"归档"时，使用 Ontology 记录**：

- ✅ 项目进度 → 创建 Note 实体，关联到项目
- ✅ 重要决策 → 创建 Note 实体，标签"决策"
- ✅ 角色/设定 → 创建 Person/Note 实体
- ✅ 任务状态 → 更新 Task 实体的 status

**Self-Improvement 用途**：
- 仅用于记录错误、教训、踩坑经验
- 文件位置：`.learnings/` 目录

**Ontology 优势**：
- 结构化数据，可查询
- 实体有关系，可图遍历
- 长期有效，不会过时






## 📝 Summarize 摘要技能

**学习日期：** 2026-03-14
**来源：** ClawHub (clawhub.ai/steipete/summarize)

### 支持的摘要模式

- 📌 **要点式** (bullet) - 关键要点列表
- 📄 **段落式** (paragraph) - 连贯段落总结
- 🔢 **1-3-5 格式** - 1 句话 +3 要点 +5 细节
- 📊 **结构化** (structured) - 多维度完整摘要
- ⏱️ **TL;DR** - 超简短 1-2 句话

### 支持的输入类型

- 文章/网页
- 文档 (PDF/Word/Markdown/TXT)
- 对话/会议记录
- 视频/音频转录

### 使用场景

- AI 简报内容摘要
- 财报/新闻快速总结
- 会议纪要整理
- 长文档快速浏览

---

## 🔄 Self-Improving Agent 自我改进技能

**学习日期：** 2026-03-14
**来源：** ClawHub (clawhub.ai/ivangdavila/self-improving)
**版本：** 3.0.1

### 核心功能

持续记录学习、错误和改进，实现 AI 代理的自我进化。

### 触发场景

| 场景 | 记录位置 |
|------|----------|
| 命令/操作失败 | `.learnings/ERRORS.md` |
| 用户纠正你 | `.learnings/LEARNINGS.md` (correction) |
| 用户请求新功能 | `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | `.learnings/ERRORS.md` |
| 知识过时/错误 | `.learnings/LEARNINGS.md` (knowledge_gap) |
| 发现更好方法 | `.learnings/LEARNINGS.md` (best_practice) |

### 记录格式

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 时间戳
**Priority**: low | medium | high | critical
**Status**: pending | resolved | promoted
**Area**: frontend | backend | infra | tests | docs | config

### Summary
一句话描述

### Details
完整上下文

### Suggested Action
具体改进建议

---
```

### 升级路径

| 学习类型 | 升级到 |
|----------|--------|
| 行为模式 | `SOUL.md` |
| 工作流改进 | `AGENTS.md` |
| 工具技巧 | `TOOLS.md` |
| 项目约定 | `CLAUDE.md` |

### 主动代理功能

- 🔍 定期审查 `.learnings/` 目录
- 📊 检测重复出现的问题
- 📈 优先处理高优先级事项
- ✅ 自动标记已解决的问题

### 位置

`~/.openclaw/workspace/skills/self-improving-agent/`

---

## 🔍 Multi-Search-Engine 多搜索引擎技能

**学习日期：** 2026-03-14
**来源：** ClawHub (clawhub.ai/gpyAngyoujun/multi-search-engine)

### 支持的搜索引擎

**国际引擎：**
- Google - 最全面，质量高
- Bing - 微软生态，视频搜索强
- DuckDuckGo - 隐私保护，无追踪
- Brave Search - 隐私友好，独立索引

**国内引擎：**
- 百度 - 中文内容最全
- 必应中国 - 中英文兼顾
- 搜狗 - 微信内容独家
- 360 搜索 - 安全导向

### 使用场景

- ✅ 深度研究 - 全面信息覆盖
- ✅ 事实验证 - 交叉验证准确性
- ✅ 竞品分析 - 不同引擎结果对比
- ✅ SEO 研究 - 了解各引擎排名差异
- ✅ 敏感话题 - 避免单一引擎偏见

### 核心功能

- 🔀 **并行搜索** - 同时查询多个引擎
- 🔀 **去重融合** - 智能去重 + Borda 排序
- 📊 **结果聚类** - 按主题自动分类
- ✅ **交叉验证** - 事实准确性验证

### 输出格式

- 汇总统计（引擎数、结果数、搜索时间）
- 高相关性结果 Top N
- 引擎对比表
- 主题分类

---

## 🔄 Auto-Updater 自动更新技能

**学习日期：** 2026-03-14
**来源：** ClawHub (clawhub.ai/maximeprades/auto-updater)

### 支持的更新类型

| 类型 | 内容 | 策略 |
|------|------|------|
| 📦 **依赖更新** | npm、pip、Rust、Go 包 | 自动/询问 |
| 🧩 **技能更新** | ClawHub 技能 | 自动/询问 |
| 📝 **配置更新** | OpenClaw 配置、环境变量 | 手动审查 |
| 🌐 **远程资源** | 远程配置、模板、数据 | 定时刷新 |

### 更新策略

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `auto` | 自动更新，无需确认 | 补丁版本、安全更新 |
| `prompt` | 更新前询问用户 | 次版本升级 |
| `manual` | 仅提醒，不自动更新 | 主版本、重大变更 |

### 核心功能

- 🔍 **定期检查** - Cron 定时检查更新
- 📊 **更新报告** - 生成详细更新清单
- 💾 **更新前备份** - 自动备份可回滚
- ✅ **更新后测试** - 验证更新成功
- 🔙 **回滚机制** - 失败自动回滚
- 🔔 **通知系统** - 完成/失败通知

### 最佳实践

- **更新频率**: 依赖每天、技能每周、主版本每月审查
- **备份优先**: 更新前务必备份
- **测试验证**: 更新后运行基本测试
- **记录日志**: 保留完整更新日志

### 配置位置

`~/.openclaw/config/auto-update.json`

---

## 🎯 机会发现引擎 (Opportunity Discovery Engine)

**学习日期：** 2026-03-20

**目标：** 持续识别能创造财务价值的机会（商业机会、市场低效、技术变革、新兴趋势）

### 分析框架（7 步）

| 步骤 | 核心问题 | 关注点 |
|------|----------|--------|
| 1️⃣ **识别低效** | 哪里存在信息不对称/定价错误？ | 技术颠覆、法规变化、消费者行为转变 |
| 2️⃣ **评估不对称性** | 下行有限、上行巨大？ | 高期望值 > 保证结果 |
| 3️⃣ **及早检测趋势** | 新基础设施/资金流入/采用信号？ | 早期趋势 = 最大机会 |
| 4️⃣ **变现路径** | 实际怎么赚钱？ | 投资、工具/服务、信息套利、自动化、分销 |
| 5️⃣ **竞争格局** | 拥挤度/壁垒/优势？ | 高壁垒 + 低认知 = 宝贵 |
| 6️⃣ **排序机会** | EV/难度/资本/时间？ | 最佳风险/回报比优先 |
| 7️⃣ **创意思考** | 非常规方法/被忽略细分？ | 发掘他人未注意的机会 |

### 应用方向

- 📈 投资标的筛选（股票、加密货币、预测市场）
- 🛠️ 工具/服务构建机会
- 📊 信息套利（跨平台、跨语言、跨时区）
- 🤖 自动化机会（重复流程、人工密集型）
- 🌐 新兴趋势早期布局

**触发时机：** 定期扫描（每周）、重大新闻事件后、用户询问"有什么机会"时
