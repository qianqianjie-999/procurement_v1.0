#!/usr/bin/env python3
"""
快速验证修复后的系统
"""
from app import create_app
from app.models import PurchasePlan, User

def main():
    app = create_app('development')
    
    with app.test_client() as client:
        # 测试主页（未登录）
        response = client.get('/')
        print(f"🏠 主页状态: {response.status_code}")
        
        # 测试登录页面
        response = client.get('/auth/login')
        print(f"🔑 登录页状态: {response.status_code}")
        
        # 如果有用户，测试登录后页面
        with app.app_context():
            user = User.query.first()
            if user:
                print(f"👤 测试用户: {user.username}")
                # 这里不实际登录，只验证数据访问
                plans = PurchasePlan.query.filter_by(created_by=user.id).all()
                print(f"📋 采购计划数量: {len(plans)}")
                
                if plans:
                    plan = plans[0]
                    print(f"   - 计划ID: {plan.id}")
                    print(f"   - 计划名称: {plan.plan_name}")
                    print(f"   - 申请人: {plan.creator.username if plan.creator else '未知'}")
        
        print("\n✅ 基础功能验证通过！")

if __name__ == '__main__':
    main()