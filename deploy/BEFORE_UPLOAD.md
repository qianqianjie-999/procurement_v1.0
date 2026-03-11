# 上传到 GitHub 前的检查清单

## 1. 检查敏感文件

以下文件 **不应** 上传到 GitHub：

- [ ] `.env` - 环境变量（包含密码和密钥）
- [ ] `venv/` - Python 虚拟环境
- [ ] `__pycache__/` - Python 缓存文件
- [ ] `*.db` - SQLite 数据库文件
- [ ] `instance/` - Flask 实例目录
- [ ] `.gitignore` 中列出的其他文件

## 2. 检查配置文件

### config.py
- [ ] 确保没有硬编码的密码
- [ ] 敏感配置应从环境变量读取

### .env.example
- [ ] 提供配置模板供其他人参考
- [ ] 使用占位符值，不要使用真实密码

## 3. 首次上传步骤

```bash
# 进入项目目录
cd /home/qianqianjie/procurement

# 初始化 git（如果没有）
git init

# 添加所有文件
git add .

# 检查状态，确认没有敏感文件
git status

# 提交
git commit -m "Initial commit"

# 添加远程仓库（替换为你的 GitHub 用户名和仓库名）
git remote add origin https://github.com/qianqianjie-999/procurement_v1.0.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 4. 后续更新

```bash
git add .
git commit -m "更新内容描述"
git push origin main
```

## 5. 服务器拉取部署

在服务器上执行：

```bash
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

## 6. GitHub Actions 自动部署

如需配置自动部署，详见 [GITHUB_DEPLOY.md](GITHUB_DEPLOY.md)

## 7. 推荐的项目结构

```
procurement/
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions 配置
├── app/                     # 应用代码
├── deploy/                  # 部署脚本和配置
│   ├── apache/
│   ├── scripts/
│   ├── wsgi.py
│   ├── deploy.sh
│   ├── pull_deploy.sh
│   ├── README.md
│   └── GITHUB_DEPLOY.md
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略文件
├── README.md               # 项目说明
├── config.py               # 配置文件
├── requirements.txt        # Python 依赖
└── run.py                  # 启动脚本
```

## 8. GitHub 仓库设置建议

1. **Visibility**: 私有仓库（推荐）或公开仓库
2. **Branch Protection**: 保护 `main` 分支
3. **Secrets**: 在 Settings → Secrets 中配置服务器密钥

## 9. 安全提醒

- 不要将 `.env` 文件上传到 GitHub
- 不要将数据库密码等敏感信息写入代码
- 使用 `.gitignore` 排除敏感文件
- 定期更新 GitHub Secrets
- 使用 SSH 密钥而不是密码进行部署
