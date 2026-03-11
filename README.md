# 采购管理系统

企业级采购管理平台，支持采购计划创建、审批流程管理、PDF 导出等功能。

## 功能特性

- 用户注册与登录
- 采购计划管理（创建、编辑、删除）
- 采购明细管理
- 多级审批流程
- PDF 导出与打印
- 角色权限管理

## 技术栈

- **后端**: Flask 3.1 + Python 3.9
- **数据库**: MariaDB
- **前端**: Bootstrap 5 + Font Awesome
- **部署**: Apache + mod_wsgi

## 快速开始

### 本地开发

```bash
# 克隆项目
git clone https://github.com/your-username/procurement.git
cd procurement

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库

# 初始化数据库
python init_users.py

# 运行开发服务器
python run.py
```

### 生产部署

#### 从 GitHub 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/qianqianjie-999/procurement_v1.0.git /var/www/html/procurement

# 执行部署脚本
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

### 自动部署

配置 GitHub Actions 后，推送到 `main` 分支自动部署。详见 [GitHub 部署配置](deploy/GITHUB_DEPLOY.md)。

### 手动部署

详见 [部署文档](deploy/README.md)

## 目录结构

```
procurement/
├── app/                 # 应用主目录
│   ├── __init__.py      # 应用工厂
│   ├── models.py        # 数据模型
│   ├── forms.py         # WTForms 表单
│   ├── routes/          # 路由蓝图
│   ├── templates/       # Jinja2 模板
│   └── static/          # 静态文件
├── deploy/              # 部署配置
│   ├── apache/          # Apache 配置
│   ├── scripts/         # 数据库脚本
│   ├── wsgi.py          # WSGI 入口
│   └── deploy.sh        # 部署脚本
├── config.py            # 配置文件
├── requirements.txt     # Python 依赖
└── run.py               # 启动脚本
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

## License

MIT
