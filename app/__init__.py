from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from flask_login import LoginManager

from config import config


# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面。'


def create_app(config_name=None):
    """
    应用工厂函数

    Args:
        config_name: 配置名称 (development, testing, production)

    Returns:
        Flask 应用实例
    """
    if config_name is None:
        config_name = 'default'

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # 注册自定义模板过滤器
    from app.utils.helpers import number_to_chinese, now
    app.jinja_env.filters['number_to_chinese'] = number_to_chinese
    app.jinja_env.globals['now'] = now

    # 注册路由蓝图
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.plan import plan_bp
    app.register_blueprint(plan_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.pdf_view import pdf_bp
    app.register_blueprint(pdf_bp)

    from app.routes.approval_request import approval_request_bp
    app.register_blueprint(approval_request_bp)

    # 注册全局异常处理器（2026-10-07 新增：CSRF 校验失败 → 400 友好页）
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """注册全局异常处理器（2026-10-07 新增）。"""

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        """CSRF 校验失败 → 400 友好页/JSON。

        此前无任何 errorhandler：用户看到的是 Werkzeug 默认裸 400 页，既没有
        任何引导（不知道该刷新重试），也不留日志线索。这里补上。响应体为静态
        字符串，不回显任何请求数据，无 XSS 面。
        """
        from flask import Response, jsonify, request
        # ⚠️ 日志一行必须是纯 ASCII：procurement 的 WSGI 进程 stderr 编码为 ascii
        #    （实测 UnicodeEncodeError: 'ascii' codec can't encode characters），
        #    中文日志会在 logging 内部抛异常并往错误日志灌 --- Logging error --- 转储。
        line = 'CSRF validation failed: %s %s (%s)' % (request.method,
                                                       request.path,
                                                       error.description)
        app.logger.warning(line.encode('ascii', 'backslashreplace').decode('ascii'))
        if request.path.startswith('/api') or \
                'text/html' not in (request.headers.get('Accept') or ''):
            return jsonify({'success': False,
                            'message': '会话已过期或页面校验令牌失效，请刷新页面后重试'}), 400
        return Response(_CSRF_ERROR_HTML, status=400,
                        mimetype='text/html; charset=utf-8')


_CSRF_ERROR_HTML = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>400 - 页面已过期</title>\n<style>\n  html,body{height:100%;margin:0}\n  body{display:flex;align-items:center;justify-content:center;\n       font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;\n       background:#f5f6f8;color:#24292f}\n  .box{max-width:460px;padding:36px 40px;background:#fff;border-radius:12px;\n       box-shadow:0 6px 24px rgba(0,0,0,.08);text-align:center}\n  h1{margin:0 0 8px;font-size:22px}\n  p{margin:8px 0 20px;color:#57606a;line-height:1.7;font-size:14px}\n  a{display:inline-block;padding:10px 22px;border-radius:8px;background:#1f6feb;\n    color:#fff;text-decoration:none;font-size:14px}\n  a:hover{background:#1a5fd0}\n  code{background:#f0f2f5;padding:1px 6px;border-radius:4px;font-size:12px}\n</style>\n</head>\n<body>\n  <div class="box">\n    <h1>页面已过期</h1>\n    <p>会话或页面校验令牌已失效，本次提交未被处理。<br>\n       请返回后刷新页面，再重新提交一次。</p>\n    <a href="/">返回首页</a>\n    <p style="margin-top:16px;font-size:12px;color:#8c959f">\n      错误码 <code>400</code> · 校验失败（CSRF）\n    </p>\n  </div>\n</body>\n</html>\n'
