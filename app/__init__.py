from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
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

    return app
