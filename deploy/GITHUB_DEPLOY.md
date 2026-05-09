# GitHub 部署配置

详细说明请参阅 [README.md](../README.md)。

## GitHub Secrets 配置

在 **Settings → Secrets and variables → Actions** 添加：

| Secret | 说明 |
|--------|------|
| `SERVER_HOST` | 服务器 IP |
| `SERVER_USERNAME` | SSH 用户名 |
| `SERVER_PORT` | SSH 端口 |
| `SERVER_SSH_KEY` | SSH 私钥 |

## 部署触发

推送代码到 `main` 分支自动部署：

```bash
git push origin main
```

## 手动拉取部署

```bash
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

## 分支策略

- `main` - 生产环境（自动部署）
- `develop` - 开发环境（可选）
