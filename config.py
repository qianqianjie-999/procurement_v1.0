#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import timedelta

# ====================== 核心修复：给 Config 基类添加 init_app 方法 ======================
class Config:
    """基础配置类 - 所有环境的通用配置"""
    # 通用配置项（根据你的实际情况调整）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'procurement-secret-key-2026'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # 关键：添加这个缺失的 init_app 方法（空实现即可）
    @staticmethod
    def init_app(app):
        """基础配置初始化（空实现，供子类调用）"""
        pass

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # 开发环境数据库地址（优先从环境变量读取，否则使用 SQLite）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///procurement.db'

    # SQLite 不需要连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # PDF 导出配置（开发环境）
    PDF_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'pdfs')
    CHINESE_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'fonts', 'SimSun.ttf')

    # 上传文件配置（开发环境）
    SCANNED_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads', 'scanned')
    ATTACHMENT_STORAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads', 'attachments')

    # 上传文件大小限制 (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_SCANNED_EXTENSIONS = {'pdf'}
    ALLOWED_ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)  # 现在父类有 init_app 方法了，不会报错
        app.logger.info('Development config initialized')
        
        # 确保上传目录存在
        os.makedirs(cls.PDF_STORAGE_PATH, exist_ok=True)
        os.makedirs(cls.SCANNED_STORAGE_PATH, exist_ok=True)
        os.makedirs(cls.ATTACHMENT_STORAGE_PATH, exist_ok=True)

# 测试环境配置（如果有）
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+pymysql://root:你的密码@localhost/procurement_test'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.logger.info('Testing config initialized')

# 生产环境配置（你提供的内容）
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # 生产环境数据库地址（根据你的实际配置修改）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://procurement:YourSecurePassword123!@127.0.0.1/procurement_system'

    # 数据库连接池配置 - 防止 "MySQL server has gone away" 错误
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,              # 连接池大小
        'max_overflow': 20,           # 超过 pool_size 后允许的连接数
        'pool_timeout': 30,           # 等待连接的超时时间（秒）
        'pool_recycle': 1800,         # 连接回收时间（秒），防止连接过期
        'pool_pre_ping': True,        # 每次使用前检查连接是否有效，自动重连
    }

    # PDF 导出配置
    PDF_STORAGE_PATH = '/var/www/html/procurement/app/static/pdfs'
    CHINESE_FONT_PATH = '/var/www/html/procurement/app/static/fonts/SimSun.ttf'

    # PDF 优化配置：预加载字体到内存，避免每次读取磁盘
    PRELOAD_FONTS = True

    # 上传文件配置
    SCANNED_STORAGE_PATH = '/var/www/html/procurement/app/static/uploads/scanned'
    ATTACHMENT_STORAGE_PATH = '/var/www/html/procurement/app/static/uploads/attachments'

    # 上传文件大小限制 (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_SCANNED_EXTENSIONS = {'pdf'}
    ALLOWED_ATTACHMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)  # 现在父类有 init_app 方法，不会报错
        # 生产环境日志配置
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug:
            log_file='/var/www/html/procurement/procurement.log'
            file_handler = RotatingFileHandler(
                '/var/www/html/procurement/procurement.log', maxBytes=10240, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Procurement System Startup')

# 配置映射（供 create_app 调用）
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

