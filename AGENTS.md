# Repository Guidelines

本文件是本项目的 AI Agent 总入口。完整规则按分类维护在 `.ai/` 目录；执行任务前应先阅读 `.ai/index.md`，再按任务类型读取对应规则。

## 基本约束

- 始终使用简体中文与用户沟通。
- `README.md` 暂时保持现状，除非用户明确要求，否则不要修改。
- 本项目使用 Uv 管理 Python 3.14 项目，优先使用 `uv` 执行同步、运行、测试和构建。
- `uv sync` 默认不必附加参数；若命令涉及远程请求，可先尝试设置 `http://127.0.0.1:7890` 作为系统 HTTP 代理环境。
- `version-checker.toml` 是核心配置文件，修改软件检测行为前必须先检查该文件中的现有条目。
- `data/` 是运行时生成 JSON 数据目录，数据量较大；除非用户明确要求分析生成结果，否则不要深度读取或遍历。
- `.gitignore` 不要主动修改；如发现规则需要调整，只提示用户建议变更项。

## 规则入口

- `.ai/index.md`：AI 规则索引和阅读顺序。
- `.ai/architecture/project-overview.md`：项目结构、运行链路和关键文件边界。
- `.ai/style/python-style.md`：Python 代码、注释、日志和测试风格。
- `.ai/workflow/development.md`：依赖兼容性检查、验证命令和 Windows 执行约束。
- `.ai/workflow/github-release-config.md`：GitHub Releases 软件配置生成规则。

## 常用命令

- `uv sync`
- `uv run version-checker inspect`
- `uv run pytest`
- `uv pip check`
- `uv build`

Windows PowerShell 下 `Makefile` 可能因 POSIX 命令不兼容失败；需要验证 `make` 时优先使用 Git Bash。
