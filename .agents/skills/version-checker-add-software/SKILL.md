---
name: version-checker-add-software
description: 为当前 `version-checker` 项目从软件链接新增或更新软件检测配置，并生成、验证、同步 `version-checker.toml`。用户以 `@version-checker-add-software 软件链接`、`@技能 GitHub 仓库地址`、`生成 version-checker.toml 配置`、`新增软件下载检测配置`、`检查 Releases/Tags/下载链接`、`捕获 Windows/Linux x64/amd64 附件`、`用 CSS Selector/XPath 找下载地址` 等方式请求时必须使用。本技能既处理 GitHub Releases/Tags，也处理非 GitHub 下载页；会先写 `test.toml` 做验证，验证通过后再同步正式配置，且不主动提交 Git。
---

# Version Checker 软件配置技能

把用户给出的软件链接转换成当前项目可维护的 `[[softwares]]` 配置，并用最小测试配置验证后再落到 `version-checker.toml`。

## 适用范围

使用本技能处理这些输入：

- GitHub 仓库、GitHub Releases 页面、GitHub Tag 页面。
- 非 GitHub 的软件主页、下载页、目录索引页。
- 用户要求生成或更新 `version-checker.toml`、`download_urls`、`pattern`、`release = true`、`assets_patterns`。
- 用户直接说：`@version-checker-add-software 软件链接` 或 `@技能 软件链接`。此时不要只给建议，立即开始探测、生成 `test.toml`、验证配置。

不适合直接生成配置的情况：

- 页面需要登录、验证码、动态前端执行后才出现真实下载地址。
- 当前项目没有对应解析器或配置模型，而且 `parser = "index"` 无法覆盖。
- 下载地址只能通过复杂 API、脚本计算、许可证选择或多步表单得到。

遇到不支持类型时，说明缺少哪类解析器，并引导用户新增开发；不要编造项目尚不支持的 TOML 字段。

## 总体流程

1. 读取项目上下文。
   - 检查 `version-checker.toml` 中是否已有同一软件条目。
   - 优先按 `repo` 判断重复，其次按 `url`，最后按 `name`。
   - 查看相邻条目的格式，保持字段顺序和命名风格一致。

2. 判断链接类型。
   - `github.com/<owner>/<repo>`：走 GitHub 流程。
   - 其他域名：走非 GitHub 流程。
   - GitHub 以外但属于 Gitea/GitLab/Codeberg/SourceForge 等已支持解析器时，优先使用现有专用 parser。
   - 不确定时先用 `HEAD`/`GET` 核实最终 URL、状态码和响应头。

3. 基于一手信息生成候选配置。
   - 不凭记忆猜测版本、资产文件名、下载地址。
   - 记录最新版本、Tag 风格、资产列表、重定向链和关键响应头。

4. 写入临时配置验证。
   - 先生成 `test.toml`，不要直接改正式配置。
   - `test.toml` 应包含原配置必要的 `[app]` 基础信息和目标 `[[softwares]]` 条目，或能被 `version-checker` CLI 独立加载。
   - 用 `uv run version-checker -c test.toml inspect --filter-name <name>` 或当前 CLI 支持的等价最小命令验证目标条目。
   - 验证失败时先修正候选配置；不要把未验证配置同步到正式文件。

5. 同步正式配置。
   - 验证通过后，更新 `version-checker.toml`。
   - 已有条目则更新原条目，不新增重复块。
   - 新条目默认追加到文件末尾，除非用户指定位置。
   - 更新后再运行最小验证，确认正式配置可解析。
   - 不主动提交 Git；由用户决定何时提交。

6. 收尾说明。
   - 简要列出最终配置、验证命令和结果。
   - 若修改了配置键、运行方式或 README 可能需要同步，只提示用户；本项目 README 由用户维护。

## GitHub 流程

### 数据来源优先级

1. 优先检查 GitHub Releases。
   - 使用 GitHub Releases API：`https://api.github.com/repos/<owner>/<repo>/releases`。
   - 如果用户要求最新稳定版，默认跳过 draft 和 prerelease，除非仓库只有 prerelease 或用户明确接受。
   - 如果 Releases 中包含目标平台资产，使用 `release = true`。

2. Releases 不可用或没有有效资产时，再检查 Tags。
   - 使用 Tags API：`https://api.github.com/repos/<owner>/<repo>/tags`。
   - Tags 只适合生成版本检测和源码包链接；无法凭空生成不存在的二进制下载地址。

3. 如果仓库没有 Releases/Tags，说明当前无法配置版本检测，除非用户提供其他版本来源。

### Tag 与 pattern

- `pattern` 匹配 Release/Tag 名，不匹配附件文件名。
- 根据真实最新 Tag 推导，不要硬套 semver。
- 优先使用命名分组：
  - `version`
  - `major`
  - `minor`
  - `patch`
- 常见写法：

```toml
pattern = "^v(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$"
pattern = "^(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$"
pattern = "^release-(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$"
```

- 如果真实 Tag 是 `v1.2`，不要强行要求 patch。
- 如果真实 Tag 是 `app-v1.2.3`、`jq-1.8.0`、`bun-v1.2.3`，保留前缀。

### Release 资产筛选

默认目标是捕获 Windows/Linux 的 x64/amd64 版本和源码包：

- 保留平台：
  - `windows`、`win`
  - `linux`
- 保留架构：
  - `amd64`
  - `x64`
  - `x86_64`
- 排除：
  - `arm64`、`aarch64`、`armv7`、`arm`
  - `386`、`i386`、`x86`，除非它明确表示 `x86_64`
  - macOS、darwin、android、ios
  - checksum、sha256、sha512、sig、asc、minisig、sbom、attestation、provenance
  - debug symbols、source zip、installer metadata

选择规则：

- 默认每个平台至少保留一个最直接可用资产。
- Windows 优先 `.zip`，其次 `.msi`、`.exe`。
- Linux 优先 `.tar.gz` 或 `.tar.xz`，其次 `.zip`、`.deb`、`.rpm`、无扩展可执行文件。
- 同平台有 `gnu`/`musl`、`msvc`/`gnu` 等多个变体时，保留上游最常用或项目现有风格一致的变体；不确定时可以保留多个，但要说明原因。
- Release 资产不足时仍可加入源码包，但要说明没有找到目标平台二进制。

### 源码包链接

- 默认加入 `Source code (tar.gz)`，放在 `download_urls` 最后。
- 不加入 `Source code (zip)`，除非用户明确要求。
- 模板：

```toml
"https://github.com/<owner>/<repo>/archive/refs/tags/<tag-template>.tar.gz"
```

### 下载链接模板化

- 将最新 Tag 中由 `pattern` 捕获的版本部分替换为 `{version}`。
- 如果 Release URL 的 Tag 前缀不是版本的一部分，保留前缀：
  - `v1.2.3` -> `/download/v{version}/...`
  - `jq-1.8.0` -> `/download/jq-{version}/...`
  - `bun-v1.2.3` -> `/download/bun-v{version}/...`
- 资产文件名中的版本也替换为 `{version}`。

### 重定向与真实文件名

- 对候选下载链接执行 `HEAD`，必要时用小范围 `GET`，允许跟随 301/302/303/307/308。
- 记录最终 URL 和状态码；2xx 或可解释的 3xx 才视为有效。
- 真实保存文件名优先级：
  1. `Content-Disposition` 中的 `filename*` 或 `filename`。
  2. 最终 URL path 的最后一段。
  3. 原始资产名。
- 如果响应头文件名与 URL 文件名不同，应考虑在 `download_urls` 中追加 `#目标文件名`，使保存文件名稳定。
- 如果文件名本身不包含版本号，也应追加 `#目标文件名`，让下载结果包含 `{version}`。
- 如果 `#` 后目标文件名与 URL 最后文件名完全相同，不要追加无意义重命名。

示例：

```toml
"https://github.com/hatoo/oha/releases/download/v{version}/oha-linux-amd64#oha-{version}-linux-amd64"
"https://github.com/duckdb/duckdb/releases/download/v{version}/duckdb_cli-linux-amd64.zip#duckdb_cli-{version}-linux-amd64.zip"
```

## 非 GitHub 流程

### 页面探测

1. 先请求用户给出的软件链接。
2. 跟随重定向，记录最终 URL、HTTP status code、content-type。
3. 如果是 HTML 页面：
   - 用 CSS Selector 查找真实下载链接。
   - XPath 可用于浏览器或文档分析；落到当前项目配置前要确认项目是否已有支持该 XPath 的 parser。
   - 优先找明确包含版本号、平台、架构、扩展名的 `href`。
4. 如果是目录索引页：
   - 当前项目可优先尝试 `parser = "index"`。
   - `parser = "index"` 只会读取 `pre > a[href]` 和 `td > a[href]`，因此必须确认页面结构匹配。
5. 如果是 JSON/XML/API：
   - 只有当前项目已有对应 parser 时才直接配置。
   - 否则引导新增 parser。

### 非 GitHub 配置策略

优先使用项目已有 parser：

- 通用目录索引：`parser = "index"`。
- GitLab：`parser = "gitlab"`。
- Gitea：`parser = "gitea"`。
- Codeberg：`parser = "codeberg"`。
- SourceForge：`parser = "sf"`。
- 其他已存在的专用 parser 以 `src/app/core/config.py` 和 `src/app/parser/` 为准。

不要生成当前模型不支持的字段，例如 `css_selector = "..."`
或 `xpath = "..."`。如果必须依赖 CSS Selector/XPath 才能解析版本或下载链接，应输出“需要新增解析器”的开发建议，包含：

- parser 名称建议。
- 需要的配置字段。
- CSS Selector/XPath。
- 目标版本文本样例。
- 目标下载链接样例。
- 最小测试思路。

### 下载链接校验

- 对从 CSS Selector/XPath 找到的下载链接做 URL 规范化。
- 相对链接用最终页面 URL 补全。
- 跟随重定向并检查最终状态码。
- 从 `Content-Disposition` 获取保存文件名；没有时使用最终 URL 文件名。
- 对模板化下载链接保留 `{version}`，但验证时用真实最新版本替换后检查。

## `test.toml` 验证要求

用户给出链接后，默认按这个节奏执行：

1. 生成候选条目到 `test.toml`。
2. 运行配置解析或目标 inspect：

```powershell
uv run version-checker -c test.toml inspect --filter-name <name>
```

3. 如果 CLI 当前参数不同，以 `version-checker --help` 和 `inspect --help` 为准。
4. 验证 `data/<name>.json` 或 CLI 输出中包含期望最新版本和下载链接。
5. 验证通过后再更新 `version-checker.toml`。
6. 更新正式配置后再运行最小验证。

如果网络不稳定，可以在当前 shell 进程临时设置代理，但不要写入配置文件。

## 输出格式

### 成功生成并验证

用简短中文说明：

- 软件名称。
- 版本来源：GitHub Release、GitHub Tag、目录索引页、专用 parser 等。
- 最新版本和 Tag。
- 选择的下载链接数量与平台。
- `test.toml` 验证命令和结果。
- 是否已同步 `version-checker.toml`。
- 明确说明“未提交 Git”。

### 仅能输出候选配置

如果用户只要求片段，返回完整 TOML 配置块，并说明未写文件、未验证或验证限制。

### 不支持类型

输出新增开发建议，不要假装可配置：

```text
当前项目还不支持该页面类型，需要新增 parser。
建议 parser: xxx
版本来源: CSS Selector / XPath / API
下载链接来源: ...
需要补充测试: ...
```

## 配置示例

GitHub Release：

```toml
[[softwares]]
name = "example"
repo = "owner/repo"
url = "https://github.com/owner/repo"
pattern = "^v(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$"
release = true
download_urls = [
    "https://github.com/owner/repo/releases/download/v{version}/example-{version}-linux-amd64.tar.gz",
    "https://github.com/owner/repo/releases/download/v{version}/example-{version}-windows-amd64.zip",
    "https://github.com/owner/repo/archive/refs/tags/v{version}.tar.gz",
]
```

目录索引页：

```toml
[[softwares]]
name = "example-index"
parser = "index"
url = "https://downloads.example.com/example/"
pattern = "^example-(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))\\.tar\\.gz$"
download_urls = [
    "https://downloads.example.com/example/example-{version}.tar.gz",
]
```
