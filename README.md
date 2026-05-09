# 采购管理系统

企业级采购管理平台，支持采购计划全流程管理、审批流转、PDF导出等功能。

## 功能特性

| 模块 | 功能 |
|------|------|
| **用户认证** | 注册、登录、角色权限管理（管理员/普通用户） |
| **采购计划** | 创建、编辑、删除、列表查看、详情浏览 |
| **采购明细** | 物资名称、品牌型号、规格数量、需求日期 |
| **审批流程** | 多级审批、审批日志、同意/拒绝操作 |
| **PDF导出** | 采购计划PDF、审批单PDF、签章PDF |
| **安全防护** | CSRF保护、登录限速、验证码、密码加密 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.1 + Python 3.9+ |
| 数据库 | MariaDB / SQLite（开发） |
| 前端框架 | Bootstrap 5 + Bootstrap Icons |
| 认证 | Flask-Login + Flask-WTF |
| 部署 | Apache + mod_wsgi |
| PWA | Service Worker + Web App Manifest |

## 快速开始

### 环境要求

- Python 3.9+
- MariaDB 10.5+（生产环境）
- Apache + mod_wsgi（生产环境）

### 本地开发

```bash
# 克隆项目
git clone https://github.com/qianqianjie-999/procurement_v1.0.git
cd procurement

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 初始化数据库
python init_users.py

# 运行开发服务器
python run.py
```

访问 http://localhost:5000

### 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

**首次登录后请修改默认密码！**

## 项目结构

```
procurement/
├── app/
│   ├── __init__.py          # 应用工厂 create_app()
│   ├── models.py            # 数据模型
│   ├── forms.py             # WTForms 表单定义
│   ├── routes/              # 路由蓝图
│   │   ├── auth.py          # 认证（登录/注册/登出）
│   │   ├── admin.py         # 管理（用户管理/报表）
│   │   ├── plan.py          # 采购计划 CRUD
│   │   ├── approval_request.py  # 审批流程
│   │   └── pdf_view.py      # PDF 视图
│   ├── templates/           # Jinja2 模板
│   │   ├── auth/            # 认证页面
│   │   ├── admin/           # 管理页面
│   │   ├── plan/            # 采购计划页面
│   │   └── approval_request/ # 审批页面
│   └── static/              # 静态资源
│       ├── css/             # 样式文件
│       ├── js/              # JavaScript
│       ├── fonts/           # 字体文件
│       └── pwa/             # PWA 图标
├── deploy/                  # 部署配置
│   ├── apache/              # Apache VirtualHost 配置
│   ├── nginx/               # Nginx 配置
│   ├── scripts/             # 数据库初始化脚本
│   ├── systemd/             # systemd 服务配置
│   ├── uwsgi/               # uWSGI 配置
│   ├── deploy.sh            # 部署脚本
│   └── pull_deploy.sh       # 拉取部署脚本
├── migrations/              # Flask-Migrate 数据库迁移
├── config.py                # 配置文件
├── requirements.txt         # Python 依赖
└── run.py                   # 开发服务器入口
```

## 数据模型

```
User (用户)
├── username, email, password_hash
├── role (admin/user)
├── is_active_field
└── department, full_name

PurchasePlan (采购计划)
├── plan_number (编号), plan_name (名称)
├── status (draft/pending/approved/rejected/cancelled/completed)
├── budget_amount, actual_amount
├── procurement_method (采购方式)
└── created_by → User

PurchaseItem (采购明细)
├── item_name, brand_model, specification
├── quantity, unit
├── required_date
└── plan_id → PurchasePlan

ApprovalFlow (审批流程)
├── name, description
├── is_active
└── steps → ApprovalStep

ApprovalStep (审批步骤)
├── step_order, approver_type
├── approver_id → User
└── flow_id → ApprovalFlow

ApprovalLog (审批日志)
├── action, comment
├── created_at
├── user_id → User
└── request_id → ApprovalRequest
```

## 部署指南

### 方式一：GitHub Actions 自动部署（推荐）

1. 配置 GitHub Secrets：
   - `SERVER_HOST` - 服务器 IP
   - `SERVER_USERNAME` - SSH 用户名
   - `SERVER_PORT` - SSH 端口
   - `SERVER_SSH_KEY` - SSH 私钥

2. 推送代码：
   ```bash
   git push origin main
   ```

### 方式二：服务器手动部署

```bash
# 克隆项目
sudo git clone https://github.com/qianqianjie-999/procurement_v1.0.git /var/www/html/procurement

# 执行部署脚本
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

### 方式三：手动部署

1. 上传项目到 `/var/www/html/procurement`
2. 执行 `deploy/deploy.sh`
3. 配置 `deploy/wsgi.py` 中的环境变量
4. 重启 Apache：`sudo systemctl restart httpd`

访问 http://server-ip:9002/

### Apache 配置端口

默认部署使用端口 9002。如需修改，编辑 `deploy/apache/procurement.conf`：

```apache
Listen 9002
<VirtualHost *:9002>
```

## 安全特性

| 特性 | 说明 |
|------|------|
| **密码存储** | Werkzeug pbdf2:sha256 加密 |
| **CSRF 防护** | Flask-WTF 全局保护 + AJAX X-CSRF-Token |
| **登录限速** | 5次失败后封禁IP 5分钟 |
| **注册验证码** | 4位图片验证码 |
| **注册限速** | 同一IP每分钟最多注册5次 |
| **SQL注入防护** | SQLAlchemy ORM 参数化查询 |
| **XSS防护** | Jinja2 自动转义 |
| **重定向验证** | 仅允许相对路径 |

## 配置说明

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `SECRET_KEY` | Flask 密钥 | `openssl rand -hex 32` |
| `DATABASE_URL` | 数据库连接 | `mariadb+pymysql://user:pass@localhost/db` |
| `FLASK_ENV` | 运行环境 | `production` |

### 生产环境重要配置

1. **修改 SECRET_KEY**：
   ```bash
   openssl rand -hex 32
   ```
   将结果写入 `deploy/wsgi.py`

2. **修改数据库密码**：
   编辑 `deploy/scripts/init_database.sql`

3. **修改默认管理员密码**：
   首次登录后立即修改

## 故障排查

### 查看日志

```bash
# Apache 错误日志
sudo tail -f /var/log/httpd/procurement_error.log

# MariaDB 日志
sudo tail -f /var/log/mariadb/mariadb.log
```

### 常见问题

**mod_wsgi 未加载**：
```bash
httpd -M | grep wsgi
sudo dnf install -y mod_wsgi
```

**权限错误**：
```bash
sudo chown -R apache:apache /var/www/html/procurement
```

**数据库连接失败**：
```bash
mysql -u procurement -p -e "SELECT 1"
```

## 维护

### 备份数据库
```bash
mysqldump -u procurement -p procurement_system > backup_$(date +%Y%m%d).sql
```

### 更新应用
```bash
cd /var/www/html/procurement
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart httpd
```

## API 路由

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/` | 首页/仪表盘 |
| GET/POST | `/auth/login` | 登录 |
| GET/POST | `/auth/register` | 注册（含验证码） |
| GET | `/auth/logout` | 登出 |
| GET | `/admin/users` | 用户管理 |
| POST | `/admin/users/create` | 创建用户 |
| POST | `/admin/users/<id>/toggle-active` | 切换用户状态 |
| POST | `/admin/users/<id>/set-role` | 设置用户角色 |
| GET | `/plan` | 采购计划列表 |
| GET/POST | `/plan/new` | 创建采购计划 |
| GET | `/plan/<id>` | 采购计划详情 |
| GET | `/approval` | 审批列表 |
| GET | `/approval/<id>` | 审批详情 |
| POST | `/approval/<id>/approve` | 审批通过 |
| POST | `/approval/<id>/reject` | 审批拒绝 |

## 开发指南

### 添加新路由

1. 在 `app/routes/` 创建蓝图文件
2. 注册蓝图：`app/__init__.py`
3. 添加权限检查装饰器

```python
# app/routes/example.py
from flask import Blueprint
example_bp = Blueprint('example', __name__)

@example_bp.route('/example')
def example():
    return "Example"
```

```python
# app/__init__.py
from app.routes.example import example_bp
app.register_blueprint(example_bp)
```

### 添加新模型

```python
# app/models.py
class NewModel(db.Model):
    __tablename__ = 'new_models'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
```

### 添加新表单

```python
# app/forms.py
class NewForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    submit = SubmitField('提交')
```

## License

MIT License
