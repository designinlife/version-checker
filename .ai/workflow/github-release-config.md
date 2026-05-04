# GitHub Releases 配置工作流

当用户要求新增仓库配置、生成 TOML 片段、根据 GitHub Release Tag 编写 `pattern`、筛选 `download_urls`，或提到 `release = true`、GitHub Releases、Windows/Linux amd64 附件时，必须使用项目技能：

- `.agents/skills/version-checker-github-release-config/SKILL.md`

## 基本流程

1. 先检查 `version-checker.toml` 是否已有相同软件条目。
2. 优先按 `repo` 判断重复，其次按 `name` 判断重复。
3. 必须基于 GitHub Releases API 或 Tags API 的一手信息生成配置。
4. 根据真实 Tag 风格编写 `pattern`，不要凭记忆猜测。
5. 如果条目已存在，默认更新现有条目，不要新增重复配置。

## `pattern` 规则

- `release = true` 时，`pattern` 匹配 GitHub Release Tag 名，不匹配附件文件名。
- 优先使用命名分组：
  - `version`
  - `major`
  - `minor`
  - `patch`
- 真实 Tag 没有 patch 时，不要强行要求 patch。

## `download_urls` 规则

- 默认保留 Windows 和 Linux 的 amd64/x64/x86_64 附件。
- 默认排除 `arm64`、`aarch64`、`386`、`arm`、校验和、签名、SBOM 和其他平台附件。
- 默认加入 `Source code (tar.gz)`，并放在 `download_urls` 最后。
- 除非用户明确要求，不加入 `Source code (zip)`。

## 文件名重写规则

- 如果资产文件名本身已包含版本号，不要追加 `#目标文件名`。
- 如果资产文件名不包含版本号，才追加 `#目标文件名`，确保下载后的文件名带版本号。
- 如果 `#` 后目标文件名与 URL 最后实际文件名完全相同，不要追加无意义重命名。

## 输出规则

- 用户只要求片段时，输出可直接使用的 TOML 配置块。
- 用户要求直接修改文件时，修改 `version-checker.toml` 后简要说明。
- 修改配置后，应至少运行配置解析或目标条目的最小验证；涉及真实网络时说明是否执行了联调。
