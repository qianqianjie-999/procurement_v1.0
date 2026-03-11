# GitHub 部署配置说明

## 1. 推送到 GitHub

```bash
# 初始化 git 仓库（如果没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/qianqianjie-999/procurement_v1.0.git

# 推送到 main 分支
git push -u origin main
```

## 2. 配置 GitHub Secrets

在 GitHub 仓库中，进入 **Settings → Secrets and variables → Actions**，添加以下 Secrets：

| Secret Name | 说明 | 示例值 |
|-------------|------|--------|
| `SERVER_HOST` | 服务器 IP 地址 | `*.*.*.*` |
| `SERVER_USERNAME` | 服务器用户名 | `root` |
| `SERVER_PORT` | SSH 端口 | `` |
| `SERVER_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### 生成 SSH 密钥（如果没有）

```bash
# 在服务器上生成专用部署密钥
ssh-keygen -t ed25519 -f github_deploy_key -C "github-actions"

# 将公钥添加到服务器 authorized_keys
cat github_deploy_key.pub >> ~/.ssh/authorized_keys

# 私钥内容添加到 GitHub Secrets
cat github_deploy_key | pbcopy  # macOS
# 或
cat github_deploy_key  # Linux/Windows 复制内容
```

## 3. 自动部署

配置完成后，每次推送到 `main` 分支会自动触发部署：

```bash
git add .
git commit -m "修复 bug"
git push origin main
```

GitHub Actions 会自动：
1. 拉取最新代码
2. 安装依赖
3. 重启 Apache

## 4. 手动从 GitHub 拉取部署

在服务器上执行：

```bash
cd /var/www/html/procurement
bash deploy/pull_deploy.sh
```

## 5. 首次从 GitHub 部署

如果是全新冠名部署，在服务器上执行：

```bash
# 1. 克隆项目
git clone https://github.com/your-username/procurement.git /var/www/html/procurement

# 2. 进入目录
cd /var/www/html/procurement

# 3. 执行部署脚本
bash deploy/deploy.sh
```

## 6. 分支策略

推荐分支：
- `main` - 生产分支，推送到此分支自动部署
- `develop` - 开发分支
- `feature/*` - 功能分支

修改 GitHub Actions 触发分支（.github/workflows/deploy.yml）：
```yaml
on:
  push:
    branches:
      - main      # 生产环境
      # - develop # 测试环境（可添加）
```
