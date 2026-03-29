#!/usr/bin/env python3
"""
测试修复后的采购管理系统
"""
from app import create_app
from app.models import PurchasePlan, User

app = create_app('development')

if __name__ == '__main__':
    print("🚀 启动测试服务器...")
    print("访问 http://localhost:5001 查看修复后的ERP界面")
    app.run(host='0.0.0.0', port=5001, debug=True)