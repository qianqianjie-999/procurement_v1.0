import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///procurement.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # 邮件配置（可选）
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # 每页显示数量
    POSTS_PER_PAGE = 20

    # PDF 配置
    PDF_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'pdfs')
    PDF_URL_PATH = '/static/pdfs'

    # 扫描件配置
    SCANNED_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'scanned')
    SCANNED_URL_PATH = '/static/scanned'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB 最大上传大小
    ALLOWED_SCANNED_EXTENSIONS = {'pdf'}

    # 中文字体配置（使用项目内字体文件）
    CHINESE_FONT_FAMILY = os.environ.get('CHINESE_FONT_FAMILY', 'SimSun, Songti SC, STSong, SimHei')
    CHINESE_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'fonts', 'SimSun.ttf')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

    @classmethod
    def init_app(cls, app):
        pass


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mariadb+pymysql://root:password@localhost/procurement_test'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug:
            file_handler = RotatingFileHandler(
                'procurement.log', maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Procurement System Startup')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
