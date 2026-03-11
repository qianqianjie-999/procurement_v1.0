#!/bin/bash
# ============================================================================
# 采购管理系统 - 快速部署脚本
# 适用于 CentOS Stream 9
# 用法：sudo bash deploy.sh
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 运行
if [[ $EUID -ne 0 ]]; then
    log_error "此脚本必须以 root 权限运行"
    exit 1
fi

# 配置变量
APP_USER="apache"
APP_DIR="/var/www/html/procurement"
DB_NAME="procurement_system"
DB_USER="procurement"
DB_PASS="YourSecurePassword123!"
ADMIN_PASS="admin123"
PYTHON_VERSION="python3.9"

# ============================================================================
# 1. 安装系统依赖 (MariaDB/httpd 已安装可跳过)
# ============================================================================
log_info "步骤 1: 检查并安装依赖..."

# 检查 MariaDB
if systemctl is-active --quiet mariadb; then
    log_info "MariaDB 已在运行"
else
    log_warn "MariaDB 未运行，尝试启动..."
    systemctl enable --now mariadb
fi

# 检查 httpd
if systemctl is-active --quiet httpd; then
    log_info "httpd 已在运行"
else
    log_warn "httpd 未运行，尝试启动..."
    systemctl enable --now httpd
fi

# 检查 mod_wsgi
if httpd -M 2>/dev/null | grep -q wsgi; then
    log_info "mod_wsgi 已安装"
else
    log_warn "mod_wsgi 可能未安装，尝试安装..."
    dnf install -y mod_wsgi || true
fi

# 安装 Python 3.9 和开发工具（如果未安装）
if command -v python3.9 &>/dev/null; then
    log_info "Python 3.9 已安装"
else
    dnf install -y python3.9 python3.9-pip python3.9-devel gcc gcc-c++ make git
fi

# 安装字体
dnf install -y fonts-simsun || log_warn "字体包未找到，PDF 中文可能无法正常显示"

# ============================================================================
# 2. 配置 MariaDB 数据库
# ============================================================================
log_info "步骤 2: 配置 MariaDB 数据库..."

# 检查是否需要初始化数据库
read -p "是否需要初始化数据库？(输入密码将自动创建数据库和用户) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 获取 MariaDB root 密码
    read -sp "请输入 MariaDB root 密码：" MYSQL_ROOT_PASS
    echo

    # 初始化数据库
    mysql -u root -p"${MYSQL_ROOT_PASS}" << MYSQL_EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME}
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost'
    IDENTIFIED BY '${DB_PASS}';

GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
MYSQL_EOF
    log_info "数据库创建完成"
else
    log_warn "跳过数据库初始化，请手动执行 deploy/scripts/init_database.sql"
fi

# ============================================================================
# 3. 创建应用目录
# ============================================================================
log_info "步骤 3: 创建应用目录..."

mkdir -p ${APP_DIR}
mkdir -p /var/log/procurement

# ============================================================================
# 4. 安装应用
# ============================================================================
log_info "步骤 4: 安装应用..."

cd ${APP_DIR}

# 创建虚拟环境（使用 Python 3.9）
if [[ ! -d "venv" ]]; then
    ${PYTHON_VERSION} -m venv venv
    log_info "虚拟环境创建完成"
else
    log_warn "虚拟环境已存在"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    log_info "依赖安装完成"
else
    log_warn "requirements.txt 未找到"
fi

# 安装 PyMySQL (确保 MySQL 驱动)
pip install PyMySQL cryptography

# ============================================================================
# 5. 创建环境变量文件
# ============================================================================
log_info "步骤 5: 创建环境变量文件..."

cat > ${APP_DIR}/.env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=mariadb+pymysql://${DB_USER}:${DB_PASS}@localhost/${DB_NAME}?charset=utf8mb4
FLASK_ENV=production
EOF

chmod 600 ${APP_DIR}/.env

# ============================================================================
# 6. 设置权限
# ============================================================================
log_info "步骤 6: 设置权限..."

chown -R apache:apache ${APP_DIR}
chmod -R 755 ${APP_DIR}

# ============================================================================
# 7. 配置 Apache Web 服务器
# ============================================================================
log_info "步骤 7: 配置 Apache Web 服务器..."

# 复制 Apache 配置文件
if [[ -f "${APP_DIR}/deploy/apache/procurement.conf" ]]; then
    cp ${APP_DIR}/deploy/apache/procurement.conf /etc/httpd/conf.d/
    log_info "Apache 配置文件已复制"

    # 测试 Apache 配置
    if httpd -t 2>/dev/null; then
        log_info "Apache 配置测试通过"
    else
        log_warn "Apache 配置测试失败，请检查 /etc/httpd/conf.d/procurement.conf"
    fi
else
    log_warn "Apache 配置文件未找到"
fi

# ============================================================================
# 8. 重启 Apache
# ============================================================================
log_info "步骤 8: 重启 Apache..."

systemctl restart httpd

if systemctl is-active --quiet httpd; then
    log_info "Apache 运行正常"
else
    log_error "Apache 启动失败，请检查 /var/log/httpd/procurement_error.log"
fi

# ============================================================================
# 9. 配置防火墙
# ============================================================================
log_info "步骤 9: 配置防火墙..."

if command -v firewall-cmd &>/dev/null; then
    # 开放 9002 端口
    firewall-cmd --permanent --add-port=9002/tcp || true
    firewall-cmd --reload || true
    log_info "防火墙配置完成（端口 9002）"
else
    log_warn "firewall-cmd 未找到，请手动开放端口 9002"
fi

# ============================================================================
# 完成
# ============================================================================
echo ""
log_info "=========================================="
log_info "部署完成!"
log_info "=========================================="
echo ""
log_info "数据库信息:"
log_info "  数据库名：${DB_NAME}"
log_info "  用户名：${DB_USER}"
log_info "  密码：${DB_PASS}"
echo ""
log_info "默认管理员账号:"
log_info "  用户名：admin"
log_info "  密码：${ADMIN_PASS}"
echo ""
log_warn "请务必在首次登录后修改默认密码!"
echo ""
log_info "访问地址：http://localhost"
echo ""
