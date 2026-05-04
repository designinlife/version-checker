# 开发与验证工作流

## 环境管理

- 本项目采用 Uv 管理 Python 3.14。
- 优先使用 `uv` 命令，不要默认使用裸 `python`、裸 `pip` 或其他包管理器。
- `uv sync` 默认不必附加参数。
- 常用命令：
  - `uv sync`
  - `uv run version-checker inspect`
  - `uv run pytest`
  - `uv pip check`
  - `uv build`

## 远程请求与代理

- 执行涉及远程请求的 `uv` 命令前，如果网络访问不稳定，可先尝试在当前 shell 进程设置 HTTP 代理环境变量为 `http://127.0.0.1:7890`。
- PowerShell 当前进程示例：

```powershell
$env:HTTP_PROXY = 'http://127.0.0.1:7890'
$env:HTTPS_PROXY = 'http://127.0.0.1:7890'
uv sync
```

- 代理只作为网络访问辅助手段；不要把代理地址写入项目配置、提交到仓库或固化到脚本中。

## 依赖兼容性检查

当 `pyproject.toml` 依赖版本发生变化时，按以下顺序检查：

1. `uv run python --version`，确认当前解释器为 Python 3.14。
2. `uv sync`，确认依赖可解析并安装。
3. `uv pip check`，确认已安装包之间无依赖冲突。
4. `uv tree --depth 2`，必要时查看实际解析版本。
5. `uv run pytest`，确认项目测试状态。

如果 `uv sync` 输出间接依赖的旧式版本声明规范化警告，但命令退出码为 0 且 `uv pip check` 通过，应记录为上游元数据警告，而不是直接认定依赖不兼容。

## 当前已知验证状态

截至最近一次检查：

- `uv run python --version`：Python 3.14.4。
- `uv sync`：通过。
- `uv pip check`：通过，52 个已安装包兼容。
- `uv tree --depth 2`：可正常解析依赖树。
- `uv run pytest`：通过，10 个测试全部通过。

验证结论必须来自当前轮 fresh command output；不要沿用旧状态。

## Windows 命令约束

- 普通 CLI 优先直接执行，例如 `rtk rg`、`rtk fd`、`rtk bat`、`rtk git`、`rtk uv`。
- 只有命令依赖 PowerShell 语法、变量、条件判断或脚本执行时，才使用 `pwsh`。
- `Makefile` 中存在 `rm -rf` 等 POSIX 语义；Windows PowerShell 下直接运行 `make` 可能不兼容。
- 需要验证 `make` 时，优先使用 Git Bash，并明确工作目录。

## 生成目录处理

- `data/` 是运行时生成 JSON 数据目录，数据量较大。
- 默认不要深度读取、全文搜索或遍历 `data/`。
- 搜索项目代码时排除 `data/`、`.venv/`、`dist/`、`build/`、`__pycache__/`。
- 只有当用户明确要求核查生成结果时，才读取 `data/` 中的具体目标文件。

## 文档约束

- `README.md` 更新由用户负责，AI 不主动干预；如发现 README 可能需要同步，只在回复中提示用户。
- AI 规则写入 `.ai/`，根目录入口文件只保留索引和摘要。
- 修改配置键、环境变量或运行方式时，不主动修改 README；必要时提示用户需要自行同步 README。
- `.gitignore` 不要主动修改；如果发现需要新增或删除忽略规则，只在回复中提示用户建议调整内容。
- `docs/` 目录明确不提交；不要把必须随仓库保留的长期规则或交付物写入 `docs/`。用户明确要求本地过程材料时，可以写入 `docs/`，但必须说明其不会被 Git 跟踪。
