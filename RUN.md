# Run

## Supported environment variables

| Name            | Value             | Description                                   |
| :-------------- | :---------------- | :-------------------------------------------- |
| OUTPUT_DATA_DIR | default: `./data` | Data storage directory (Notes: Relative Path) |
| PROXY           | `None`            | The proxy server address.                     |
| GITHUB_TOKEN    | `None`            | Github Token.                                 |

## Synchronize docker images

```bash
HTTPS_PROXY=192.168.6.113:7890 DOCKER_REGISTRY_HOST=harbor.stone.cs version-checker -c /usr/local/etc/version-checker.toml skopeo --latest
```
