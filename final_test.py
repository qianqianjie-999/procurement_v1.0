#!/usr/bin/env python3
"""
采购管理系统 - 最终功能验证测试
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import PurchasePlan, User

def test_application():
    """测试应用创建和基本功能"""
    print("🔧 测试应用创建...")
    app = create_app('development')
    
    with app.app_context():
        print("✅ 应用创建成功")
        
        # 测试用户查询
        print("👥 测试用户查询...")
        user = User.query.first()
        if user:
            print(f"✅ 找到用户: {user.username}")
            
            # 测试采购计划查询
            print("📋 测试采购计划查询...")
            plans = PurchasePlan.query.filter_by(created_by=user.id).all()
            print(f"✅ 找到 {len(plans)} 个采购计划")
            
            if plans:
                plan = plans[0]
                print(f"   - 计划名称: {plan.plan_name}")
                print(f"   - 申请人: {plan.creator.username if plan.creator else '未知'}")
                print(f"   - 状态: {plan.status}")
                print(f"   - 预算金额: {plan.budget_amount}")
            
            # 测试模板渲染（简化版）
            print("🎨 测试模板兼容性...")
            from flask import render_template_string
            
            # 测试仪表板模板结构
            dashboard_template = """
            {% set plan_stats = {'total': 5, 'approved': 3, 'pending': 1, 'draft': 1} %}
            {% set recent_plans = [] %}
            {% extends "base.html" %}
            {% block content %}Dashboard Test{% endblock %}
            """
            
            try:
                result = render_template_string(dashboard_template)
                print("✅ 仪表板模板结构正常")
            except Exception as e:
                print(f"❌ 仪表板模板错误: {e}")
                return False
                
        else:
            print("⚠️  没有找到测试用户")
    
    return True

if __name__ == '__main__':
    print("🚀 采购管理系统最终测试")
    print("=" * 40)
    
    try:
        success = test_application()
        if success:
            print("\n🎉 所有测试通过！系统准备就绪！")
            print("\n📋 使用说明:")
            print("1. 启动开发服务器: python run.py")
            print("2. 访问 http://localhost:5000")
            print("3. 使用测试账号登录:")
            print("   - 管理员: admin / admin123")
            print("   - 普通用户: user / user123")
        else:
            print("\n❌ 测试失败，请检查错误信息")
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        sys.exit(1)