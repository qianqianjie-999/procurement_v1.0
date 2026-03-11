#!/usr/bin/python3
import sys
import logging
import os

# 配置日志
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# 关键：添加项目根目录到 Python 路径
sys.path.insert(0, '/var/www/html/procurement')

# 设置环境
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key-change-this'
os.environ['DATABASE_URL'] = 'mariadb+pymysql://procurement:YourSecurePassword123!@localhost/procurement_system?charset=utf8mb4'

try:
    # 从 app 包导入 create_app 函数
    from app import create_app

    # 创建应用实例
    application = create_app('production')

    # 强制生产环境配置
    application.config['DEBUG'] = False

except Exception as e:
    import traceback
    logging.error("Application startup failed: %s", str(e))
    logging.error(traceback.format_exc())
    raise
