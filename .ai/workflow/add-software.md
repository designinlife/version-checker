# 软件配置生成工作流

当用户要求新增软件配置、更新已有软件配置、从软件链接生成 `version-checker.toml` 片段、检查 GitHub Releases/Tags、筛选 Windows/Linux amd64 下载链接，或用 CSS Selector/XPath 分析非 GitHub 下载页时，必须使用项目技能：

- `.agents/skills/version-checker-add-software/SKILL.md`

## 触发场景

- `@version-checker-add-software 软件链接`
- `@技能 GitHub 仓库地址`
- 生成或更新 `[[softwares]]` 配置。
- 新增软件下载检测配置。
- 检查 Release 资产、Tag 版本、下载链接、重定向和真实保存文件名。
- 分析非 GitHub 下载页的真实下载链接。

## 基本流程

1. 先检查 `version-checker.toml` 是否已有相同软件条目。
2. 优先按 `repo` 判断重复，其次按 `url`，最后按 `name`。
3. 判断链接类型：
   - GitHub 仓库优先检查 Releases，Tag 版本次之。
   - 非 GitHub 项目优先尝试当前已有 parser；必要时用 CSS Selector/XPath 分析真实下载链接。
4. 先生成 `test.toml` 并做目标条目的最小验证。
5. 验证通过后再同步 `version-checker.toml`。
6. 更新正式配置后不要主动提交 Git，由用户决定提交时机。

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
