# Claude 项目入口

本文件是兼容入口，避免在多个根级 AI 文档中重复维护完整规则。

请优先阅读：

1. `AGENTS.md`
2. `.ai/index.md`
3. 与当前任务相关的 `.ai/architecture/`、`.ai/style/`、`.ai/workflow/` 规则

关键约束：

- 使用简体中文沟通。
- `README.md` 暂时保持现状，不要主动修改。
- 本项目采用 Uv + Python 3.14。
- `uv sync` 默认不必附加参数；涉及远程请求时，可先尝试设置 `http://127.0.0.1:7890` 作为系统 HTTP 代理环境。
- `version-checker.toml` 是核心配置文件。
- `data/` 是运行时生成 JSON 数据目录，除非任务明确要求，否则不要深度读取。
- `.gitignore` 不要主动修改；如需调整，仅向用户提示建议规则。
