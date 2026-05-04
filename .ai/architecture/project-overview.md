# 项目结构与运行链路

## 项目定位

`version-checker` 是用于检测软件最新版本并生成 JSON 数据的 Python CLI 项目。项目入口、配置模型、解析器和生成数据之间存在明确链路，修改前应先确认真实调用路径。

## 关键目录

- `src/app/cli.py`：Click 命令入口，加载环境变量，读取 `version-checker.toml`，注册子命令。
- `src/app/core/`：通用配置模型、HTTP、GitHub、通知和版本工具。
- `src/app/parser/`：软件源解析器。新增解析器时，模块名应与配置中的 `parser` 值对应，短横线在动态导入时会转换为下划线。
- `src/app/commands/`：CLI 子命令，例如 `inspect`、`combine`、`skopeo`、`jbp`。
- `src/app/link/`：特定链接或外部系统辅助逻辑。
- `tests/`：测试目录，当前测试由 `pytest` 执行。
- `data/`：运行时生成 JSON 数据目录。默认不要深度读取或遍历。
- `.agents/skills/`：项目内技能目录，目前包含 GitHub Releases 配置生成技能。

## 核心配置

`version-checker.toml` 是核心配置文件。常见配置字段包括：

- `name`：软件条目名称。
- `repo`：GitHub、Gitea、Codeberg 等仓库标识。
- `url`：软件主页或仓库地址。
- `parser`：解析器类型；未指定时，GitHub 配置模型默认使用 `gh`。
- `pattern`：匹配版本来源的正则，GitHub Release 场景匹配 Tag 名。
- `release`：GitHub 类配置中表示使用 Releases API，而不是 Tags API。
- `download_urls`：生成结果中的下载地址模板。

修改配置前必须先检查是否已存在同一软件条目，优先按 `repo` 判断，其次按 `name` 判断，避免重复新增。

## Inspect 链路

1. `src/app/cli.py` 读取 `version-checker.toml`。
2. `AppSetting` 使用 Pydantic 校验 `[[softwares]]` 配置。
3. `version-checker inspect` 遍历启用的软件条目。
4. `src/app/commands/inspect.py` 根据 `parser` 动态加载 `src/app/parser/<parser>.py`。
5. 解析器处理版本并写入运行时 JSON 数据。
6. `inspect` 结束后调用 `combine` 合并输出。

## 边界要求

- 不要把 `data/` 当作源配置目录；它是生成结果目录。
- 不要在未检查 `version-checker.toml` 的情况下新增软件配置。
- 不要把 README 当作 AI 规则主维护位置；AI 规则维护在 `.ai/`。
- `README.md` 更新由用户负责，AI 不主动干预；如发现 README 可能需要同步，只在回复中提示用户。
- `docs/` 目录明确不提交，不要把必须随仓库保留的规则、计划或交付物写入 `docs/`。
