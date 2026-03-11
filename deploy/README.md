# 采购管理系统 - 部署指南

## 服务器环境要求

- **操作系统**: CentOS Stream 9 (或 RHEL/AlmaLinux/Rocky Linux 9)
- **Web 服务器**: Apache HTTPD (已安装 mod_wsgi)
- **数据库**: MariaDB
- **Python**: 3.9+

---

## 方式一：从 GitHub 拉取部署（推荐）

### 1. 克隆项目

```bash
sudo git clone https://github.com/your-username/procurement.git /var/www/html/procurement
```

### 2. 执行部署脚本

```bash
cd /var/www/html/procurement
sudo bash deploy/pull_deploy.sh
```

### 3. 访问应用

浏览器访问：`http://your-server-ip:9002/`

---

## 方式二：自动部署（GitHub Actions）

配置 GitHub Actions 实现推送代码后自动部署。

### 1. 在 GitHub 仓库配置 Secrets

进入 **Settings → Secrets and variables → Actions**，添加：

| Secret | 说明 | 示例 |
|--------|------|------|
| `SERVER_HOST` | 服务器 IP | `123.57.86.80` |
| `SERVER_USERNAME` | SSH 用户名 | `root` |
| `SERVER_PORT` | SSH 端口 | `22` |
| `SERVER_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### 2. 推送代码

```bash
git push origin main
```

GitHub Actions 会自动部署到服务器。

详见 [GitHub 部署配置](GITHUB_DEPLOY.md)。

---

## 方式三：手动部署

### 1. 上传项目文件

将项目上传到 `/var/www/html/procurement` 目录：

```bash
# 创建目录
sudo mkdir -p /var/www/html/procurement

# 上传项目文件（使用 scp、rsync 或 FTP）
# 或解压压缩包
sudo tar -xzf procurement.tar.gz -C /var/www/html/
```

### 2. 执行部署脚本

```bash
cd /var/www/html/procurement
sudo bash deploy/deploy.sh
```

部署脚本会自动：
- 检查 MariaDB 和 httpd 状态
- 创建数据库和用户（可选）
- 创建 Python 3.9 虚拟环境
- 安装 Python 依赖
- 配置 Apache VirtualHost
- 设置文件权限

### 3. 初始化数据库

如果部署时跳过了数据库初始化，手动执行：

```bash
# 登录 MariaDB
mysql -u root -p

# 执行初始化脚本
source /var/www/html/procurement/deploy/scripts/init_database.sql

# 或
mysql -u root -p < /var/www/html/procurement/deploy/scripts/init_database.sql
```

### 4. 配置环境变量

编辑 `/var/www/html/procurement/deploy/wsgi.py`，修改：

```python
os.environ['SECRET_KEY'] = 'your-unique-secret-key'
os.environ['DATABASE_URL'] = 'mariadb+pymysql://procurement:YourPassword@localhost/procurement_system?charset=utf8mb4'
```

### 5. 重启 Apache

```bash
sudo systemctl restart httpd
```

### 6. 访问应用

浏览器访问：`http://your-server-ip:9002/`

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

默认普通用户：
- 用户名：`user`
- 密码：`user123`

**请务必在首次登录后修改默认密码！**

---

## 手动部署步骤

### 1. 创建虚拟环境

```bash
cd /var/www/html/procurement
python3.9 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置数据库

编辑 `deploy/scripts/init_database.sql`，修改密码后执行：

```bash
mysql -u root -p < deploy/scripts/init_database.sql
```

### 4. 配置 Apache

复制配置文件：

```bash
sudo cp deploy/apache/procurement.conf /etc/httpd/conf.d/
```

编辑 `/etc/httpd/conf.d/procurement.conf`，确认路径正确。

### 5. 设置权限

```bash
sudo chown -R apache:apache /var/www/html/procurement
sudo chmod -R 755 /var/www/html/procurement
```

### 6. 重启 Apache

```bash
sudo systemctl restart httpd
```

---

## 配置说明

### 数据库配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 数据库名 | 采购管理系统数据库 | `procurement_system` |
| 用户名 | 数据库用户 | `procurement` |
| 密码 | 数据库密码 | 请修改为强密码 |

### 环境变量 (在 wsgi.py 中配置)

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| SECRET_KEY | Flask 密钥 | 随机生成字符串 |
| DATABASE_URL | 数据库连接 URL | mariadb+pymysql://user:pass@localhost/db |
| FLASK_ENV | 运行环境 | production |

---

## 故障排查

### 查看日志

```bash
# Apache 错误日志
sudo tail -f /var/log/httpd/procurement_error.log

# Apache 访问日志
sudo tail -f /var/log/httpd/procurement_access.log

# MariaDB 日志
sudo tail -f /var/log/mariadb/mariadb.log
```

### 常见问题

**1. mod_wsgi 未加载**

```bash
# 检查 mod_wsgi 是否加载
httpd -M | grep wsgi

# 如果未加载，安装
sudo dnf install -y mod_wsgi
```

**2. Python 版本不匹配**

mod_wsgi 使用的 Python 版本必须与虚拟环境一致：

```bash
# 检查 mod_wsgi 的 Python 版本
rpm -qa | grep mod_wsgi

# 如果需要，重新编译安装对应版本的 mod_wsgi
```

**3. 权限错误**

```bash
# 检查文件权限
ls -la /var/www/html/procurement

# 修复权限
sudo chown -R apache:apache /var/www/html/procurement
```

**4. 数据库连接失败**

```bash
# 测试数据库连接
mysql -u procurement -p -e "SELECT 1"

# 检查 MariaDB 状态
systemctl status mariadb
```

**5. 端口冲突（已有 3 个项目在运行）**

如果端口 80 已被占用，可以：
- 使用不同端口（修改 Apache 配置）
- 使用不同域名/子域名
- 使用反向代理

---

## 维护

### 备份数据库

```bash
mysqldump -u procurement -p procurement_system > backup_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
mysql -u procurement -p procurement_system < backup_20260311.sql
```

### 更新应用

```bash
cd /var/www/html/procurement
git pull  # 或手动更新文件
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart httpd
```

---

## 联系支持

如有问题，请联系系统管理员。
