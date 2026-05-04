# AI 规则索引

本目录集中维护 `version-checker` 项目的 AI Agent 约束。根目录 `AGENTS.md` 和 `CLAUDE.md` 只作为入口和兼容说明，长期规则以本目录为主。

## 阅读顺序

1. 先读 `AGENTS.md`，确认项目级硬性约束。
2. 再读本文，确认规则分类。
3. 根据任务类型读取下列文档：
   - 架构、配置、目录边界：`architecture/project-overview.md`
   - Python 代码修改、注释、日志、测试：`style/python-style.md`
   - 依赖、验证、Windows 命令、生成目录处理：`workflow/development.md`
   - 新增或更新软件检测配置：`workflow/add-software.md`

## 项目硬性边界

- `README.md` 更新由用户负责，AI 不主动干预。
- `version-checker.toml` 是核心配置文件；涉及软件版本检测、下载地址、解析器选择、过滤条件时，先检查该文件。
- `data/` 是运行时生成 JSON 数据目录，数据量较大；默认不要深度读取、全文搜索或遍历。
- 本项目使用 Uv 管理 Python 3.14；不要按 Poetry、PDM 或裸 `pip` 项目处理。
- `uv sync` 默认不必附加参数；远程请求不畅时，可先在当前 shell 进程设置 `http://127.0.0.1:7890` 作为 HTTP 代理环境变量。
- `.gitignore` 不要主动修改；发现忽略规则需要调整时，只提示用户建议项。
- `docs/` 目录明确不提交；不要把必须提交的长期规则或交付物写入 `docs/`。
- 日志、异常消息和脚本输出使用英文；面向用户的文档和代码注释使用中文。

## 维护规则

- 新增长期 AI 规则时，优先放入 `.ai/architecture/`、`.ai/style/` 或 `.ai/workflow/`。
- 新增规则文件后必须更新本索引。
- 一次性计划、评审或验证记录不要写入本目录。`docs/` 不提交，仅适合用户明确要求的本地过程材料；需要随仓库保留的 AI 规则应写入 `.ai/`。
