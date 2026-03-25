# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py

# Initialize database (if needed)
python init_users.py
```

## Architecture Overview

**Tech Stack**: Flask 3.1 + MariaDB + Bootstrap 5

**Core Modules**:
- `app/` - Application package
  - `routes/` - Blueprints: `main` (index/health), `auth` (login/logout/register), `plan` (CRUD/export/approval)
  - `models.py` - SQLAlchemy models: User, PurchasePlan, PurchaseItem, ApprovalFlow, ApprovalStep, ApprovalLog
  - `forms.py` - WTForms: LoginForm, RegistrationForm, PurchasePlanForm, PurchaseItemForm, ApprovalForm
  - `utils/helpers.py` - Utilities: generate_plan_number(), number_to_chinese()
  - `templates/` - Jinja2 templates organized by feature
- `config.py` - Environment configs (DevelopmentConfig, TestingConfig, ProductionConfig)
- `run.py` - Entry point with shell context

**Key Patterns**:
- Application factory pattern (`create_app` in `app/__init__.py`)
- Blueprint-based routing with `url_prefix`
- Role-based access: `current_user.is_administrator()` checks
- Purchase plan workflow: draft → pending → approved/rejected

## Deployment

**Production**: Apache + mod_wsgi on CentOS 9, port 9002
- WSGI entry: `deploy/wsgi.py`
- Deploy scripts: `deploy/pull_deploy.sh`
- GitHub Actions auto-deploys on push to `main`

**Default Accounts**:
- admin/admin123 (administrator)
- user/user123 (normal user)
