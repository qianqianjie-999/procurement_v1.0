#!/usr/bin/env python3
"""
采购管理系统 - 功能测试脚本
测试所有主要功能模块
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, PurchasePlan, PurchaseItem, ApprovalFlow, ApprovalStep, ApprovalLog
from app.forms import LoginForm, RegistrationForm, PurchasePlanForm
from flask_login import login_user, logout_user, current_user
from datetime import datetime, date
from decimal import Decimal

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_user_model():
    """测试用户模型"""
    print_section("1. 用户模型测试")

    # 测试创建用户
    user = User(
        username='test_user_001',
        email='test001@example.com',
        full_name='测试用户',
        department='测试部门',
        role='user'
    )
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()
    print(f"✅ 创建用户成功：{user.username}")

    # 测试密码验证
    assert user.check_password('test123'), "密码验证失败"
    assert not user.check_password('wrong'), "错误密码应该验证失败"
    print("✅ 密码验证功能正常")

    # 测试管理员检查
    assert not user.is_administrator(), "普通用户不应是管理员"
    user.role = 'admin'
    assert user.is_administrator(), "管理员应该通过检查"
    print("✅ 管理员检查功能正常")

    # 测试用户查询
    found_user = User.query.filter_by(username='test_user_001').first()
    assert found_user is not None, "用户查询失败"
    assert found_user.email == 'test001@example.com', "用户邮箱不匹配"
    print("✅ 用户查询功能正常")

    # 清理
    db.session.delete(user)
    db.session.commit()
    print("✅ 用户模型测试通过\n")

def test_purchase_plan_model():
    """测试采购计划模型"""
    print_section("2. 采购计划模型测试")

    # 创建测试用户
    user = User(
        username='test_plan_user',
        email='test_plan@example.com',
        role='user'
    )
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()

    # 测试创建采购计划
    plan = PurchasePlan(
        plan_number='PLAN-2026-001',
        plan_name='测试采购计划',
        project_manager='张三',
        plan_type='goods',
        status='draft',
        budget_amount=Decimal('100000.00'),
        currency='CNY',
        procurement_method='public_bidding',
        department='测试部门',
        description='测试采购说明',
        created_by=user.id
    )
    db.session.add(plan)
    db.session.commit()
    print(f"✅ 创建采购计划成功：{plan.plan_number}")

    # 测试类型标签
    assert plan.plan_type_label == '货物', "采购类型标签错误"
    assert plan.status_label == '草稿', "状态标签错误"
    print("✅ 类型和状态标签功能正常")

    # 测试状态转换
    plan.status = 'pending'
    assert plan.status_label == '待审批', "状态转换失败"
    plan.status = 'approved'
    assert plan.status_label == '已批准', "状态转换失败"
    print("✅ 状态转换功能正常")

    # 测试关联查询
    plans = user.purchase_plans.all()
    assert len(plans) == 1, "关联查询失败"
    print("✅ 关联关系查询正常")

    # 清理
    db.session.delete(plan)
    db.session.delete(user)
    db.session.commit()
    print("✅ 采购计划模型测试通过\n")

def test_purchase_item_model():
    """测试采购明细模型"""
    print_section("3. 采购明细模型测试")

    # 创建测试用户和计划
    user = User(username='test_item_user', email='test_item@example.com', role='user')
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()

    plan = PurchasePlan(
        plan_number='PLAN-2026-002',
        plan_name='测试采购计划 - 明细',
        created_by=user.id,
        status='draft'
    )
    db.session.add(plan)
    db.session.commit()

    # 测试创建采购明细
    item = PurchaseItem(
        plan_id=plan.id,
        item_name='笔记本电脑',
        brand_model='ThinkPad X1',
        specification='i7/32GB/1TB SSD',
        category='电子设备',
        quantity=Decimal('10.0000'),
        unit='台',
        batch_quantity=Decimal('5.0000'),
        supplier_name='测试供应商',
        remarks='测试备注'
    )
    db.session.add(item)
    db.session.commit()
    print(f"✅ 创建采购明细成功：{item.item_name}")

    # 测试关联关系
    items = plan.items.all()
    assert len(items) == 1, "关联查询失败"
    assert items[0].item_name == '笔记本电脑', "明细名称不匹配"
    print("✅ 关联关系查询正常")

    # 清理
    db.session.delete(item)
    db.session.delete(plan)
    db.session.delete(user)
    db.session.commit()
    print("✅ 采购明细模型测试通过\n")

def test_approval_flow_model():
    """测试审批流程模型"""
    print_section("4. 审批流程模型测试")

    # 创建测试用户和计划
    user = User(username='test_flow_user', email='test_flow@example.com', role='user')
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()

    plan = PurchasePlan(
        plan_number='PLAN-2026-003',
        plan_name='测试采购计划 - 流程',
        created_by=user.id,
        status='pending'
    )
    db.session.add(plan)
    db.session.commit()

    # 测试创建审批流程
    flow = ApprovalFlow(
        plan_id=plan.id,
        flow_name='标准审批流程',
        flow_type='standard',
        current_step=1,
        total_steps=3,
        status='pending'
    )
    db.session.add(flow)
    db.session.commit()
    print(f"✅ 创建审批流程成功：{flow.flow_name}")

    # 测试创建审批步骤
    step1 = ApprovalStep(
        flow_id=flow.id,
        step_order=1,
        step_name='部门经理审批',
        step_type='department',
        approver_id=user.id,
        status='pending'
    )
    db.session.add(step1)
    db.session.commit()
    print(f"✅ 创建审批步骤成功：{step1.step_name}")

    # 测试关联关系
    steps = flow.steps.order_by('step_order').all()
    assert len(steps) == 1, "关联查询失败"
    assert steps[0].step_name == '部门经理审批', "步骤名称不匹配"
    print("✅ 关联关系查询正常")

    # 清理
    db.session.delete(step1)
    db.session.delete(flow)
    db.session.delete(plan)
    db.session.delete(user)
    db.session.commit()
    print("✅ 审批流程模型测试通过\n")

def test_approval_log_model():
    """测试审批日志模型"""
    print_section("5. 审批日志模型测试")

    # 创建测试用户和计划
    user = User(username='test_log_user', email='test_log@example.com', role='user')
    user.set_password('test123')
    db.session.add(user)
    db.session.commit()

    plan = PurchasePlan(
        plan_number='PLAN-2026-004',
        plan_name='测试采购计划 - 日志',
        created_by=user.id,
        status='pending'
    )
    db.session.add(plan)
    db.session.commit()

    # 测试创建审批日志
    log = ApprovalLog(
        plan_id=plan.id,
        action='submit',
        previous_status='draft',
        new_status='pending',
        operator_id=user.id,
        comments='提交审批'
    )
    db.session.add(log)
    db.session.commit()
    print(f"✅ 创建审批日志成功：{log.action}")

    # 测试关联关系
    logs = plan.approval_logs.all()
    assert len(logs) == 1, "关联查询失败"
    assert logs[0].operator_id == user.id, "操作人不匹配"
    print("✅ 关联关系查询正常")

    # 清理
    db.session.delete(log)
    db.session.delete(plan)
    db.session.delete(user)
    db.session.commit()
    print("✅ 审批日志模型测试通过\n")

def test_forms():
    """测试表单验证"""
    print_section("6. 表单验证测试")

    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False  # 测试时禁用 CSRF

    with app.test_request_context():
        # 测试登录表单
        login_form = LoginForm(username='admin', password='admin123', remember_me=False)
        if not login_form.validate():
            print(f"  登录表单错误：{login_form.errors}")
        assert login_form.validate(), "登录表单验证失败"
        print("✅ 登录表单验证通过")

        # 测试注册表单（使用唯一用户名和邮箱）
        import time
        timestamp = str(int(time.time()))
        reg_form = RegistrationForm(
            username=f'test_reg_{timestamp}',
            email=f'test_reg_{timestamp}@example.com',
            password='password123',
            password2='password123',
            full_name='测试用户',
            department='测试部门'
        )
        if not reg_form.validate():
            print(f"  注册表单错误：{reg_form.errors}")
        assert reg_form.validate(), "注册表单验证失败"
        print("✅ 注册表单验证通过")

        # 测试采购计划表单
        plan_form = PurchasePlanForm(
            plan_name='测试计划',
            plan_type='goods',
            procurement_method='public_bidding',
            department='测试部门'
        )
        if not plan_form.validate():
            print(f"  采购计划表单错误：{plan_form.errors}")
        assert plan_form.validate(), "采购计划表单验证失败"
        print("✅ 采购计划表单验证通过")

    print("✅ 表单验证测试通过\n")

def test_helpers():
    """测试辅助函数"""
    print_section("7. 辅助函数测试")

    from app.utils.helpers import generate_plan_number, number_to_chinese, now

    # 测试数字转中文
    result_123 = number_to_chinese(123)
    assert '壹佰贰拾叁' in result_123, f"数字转中文失败：{result_123}"
    result_1000 = number_to_chinese(1000)
    assert '壹仟' in result_1000, f"数字转中文失败：{result_1000}"
    print("✅ 数字转中文功能正常")

    # 测试生成计划编号
    plan_number = generate_plan_number()
    assert plan_number.startswith('PP-'), "计划编号格式错误"
    print(f"✅ 生成计划编号功能正常：{plan_number}")

    # 测试当前时间
    current_time = now()
    assert isinstance(current_time, datetime), "当前时间返回类型错误"
    print("✅ 当前时间函数正常")

    print("✅ 辅助函数测试通过\n")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  采购管理系统 - 功能测试")
    print("  采购管理系统 - 功能测试")
    print("="*60)

    app = create_app('development')

    with app.app_context():
        try:
            test_user_model()
            test_purchase_plan_model()
            test_purchase_item_model()
            test_approval_flow_model()
            test_approval_log_model()
            test_forms()
            test_helpers()

            print("\n" + "="*60)
            print("  ✅ 所有测试通过!")
            print("="*60 + "\n")
            return True

        except AssertionError as e:
            print(f"\n❌ 测试失败：{e}\n")
            return False
        except Exception as e:
            print(f"\n❌ 测试异常：{e}\n")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
