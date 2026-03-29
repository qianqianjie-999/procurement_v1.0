# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (port 5000)
python run.py

# Run test server (port 5001)
python test_server.py

# Initialize database and create default users
python init_users.py

# Flask shell with pre-loaded models
flask shell

# Run tests
python -m pytest <test_file.py>
```

## Architecture Overview

**Tech Stack**: Flask 3.1 + MariaDB + Bootstrap 5

**Core Modules**:
- `app/` - Application package
  - `routes/` - Blueprints: `main` (index/health), `auth` (login/logout/register), `plan` (CRUD/export/approval), `admin`, `pdf_view`
  - `models.py` - SQLAlchemy models: User, PurchasePlan, PurchaseItem, ApprovalFlow, ApprovalStep, ApprovalLog
  - `forms.py` - WTForms: LoginForm, RegistrationForm, PurchasePlanForm, PurchaseItemForm, ApprovalForm
  - `utils/helpers.py` - Utilities: generate_plan_number(), number_to_chinese(), now()
  - `templates/` - Jinja2 templates organized by feature
  - `static/` - CSS, JS, fonts, PDFs, uploads

**Key Patterns**:
- Application factory pattern (`create_app` in `app/__init__.py`)
- Blueprint-based routing with `url_prefix`
- Role-based access: `current_user.is_administrator()` checks
- Purchase plan workflow: draft → pending → approved/rejected

## Database

**Models**:
- `User` - Users with role-based access (admin/user)
- `PurchasePlan` - Main purchase plan table with status workflow
- `PurchaseItem` - Purchase items/details linked to plans
- `ApprovalFlow` / `ApprovalStep` - Multi-level approval workflow definition
- `ApprovalLog` - Audit trail for all approval actions

**Initialization**: Run `python init_users.py` to create the database and default users.

**Environment Variables** (via `.env` or `config.py`):
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection URL (SQLite for dev, MariaDB for prod)
- `FLASK_ENV` - development/testing/production

## Deployment

**Production**: Apache + mod_wsgi on CentOS 9, port 9002
- WSGI entry: `deploy/wsgi.py`
- Deploy scripts: `deploy/pull_deploy.sh`
- GitHub Actions auto-deploys on push to `main` (see `.github/workflows/deploy.yml`)

**Default Accounts**:
- admin/admin123 (administrator)
- user/user123 (normal user)
