#!/bin/bash
# ============================================================================
# 采购管理系统 - 服务器拉取部署脚本
# 用法：bash pull_deploy.sh
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置变量
APP_DIR="/var/www/html/procurement"
PYTHON_VERSION="python3.9"

echo ""
log_info "=========================================="
log_info "采购管理系统 - 从 GitHub 拉取部署"
log_info "=========================================="
echo ""

# 检查是否已存在项目目录
if [[ ! -d "${APP_DIR}" ]]; then
    log_error "项目目录不存在，请先从 GitHub 克隆项目"
    log_info "执行：git clone <your-repo-url> ${APP_DIR}"
    exit 1
fi

cd ${APP_DIR}

# 1. 拉取最新代码
log_info "步骤 1: 拉取最新代码..."

if [[ ! -d ".git" ]]; then
    log_error "这不是一个 git 仓库，请先执行 git init 和 git remote add origin"
    exit 1
fi

git fetch origin main
git reset --hard origin/main
log_info "代码拉取完成"

# 2. 检查虚拟环境
log_info "步骤 2: 检查虚拟环境..."

if [[ ! -d "venv" ]]; then
    log_warn "虚拟环境不存在，正在创建..."
    ${PYTHON_VERSION} -m venv venv
fi

source venv/bin/activate
log_info "虚拟环境已激活"

# 3. 安装依赖
log_info "步骤 3: 安装 Python 依赖..."

pip install --upgrade pip
pip install -r requirements.txt
log_info "依赖安装完成"

# 4. 检查环境变量文件
log_info "步骤 4: 检查环境变量..."

if [[ ! -f ".env" ]]; then
    log_warn ".env 文件不存在，从 .env.example 复制..."
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        log_warn "请编辑 .env 文件配置数据库连接"
    else
        cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=mariadb+pymysql://procurement:YourPassword@localhost/procurement_system?charset=utf8mb4
FLASK_ENV=production
EOF
        log_warn "已自动生成 .env 文件，请修改数据库配置"
    fi
fi

# 5. 初始化数据库（如果需要）
log_info "步骤 5: 检查数据库..."

read -p "是否需要初始化数据库？[y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -sp "请输入 MariaDB root 密码：" MYSQL_ROOT_PASS
    echo

    mysql -u root -p"${MYSQL_ROOT_PASS}" < deploy/scripts/init_database.sql
    log_info "数据库初始化完成"
else
    log_info "跳过数据库初始化"
fi

# 6. 设置权限
log_info "步骤 6: 设置权限..."

sudo chown -R apache:apache ${APP_DIR}
sudo chmod -R 755 ${APP_DIR}

# 7. 重启 Apache
log_info "步骤 7: 重启 Apache..."

sudo systemctl restart httpd

if sudo systemctl is-active --quiet httpd; then
    log_info "Apache 运行正常"
else
    log_error "Apache 启动失败，请检查日志：/var/log/httpd/procurement_error.log"
    exit 1
fi

# 完成
echo ""
log_info "=========================================="
log_info "部署完成!"
log_info "=========================================="
echo ""
log_info "访问地址：http://your-server-ip:9002/"
echo ""
log_info "默认账号:"
log_info "  管理员：admin / admin123"
log_info "  普通用户：user / user123"
echo ""
log_warn "请务必修改默认密码!"
echo ""
