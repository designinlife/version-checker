# 软件配置生成工作流

当用户要求新增软件配置、更新已有软件配置、从软件链接生成 `version-checker.toml` 片段、检查 GitHub Releases/Tags、筛选 Windows/Linux amd64 下载链接、用 CSS Selector/XPath 分析非 GitHub 下载页，或更新 README 的 `Supported software list` 表格时，必须使用项目技能：

- `.agents/skills/version-checker-add-software/SKILL.md`

## 触发场景

- `@version-checker-add-software 软件链接`
- `@技能 GitHub 仓库地址`
- 生成或更新 `[[softwares]]` 配置。
- 新增软件下载检测配置。
- 检查 Release 资产、Tag 版本、下载链接、重定向和真实保存文件名。
- 分析非 GitHub 下载页的真实下载链接。
- 更新 README 的 `Supported software list` 表格。

## 基本流程

1. 先检查 `version-checker.toml` 是否已有相同软件条目。
2. 优先按 `repo` 判断重复，其次按 `url`，最后按 `name`。
3. 判断链接类型：
   - GitHub 仓库优先检查 Releases，Tag 版本次之。
   - 非 GitHub 项目优先尝试当前已有 parser；必要时用 CSS Selector/XPath 分析真实下载链接。
4. 先生成 `test.toml` 并做目标条目的最小验证。
5. 验证通过后再同步 `version-checker.toml`。
6. 若正式配置变更会影响生成的 `data/*.json` 输出，同步检查并更新 `README.md` 的 `Supported software list` 表格。
7. 更新正式配置后不要主动提交 Git，由用户决定提交时机。

## GitHub 规则摘要

- 必须基于 GitHub API 或真实页面信息，不凭记忆猜测。
- 优先使用 Releases 中的真实资产；没有有效 Release 时再看 Tags。
- `pattern` 匹配 Release/Tag 名，不匹配资产文件名。
- 默认捕获 Windows/Linux 的 `amd64`、`x64`、`x86_64` 资产。
- 默认排除 arm、macOS、checksum、signature、SBOM 等非目标资产。
- 默认加入 `Source code (tar.gz)`，并放在 `download_urls` 最后。

## 非 GitHub 规则摘要

- 先跟随重定向，确认最终 URL、HTTP status code 和 content-type。
- HTML 页面可用 CSS Selector/XPath 查找真实下载链接，但落到 TOML 前必须确认当前项目是否支持对应 parser。
- 当前模型不支持的字段不要写入配置，例如 `css_selector`、`xpath`。
- 如果必须新增 parser，输出开发建议和最小测试思路。

## 下载链接与文件名

- 对候选下载链接检查 301/302/303/307/308 等重定向链。
- 真实保存文件名优先从 `Content-Disposition` 的 `filename*` 或 `filename` 获取。
- 响应头没有文件名时，使用最终 URL path 的最后一段。
- 如果文件名不包含版本号，使用 `#目标文件名` 让保存文件名稳定包含 `{version}`。
- 不要追加与 URL 文件名完全相同的无意义 `#...` 重命名。

## README 支持列表摘要

- `Supported software list` 是面向人工读者的支持清单，配置事实仍以 `version-checker.toml` 和实际生成的 `data/*.json` 为准。
- 新增、删除、重命名软件条目，或 `split`、Docker Hub 输出名、parser 输出名变化时，检查并同步该表格。
- `Name` 使用自然语言名称，不直接照抄 slug；保留官方大小写和常见专有名词，例如 `GitHub CLI`、`CoreDNS`、`OpenSSL`、`Node.js`、`Docker Compose`。
- 分支型输出在 Name 后追加分支号，例如 `Python 3.14`、`OpenSSL 3.5`、`Redis 8.0`。
- Docker Hub 输出使用 `Docker 镜像：<产品名>`；普通软件输出不要误写成 Docker 镜像，例如 `docker-compose` 写成 `Docker Compose`。
- JetBrains 插件输出优先使用生成数据中的 `display_name`，Name 写成 `JetBrains 插件：<插件名>`。
- `Summary` 使用中文简短摘要，描述软件用途；分支型输出可追加 `（<版本> 分支）`。
- `Link` 指向 `https://raw.githubusercontent.com/designinlife/version-checker/main/data/<json-name>.json`，链接文本使用实际 JSON basename。
- 只调整 `## Supported software list` 到下一个二级标题之间的表格，不改写 README 其他章节。
- 更新后检查表格结构、新增或变更链接对应的本地 `data/*.json`，并在回复中说明 README 表格是否已同步或已检查无需修改。
