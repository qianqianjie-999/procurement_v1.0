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
    # 开发环境数据库地址（根据你的实际配置修改）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:你的密码@localhost/procurement_dev'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)  # 现在父类有 init_app 方法了，不会报错
        app.logger.info('Development config initialized')

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

    # PDF 导出配置
    PDF_STORAGE_PATH = '/var/www/html/procurement/app/static/pdfs'
    CHINESE_FONT_PATH = '/var/www/html/procurement/app/static/fonts/SimSun.ttf'

    # 上传文件配置
    SCANNED_STORAGE_PATH = '/var/www/html/procurement/app/static/uploads/scanned'
    ATTACHMENT_STORAGE_PATH = '/var/www/html/procurement/app/static/uploads/attachments'

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

