---
name: version-checker-github-release-config
description: 为当前 `version-checker` 项目生成或更新基于 GitHub Releases 的 `[[softwares]]` TOML 配置。只要用户提到新增仓库配置、生成 TOML 片段、根据 GitHub Release Tag 编写 `pattern`、从 Release 资产里筛选 `download_urls`，都应使用这个技能。尤其当用户提到 `release = true`、`pattern`、`download_urls`、GitHub Releases，或者只保留 Windows/Linux 的 amd64/x64/x86_64 附件时，必须优先使用本技能。
---

# Version Checker GitHub Release 配置技能

通过检查 GitHub 仓库的 Releases 和 Tags，为本项目生成可直接使用的 `[[softwares]]` 配置块。

## 目标

产出符合当前项目风格的 TOML 配置，例如：

```toml
[[softwares]]
name = "example"
repo = "owner/repo"
url = "https://github.com/owner/repo"
pattern = "^v(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$"
release = true
download_urls = [
    "https://github.com/owner/repo/releases/download/v{version}/artifact-{version}-windows-amd64.zip",
    "https://github.com/owner/repo/releases/download/v{version}/artifact-{version}-linux-amd64.tar.gz",
    "https://github.com/owner/repo/archive/refs/tags/v{version}.tar.gz"
]
```

## 必须遵循的流程

1. 先查看当前项目上下文。
    - 优先查看用户正在编辑的 TOML 文件。
    - 必须先检查主配置文件 `version-checker.toml` 是否已经存在同一个软件条目。
    - 保持与项目现有格式一致。
    - 如果 `version-checker.toml` 中已经存在相同软件（优先按 `repo` 判断，其次按 `name` 判断），就不要新增重复配置，只更新已有条目。

2. 必须基于一手信息核对 GitHub 仓库。
    - 优先使用 GitHub Releases API 与 Tags API。
    - 必须依据真实的最新 Release 和真实的资产文件名生成配置。
    - 不要凭记忆猜测资产命名。

3. 根据 Release Tag 推导 `pattern`。
    - `release = true` 表示版本来源是 GitHub Release。
    - `pattern` 用来匹配 GitHub Release 的 Tag 名，不是用来匹配附件文件名。
    - 优先使用这些命名分组：
        - `version`
        - `major`
        - `minor`
        - `patch`
    - 正则要贴合真实 Tag 风格。例如：
        - `v1.2.3` 对应 `^v(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$`
        - `1.2.3` 对应 `^(?P<version>(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+))$`
    - 如果真实 Tag 没有 patch，就不要强行要求 patch。

4. `download_urls` 由 Release 资产链接加 `Source code (tar.gz)` 组成。
    - 只保留以下系统：
        - `windows`
        - `linux`
    - 只保留以下架构：
        - `amd64`
        - `x64`
        - `x86_64`
    - 排除以下内容：
        - `arm64`
        - `aarch64`
        - `386`
        - `arm`
        - 其他平台安装包
        - checksums
        - signatures
        - SBOM
    - 默认还要额外加入 `Source code (tar.gz)` 下载链接，并且始终放在 `download_urls` 最后一个。

5. 严格应用文件名重写规则。
    - 如果资产文件名本身已经包含版本号，就不要追加 `#xxx` 重命名语法。
    - 如果资产文件名本身不包含版本号，就追加 `#目标文件名`，让下载后的文件名带上版本号。
    - 判断依据是 URL 最后面的实际文件名。
    - 如果 `#` 后面的目标文件名和 URL 最后面的实际文件名完全相同，也不要追加 `#...`。禁止出现这种无意义的“同名重命名”。
    - 例如下面这些都是错误写法：
        - `.../CLIProxyAPI_{version}_windows_amd64.zip#CLIProxyAPI_{version}_windows_amd64.zip`
        - `.../CLIProxyAPI_{version}_linux_amd64.tar.gz#CLIProxyAPI_{version}_linux_amd64.tar.gz`
    - 这个规则同样适用于源码归档链接。

6. 默认加入源码包，但只加入 `Source code (tar.gz)`。
    - 源码包使用：
        - `https://github.com/<owner>/<repo>/archive/refs/tags/<tag>.tar.gz`
    - 该源码链接默认追加到 `download_urls` 最后。
    - 除非用户明确要求，否则不要加入 `Source code (zip)`。

7. 输出要简洁且可直接使用。
    - 默认直接返回完整 TOML 配置块。
    - 如果主配置 `version-checker.toml` 已经存在对应条目，默认执行“更新现有条目”而不是“新增一段配置”。
    - 如果已经帮用户改了文件，只需用一句话说明改动内容。

## 选择规则

当存在多个匹配资产时：

- 默认每个系统只保留一个 amd64 风格附件：一个 Windows、一个 Linux，除非用户明确要求更多。
- 优先选择最常见、最直接可用的分发格式：
    - Windows 优先 `.zip`
    - Linux 优先 `.tar.gz`
- 如果同一系统同时存在 `x64` 和 `amd64`，优先选择项目现有配置风格一致的那个；若没有现成风格，则优先选择上游更明确、命名更规范的文件名。

## 输出格式

返回一个可直接粘贴的 TOML 配置块。

如果 `version-checker.toml` 中已经存在对应软件配置，则应修改原有块，而不是再新增一个新的 `[[softwares]]`。

如果用户要求直接修改文件，就修改后再展示最终结果。

## 示例

假设某个仓库的 Release Tag 是 `v6.8.55`，资产包括：

- `CLIProxyAPI_6.8.55_linux_amd64.tar.gz`
- `CLIProxyAPI_6.8.55_windows_amd64.zip`
- `CLIProxyAPI_6.8.55_windows_arm64.zip`

则结果应该只保留前两个 amd64 资产。

对应的正确写法是：

```toml
"https://github.com/router-for-me/CLIProxyAPI/releases/download/v{version}/CLIProxyAPI_{version}_linux_amd64.tar.gz",
"https://github.com/router-for-me/CLIProxyAPI/releases/download/v{version}/CLIProxyAPI_{version}_windows_amd64.zip",
```

另外还要默认在最后加入 `Source code (tar.gz)`：

```toml
"https://github.com/router-for-me/CLIProxyAPI/archive/refs/tags/v{version}.tar.gz"
```

因为这个文件名本身已经包含版本信息，所以这里不需要追加 `#...` 重命名。
