---
name: auto-updater
description: 自动更新工具，检查并更新项目依赖、技能、配置文件等，保持系统最新状态。
emoji: 🔄
---

# Auto-Updater - 自动更新技能

## 功能概述

自动检查并更新各类资源，确保系统和项目保持最新状态，减少手动维护成本。

## 支持的更新类型

### 📦 项目依赖更新

| 类型 | 工具 | 命令 |
|------|------|------|
| npm/Node.js | npm-check-updates | `ncu -u && npm install` |
| Python | pip-review | `pip-review --auto` |
| Python | pipx | `pipx upgrade-all` |
| Rust | cargo | `cargo update` |
| Go | go get | `go get -u ./...` |

### 🧩 OpenClaw 技能更新

| 操作 | 命令 |
|------|------|
| 检查更新 | `clawhub list` |
| 更新全部 | `clawhub sync --all` |
| 更新单个 | `clawhub update <skill-name>` |
| 查看可用更新 | `clawhub outdated` |

### 📝 配置文件更新

| 配置类型 | 检查内容 |
|----------|----------|
| OpenClaw 配置 | 版本兼容性、新特性 |
| 环境变量 | 过期/废弃的变量 |
| API 密钥 | 过期密钥提醒 |
| Cron 任务 | 失效的任务配置 |

### 🌐 远程资源更新

| 资源类型 | 更新内容 |
|----------|----------|
| 远程配置 | 从 URL 拉取最新配置 |
| 模板文件 | 更新项目模板 |
| 数据文件 | 刷新缓存数据 |

## 使用场景

### ✅ 适合自动更新的情况

- **依赖包** - npm、pip 等包管理
- **技能库** - ClawHub 技能更新
- **配置文件** - 兼容性配置
- **数据缓存** - 定期刷新的数据
- **文档模板** - 标准文档格式

### ⚠️ 需要确认的更新

- **主版本升级** - 可能有破坏性变更
- **核心配置** - 影响系统行为
- **安全凭证** - API 密钥、密码
- **数据库结构** - Schema 变更

### ❌ 不应自动更新

- **生产环境配置** - 需人工审核
- **自定义代码** - 可能覆盖用户修改
- **敏感数据** - 凭证、密钥
- **未测试的更新** - 稳定性未知

## 使用方法

### 基础更新

```python
# 检查所有可更新项
auto_updater.check_all()

# 更新指定类型
auto_updater.update(type="dependencies")
auto_updater.update(type="skills")
auto_updater.update(type="config")

# 更新全部
auto_updater.update_all()
```

### 定时更新

```yaml
# Cron 配置示例
auto_update:
  schedule: "0 3 * * *"  # 每天凌晨 3 点
  types:
    - dependencies
    - skills
  notify: true
  auto_commit: false
```

### 更新策略

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| `auto` | 自动更新，无需确认 | 补丁版本、安全更新 |
| `prompt` | 更新前询问用户 | 次版本升级 |
| `manual` | 仅提醒，不自动更新 | 主版本、重大变更 |

## 输出格式

### 检查报告

```markdown
## 🔄 更新检查报告

**检查时间**: 2026-03-14 16:00:00
**检查范围**: 依赖、技能、配置

### 📦 依赖更新 (5 个可用)

| 包名 | 当前 | 最新 | 类型 | 建议 |
|------|------|------|------|------|
| openclaw | 1.2.0 | 1.3.0 | minor | ✅ 更新 |
| requests | 2.28.0 | 2.31.0 | minor | ✅ 更新 |
| numpy | 1.23.0 | 2.0.0 | major | ⚠️ 审查 |

### 🧩 技能更新 (3 个可用)

| 技能 | 当前版本 | 最新版本 | 变更 |
|------|----------|----------|------|
| weather | 1.0.0 | 1.1.0 | 新增功能 |
| summarize | 2.0.0 | 2.0.1 | Bug 修复 |

### 📝 配置更新

- ✅ 配置文件最新
- ℹ️ 发现 1 个推荐配置项

### 汇总

- **可安全更新**: 6
- **需要审查**: 1
- **已是最新**: 12
```

### 更新日志

```markdown
## 🔄 更新日志 - 2026-03-14

### 已更新

1. **openclaw** `1.2.0` → `1.3.0`
   - 新增功能 X
   - 性能提升 Y%

2. **weather-skill** `1.0.0` → `1.1.0`
   - 支持更多城市
   - 修复已知问题

### 跳过

1. **numpy** `1.23.0` → `2.0.0`
   - 原因：主版本升级，需要兼容性测试

### 下次检查

- 计划时间：2026-03-15 03:00:00
```

## 实现方案

### npm/Node.js 依赖更新

```python
import subprocess
import json

def check_npm_updates():
    """检查 npm 依赖更新"""
    # 使用 npm-check-updates
    result = subprocess.run(
        ['npx', 'npm-check-updates', '--json'],
        capture_output=True,
        text=True
    )
    updates = json.loads(result.stdout)
    return updates

def update_npm_dependencies():
    """更新 npm 依赖"""
    subprocess.run(['npx', 'ncu', '-u'], check=True)
    subprocess.run(['npm', 'install'], check=True)
```

### Python 依赖更新

```python
import subprocess

def check_pip_updates():
    """检查 pip 依赖更新"""
    result = subprocess.run(
        ['pip', 'list', '--outdated', '--format=json'],
        capture_output=True,
        text=True
    )
    outdated = json.loads(result.stdout)
    return outdated

def update_pip_dependencies():
    """更新 pip 依赖"""
    subprocess.run(['pip-review', '--auto'], check=True)
```

### ClawHub 技能更新

```python
def check_skill_updates():
    """检查 ClawHub 技能更新"""
    result = subprocess.run(
        ['clawhub', 'outdated'],
        capture_output=True,
        text=True
    )
    return parse_outdated_skills(result.stdout)

def update_skills(skill_names=None):
    """更新技能"""
    if skill_names:
        for skill in skill_names:
            subprocess.run(['clawhub', 'update', skill], check=True)
    else:
        subprocess.run(['clawhub', 'sync', '--all'], check=True)
```

### 配置文件更新

```python
import requests
import hashlib

def check_config_updates():
    """检查配置文件更新"""
    config_files = [
        {
            'local': '~/.openclaw/config.json',
            'remote': 'https://example.com/config-template.json',
            'hash_file': '~/.openclaw/.config-hash'
        }
    ]
    
    updates = []
    for config in config_files:
        if has_remote_update(config):
            updates.append(config)
    
    return updates

def has_remote_update(config):
    """检查是否有远程更新"""
    local_hash = get_file_hash(config['local'])
    stored_hash = get_stored_hash(config['hash_file'])
    return local_hash != stored_hash
```

## 高级功能

### 1. 智能更新策略

```python
def determine_update_strategy(package_info):
    """
    根据更新类型决定策略
    """
    current = package_info['current_version']
    latest = package_info['latest_version']
    
    current_major = int(current.split('.')[0])
    latest_major = int(latest.split('.')[0])
    
    if current_major != latest_major:
        return 'manual'  # 主版本 - 手动审查
    elif current.split('.')[1] != latest.split('.')[1]:
        return 'prompt'  # 次版本 - 询问用户
    else:
        return 'auto'  # 补丁版本 - 自动更新
```

### 2. 更新前备份

```python
import shutil
from datetime import datetime

def backup_before_update(paths):
    """更新前备份"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'.backups/update_{timestamp}'
    
    os.makedirs(backup_dir, exist_ok=True)
    
    for path in paths:
        if os.path.exists(path):
            shutil.copy2(path, backup_dir)
    
    return backup_dir
```

### 3. 回滚机制

```python
def rollback_update(backup_dir):
    """回滚更新"""
    if not os.path.exists(backup_dir):
        raise Exception("备份目录不存在")
    
    # 恢复备份文件
    for file in os.listdir(backup_dir):
        src = os.path.join(backup_dir, file)
        dst = file  # 恢复到原位置
        shutil.copy2(src, dst)
    
    return True
```

### 4. 更新测试

```python
def test_after_update(components):
    """更新后测试"""
    results = {}
    
    for component in components:
        try:
            # 运行组件的基本测试
            test_result = run_component_test(component)
            results[component] = {
                'status': 'passed' if test_result else 'failed',
                'details': test_result
            }
        except Exception as e:
            results[component] = {
                'status': 'error',
                'error': str(e)
            }
    
    return results
```

### 5. 通知系统

```python
def send_update_notification(summary):
    """发送更新通知"""
    message = f"""
## 🔄 更新完成通知

**时间**: {summary['timestamp']}
**更新内容**:
- 依赖：{summary['dependencies_updated']} 个
- 技能：{summary['skills_updated']} 个
- 配置：{summary['config_updated']} 个

**状态**: {'✅ 成功' if summary['success'] else '⚠️ 部分失败'}

查看详情：{summary['log_file']}
"""
    
    # 发送通知（根据配置选择渠道）
    if config.get('notify_email'):
        send_email(message)
    if config.get('notify_chat'):
        send_chat_message(message)
```

## 集成示例

### 与 OpenClaw 集成

```python
# ~/.openclaw/workspace/scripts/auto-update.py

def openclaw_auto_update():
    """OpenClaw 自动更新"""
    
    # 1. 检查 OpenClaw 版本
    current_version = get_openclaw_version()
    latest_version = check_latest_version()
    
    # 2. 检查技能更新
    skill_updates = check_skill_updates()
    
    # 3. 检查配置更新
    config_updates = check_config_updates()
    
    # 4. 生成报告
    report = generate_update_report(
        current_version,
        latest_version,
        skill_updates,
        config_updates
    )
    
    # 5. 根据策略执行更新
    if config.get('auto_update', False):
        execute_updates(report['safe_updates'])
    
    return report
```

### Cron 定时任务

```yaml
# ~/.openclaw/cron/auto-update.json

{
  "name": "自动更新检查",
  "schedule": {
    "kind": "cron",
    "expr": "0 3 * * *",  # 每天凌晨 3 点
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "运行自动更新检查：cd ~/.openclaw/workspace && python3 scripts/auto-update.py，然后生成报告发送给用户。",
    "model": "dashscope/qwen3.5-plus",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce"
  },
  "sessionTarget": "isolated"
}
```

## 配置示例

### 配置文件 (~/.openclaw/config/auto-update.json)

```json
{
  "enabled": true,
  "schedule": "0 3 * * *",
  "update_types": {
    "dependencies": {
      "enabled": true,
      "strategy": "auto",
      "exclude": ["critical-package-1", "critical-package-2"],
      "include_dev": false
    },
    "skills": {
      "enabled": true,
      "strategy": "prompt",
      "auto_backup": true
    },
    "config": {
      "enabled": true,
      "strategy": "manual",
      "remote_sources": []
    }
  },
  "notifications": {
    "on_completion": true,
    "on_error": true,
    "channel": "chat"
  },
  "backup": {
    "enabled": true,
    "retention_days": 7,
    "directory": ".backups"
  },
  "rollback": {
    "auto_rollback_on_failure": true,
    "test_after_update": true
  }
}
```

## 最佳实践

### 1. 更新频率

| 类型 | 建议频率 |
|------|----------|
| 安全补丁 | 立即 |
| 依赖补丁 | 每天 |
| 技能更新 | 每周 |
| 主版本升级 | 每月审查 |

### 2. 测试策略

```yaml
test_phases:
  - name: "更新前测试"
    run_before: true
    tests: ["basic", "critical_path"]
  
  - name: "更新后测试"
    run_after: true
    tests: ["basic", "integration", "regression"]
  
  - name: "回滚测试"
    run_on_failure: true
    tests: ["rollback_verification"]
```

### 3. 版本锁定

```json
{
  "lock_file": "package-lock.json",
  "auto_update_lock": false,
  "review_major_updates": true
}
```

## 注意事项

1. **备份优先** - 更新前务必备份
2. **测试验证** - 更新后运行基本测试
3. **渐进更新** - 不要一次更新太多
4. **记录日志** - 保留完整更新日志
5. **回滚准备** - 确保可以随时回滚
6. **通知用户** - 重要更新及时通知

## 扩展方向

- 🤖 AI 辅助更新决策
- 📊 更新影响分析
- 🔔 多渠道通知（邮件、Slack、微信）
- 📈 更新统计和报告
- 🧪 自动化回归测试
