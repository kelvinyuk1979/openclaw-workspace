## [LRN-20260312-001] OpenClaw Model Fallback and Custom API Config

**Logged**: 2026-03-12T07:12:30Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
OpenClaw config validation rejects the `fallback` key in `agents.defaults.model`, causing gateway restart to fail. Custom providers need `auth` profile entries.

### Details
When attempting to set up an automatic fallback model in `~/.openclaw/openclaw.json` using `agents.defaults.model.fallback`, OpenClaw 2026.3.11's config linter rejected the file with `agents.defaults.model: Invalid input` and aborted the gateway restart.
Additionally, when adding a custom OpenAI-compatible provider (like `dashscope`), an explicit entry in `auth.profiles` (e.g., `"dashscope:default": { "provider": "dashscope", "mode": "api_key" }`) is required for it to appear properly in the UI.

### Suggested Action
1. Do NOT use `fallback` in `agents.defaults.model`.
2. To provide model switching, create a bash script (e.g., `switch-model.sh`) that modifies `agents.defaults.model.primary` using Python JSON parsing, then instruct the user to run `openclaw gateway restart`.
3. When adding custom providers to `models.providers`, always add a corresponding entry to `auth.profiles`.

### Metadata
- Source: error
- Related Files: ~/.openclaw/openclaw.json
- Tags: openclaw, config, models, fallback

---
