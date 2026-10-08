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
# ---------------------------------------------------------------------------
# SECRET_KEY（2026-10-07 修复）
# 原来这里硬编码 SECRET_KEY，且 `os.environ[...] =` 会**强制覆盖** .env 里的真随机
# 密钥 ⇒ 实际生效的是公开常量，任何人可伪造 session cookie 冒用任意账号
# （实测可直读 /admin/users）。改为从 .env 读取并 **fail-closed**：读不到就拒绝
# 启动，绝不静默退化成已知密钥。
_PROC_BAD_KEYS = {
    'your-production-secret-key-change-this', 'procurement-secret-key-2026',
    'dev-secret-key-change-in-production', 'your-secret-key-here',
}


def _proc_load_secret_key():
    v = (os.environ.get('SECRET_KEY') or '').strip()
    if v in _PROC_BAD_KEYS:
        v = ''
    if not v:
        try:
            with open('/var/www/html/procurement/.env', encoding='utf-8') as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line.startswith('SECRET_KEY='):
                        v = _line.split('=', 1)[1].strip().strip('"\'')
                        break
        except OSError:
            v = ''
    if not v or v in _PROC_BAD_KEYS:
        raise RuntimeError('SECRET_KEY 未配置或仍为占位常量，拒绝启动（procurement）')
    return v


os.environ['SECRET_KEY'] = _proc_load_secret_key()


def _proc_load_database_url():
    v = (os.environ.get('DATABASE_URL') or '').strip()
    if not v:
        try:
            with open('/var/www/html/procurement/.env', encoding='utf-8') as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line.startswith('DATABASE_URL='):
                        v = _line.split('=', 1)[1].strip().strip('"\'')
                        break
        except OSError:
            v = ''
    if not v:
        raise RuntimeError('DATABASE_URL 未配置，拒绝启动（procurement）')
    return v


os.environ['DATABASE_URL'] = _proc_load_database_url()

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
