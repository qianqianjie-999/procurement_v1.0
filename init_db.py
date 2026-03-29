#!/usr/bin/env python3
"""
初始化数据库
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def main():
    app = create_app('development')
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库初始化成功！")

if __name__ == '__main__':
    main()