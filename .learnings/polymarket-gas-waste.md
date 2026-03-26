## [LRN-20260325-001] Polymarket Gas 费浪费

**Logged**: 2026-03-25T23:30:00+08:00
**Priority**: high
**Status**: pending
**Area**: quant-trading

### Summary
Polymarket 测试未做 dry-run 直接实盘，导致 2 个 POL（约¥3）Gas 费浪费，交易未执行成功。

### Details

**背景**：
- Polymarket 自动交易系统首次测试
- 钱包充值：2 POL（Gas）+ 1 USDT（后兑换为 USDC）
- 目标：测试 $1 USDC 小额下单

**经过**：
1. ✅ 创建 API Credentials（成功）
2. ✅ USDT → USDC 兑换（成功，消耗 ~0.02 POL Gas）
3. ✅ Approve USDC for Polymarket（成功，消耗 ~0.01 POL Gas）
4. ❌ 执行下单（失败，py-clob-client 签名报错）

**结果**：
- 2 个 POL 全部用作 Gas 费
- USDC 兑换后未使用
- 交易未执行，测试失败

### Root Cause

1. **没有 dry-run 流程** — 脚本直接执行实盘，没有模拟模式
2. **SDK 未提前验证** — py-clob-client 的签名流程没在测试环境验证
3. **急于求成** — 想一次性跑通，忽略了分步验证

### Suggested Action

1. ✅ 创建 dry-run 测试脚本（`polymarket_dry_run.py`）
2. ✅ 测试流程分 6 步，逐步验证
3. ✅ 所有测试通过后才能切换到实盘
4. ⏳ 等待用户充值 POL+USDC 后执行 dry-run
5. ⏳ Dry-run 通过后再执行实盘交易

### Lesson Learned

**链上测试黄金法则**：
1. Dry-run 优先 — 任何实盘操作前必须先模拟
2. 小额验证 — 第一次用新 SDK/新流程，用最小金额测试
3. 分步执行 — Approve、Swap、Order 分开测试，不要一次性跑完
4. Gas 预算 — 提前计算 Gas 成本，预留足够余额

---

**相关文件**：
- `/Users/kelvin/.openclaw/workspace/scripts/polymarket_dry_run.py`
- `/Users/kelvin/.openclaw/workspace/polymarket-trading-system/trader.py`

**涉及金额**：2 POL（约¥3）
