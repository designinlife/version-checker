# Python 代码风格

## 基本风格

- 项目使用 Python 3.14。
- 使用 4 空格缩进。
- 模块、函数、变量使用 `snake_case`。
- 类名使用 `PascalCase`。
- 解析器模块按目标软件或来源命名，例如 `github_desktop.py`。
- 新增 CLI 命令放入 `src/app/commands/`，并在 `src/app/cli.py` 注册。

## 类型与配置

- 配置结构优先使用 `src/app/core/config.py` 中的 Pydantic 模型表达。
- 新增 `parser` 类型时，应补充对应的配置模型，并加入 `AppSetting.softwares` 的联合类型。
- `version-checker.toml` 的字段语义要与配置模型保持一致，不要只改 TOML 而不更新模型。

## 注释与日志

- 代码注释使用中文，只解释函数、类型或复杂逻辑，不写显而易见的描述。
- 运行时日志、异常消息、脚本输出使用专业英文，保持简洁清晰。
- 不要把面向用户的中文说明写入运行时日志。

## 测试

- 测试文件使用 `*_test.py` 命名。
- 新增解析器或配置模型时，优先补充版本解析、配置读取、网络响应解析和边界输入测试。
- 涉及真实网络的测试要控制范围；优先使用固定样例或最小联调。
- 当前 `uv run pytest` 在收集阶段会因既有 `tests/parser_test.py` 中 `from parser import Parser` 导入不存在的顶层模块而失败。判断依赖兼容性时不要把该错误误判为依赖版本冲突。

## 依赖使用

- 新依赖必须写入 `pyproject.toml`。
- 项目使用 Uv，不要新增 Poetry、PDM 或 requirements 作为主依赖入口。
- 依赖版本调整后至少运行：
  - `uv sync`
  - `uv pip check`
  - `uv run pytest`
