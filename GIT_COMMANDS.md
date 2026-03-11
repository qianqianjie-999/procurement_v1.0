# Git 快速命令参考

## 首次上传到 GitHub

```bash
cd /home/qianqianjie/procurement

# 初始化
git init

# 添加所有文件
git add .

# 检查状态
git status

# 提交
git commit -m "Initial commit"

# 关联远程仓库
git remote add origin https://github.com/qianqianjie-999/procurement_v1.0.git

# 推送
git branch -M main
git push -u origin main
```

## 日常提交

```bash
# 查看变更
git status
git diff

# 添加并提交
git add .
git commit -m "描述变更内容"

# 推送到 GitHub
git push origin main
```

## 服务器部署

### 方式一：手动拉取
```bash
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

### 方式二：GitHub Actions 自动部署
推送代码后自动部署，无需手动操作

## 常用 Git 命令

```bash
# 查看日志
git log --oneline

# 撤销未提交的修改
git checkout -- <file>

# 撤销已暂存的修改
git reset HEAD <file>

# 拉取远程代码
git pull origin main

# 切换分支
git checkout -b <branch-name>
```

## 服务器 SSH 密钥配置

```bash
# 生成密钥（可选 ed25519 或 rsa）
ssh-keygen -t ed25519 -C "your-email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 复制公钥内容到 GitHub: Settings → SSH and GPG keys
```

## GitHub Secrets 配置

在 GitHub 仓库 **Settings → Secrets and variables → Actions** 添加：

| Secret | 说明 | 示例 |
|--------|------|------|
| `SERVER_HOST` | 服务器 IP | `123.57.86.80` |
| `SERVER_USERNAME` | SSH 用户名 | `root` |
| `SERVER_PORT` | SSH 端口 | `22` |
| `SERVER_SSH_KEY` | SSH 私钥 | 完整的私钥内容 |
