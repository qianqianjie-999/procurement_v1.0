#!/usr/bin/env python3
"""
测试表单字段
"""
from app import create_app

def test_form_fields():
    app = create_app('development')
    
    with app.test_request_context():
        from app.forms import PurchasePlanForm
        form = PurchasePlanForm()
        
        # 检查字段是否存在
        fields = ['submit', 'submit_and_submit']
        for field in fields:
            if hasattr(form, field):
                print(f'✅ 字段 {field} 存在')
            else:
                print(f'❌ 字段 {field} 不存在')

if __name__ == '__main__':
    test_form_fields()