# 部署指南

详细部署说明请参阅主文档 [README.md](../README.md)。

## 快速部署

### 服务器手动部署

```bash
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

### 自动部署

推送代码到 `main` 分支自动触发部署（需配置 GitHub Secrets）。

## 部署脚本

| 脚本 | 说明 |
|------|------|
| `deploy.sh` | 完整部署脚本（首次部署） |
| `pull_deploy.sh` | 拉取更新脚本（已有部署） |

## 配置

- Apache: `deploy/apache/procurement.conf`
- WSGI: `deploy/wsgi.py`
- 数据库: `deploy/scripts/init_database.sql`

## 端口

默认端口 **9002**，修改请编辑 `deploy/apache/procurement.conf`。

## 故障排查

```bash
# Apache 错误日志
sudo tail -f /var/log/httpd/procurement_error.log

# 重启 Apache
sudo systemctl restart httpd
```

详细说明见 [README.md](../README.md)
