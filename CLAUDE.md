# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

采购管理系统 - 企业级采购计划管理平台，支持采购计划全流程管理、审批流转、PDF导出。

**技术栈**: Flask 3.1 + MariaDB + Bootstrap 5 + PWA

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器 (端口 5000)
python run.py

# 初始化数据库和默认用户
python init_users.py

# Flask shell (预加载模型)
flask shell
```

## 项目结构

```
app/
├── __init__.py      # 应用工厂 create_app()
├── models.py        # 数据模型: User, PurchasePlan, PurchaseItem, ApprovalFlow, ApprovalStep, ApprovalLog
├── forms.py         # WTForms 表单
├── routes/          # 路由蓝图
│   ├── auth.py              # 认证 (登录/注册/登出)
│   ├── admin.py             # 管理 (用户管理/报表)
│   ├── plan.py              # 采购计划 CRUD
│   ├── approval_request.py  # 审批流程
│   └── pdf_view.py          # PDF 视图
├── templates/        # Jinja2 模板
│   ├── auth/         # 登录、注册页面
│   ├── admin/        # 用户管理页面
│   ├── plan/         # 采购计划页面
│   └── approval_request/  # 审批页面
└── utils/           # 工具模块
    ├── captcha.py    # 验证码生成
    ├── rate_limit.py # 速率限制
    ├── security.py   # 安全工具 (登录限速)
    └── helpers.py    # 辅助函数
```

## 核心模式

- **应用工厂模式**: `create_app()` 在 `app/__init__.py`
- **蓝图路由**: 使用 `url_prefix` 的 Blueprint 模式
- **角色权限**: `current_user.is_administrator()` 检查
- **采购计划流程**: draft → pending → approved/rejected

## 数据模型

| 模型 | 说明 |
|------|------|
| User | 用户 (admin/user 角色, is_active_field 状态) |
| PurchasePlan | 采购计划主表 (status: draft/pending/approved/rejected/cancelled/completed) |
| PurchaseItem | 采购明细 (关联 PurchasePlan) |
| ApprovalFlow | 审批流程定义 |
| ApprovalStep | 审批步骤 |
| ApprovalLog | 审批操作日志 |

## 安全特性

| 特性 | 实现位置 |
|------|----------|
| CSRF 防护 | `app/routes/admin.py` - AJAX 使用 `X-CSRF-Token` 请求头 |
| 登录限速 | `app/utils/security.py` - 5次失败封禁5分钟 |
| 注册验证码 | `app/utils/captcha.py` - 4位图片验证码 |
| 注册限速 | `app/utils/rate_limit.py` - 5次/分钟 |
| 密码加密 | Werkzeug `pbdf2:sha256` |

## 模板变量/过滤器

- `csrf_token()` - 获取 CSRF token
- `number_to_chinese()` - 数字转中文大写
- `now` - 当前时间

## 环境变量

| 变量 | 说明 |
|------|------|
| SECRET_KEY | Flask 密钥 |
| DATABASE_URL | 数据库连接 URL |
| FLASK_ENV | development/testing/production |

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| user | user123 | 普通用户 |

## 部署

**生产环境**: Apache + mod_wsgi on CentOS 9, 端口 9002

- WSGI 入口: `deploy/wsgi.py`
- 部署脚本: `deploy/pull_deploy.sh`
- GitHub Actions 自动部署 (`.github/workflows/deploy.yml`)
