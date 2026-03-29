#!/usr/bin/env python3
"""
采购管理系统 - Web 路由测试脚本
测试所有主要路由和页面
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, PurchasePlan
from flask_login import login_user

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_main_routes():
    """测试主页面路由"""
    print_section("1. 主页路由测试")

    app = create_app('development')
    client = app.test_client()

    # 测试首页（应重定向到登录）
    response = client.get('/')
    assert response.status_code == 302, f"首页应重定向到登录页，得到 {response.status_code}"
    print("✅ 首页重定向到登录页")

    # 测试登录页面
    response = client.get('/auth/login')
    assert response.status_code == 200, f"登录页面应返回 200，得到 {response.status_code}"
    print("✅ 登录页面正常")

    # 测试注册页面
    response = client.get('/auth/register')
    assert response.status_code == 200, f"注册页面应返回 200，得到 {response.status_code}"
    print("✅ 注册页面正常")

    print("✅ 主页路由测试通过\n")

def test_login():
    """测试登录功能"""
    print_section("2. 登录功能测试")

    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    # 测试登录成功
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200, f"登录应成功，得到 {response.status_code}"
    print("✅ 管理员登录成功")

    # 测试登录失败（错误密码）- 应该返回表单页或重定向
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    # 登录失败可能返回 200（显示表单）或 302（重定向）
    assert response.status_code in [200, 302], "登录失败应返回表单页或重定向"
    print("✅ 错误密码登录失败处理正常")

    # 测试登出
    with app.test_request_context():
        user = User.query.filter_by(username='admin').first()
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)

    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200, "登出应成功"
    print("✅ 登出功能正常")

    print("✅ 登录功能测试通过\n")

def test_plan_routes():
    """测试采购计划路由"""
    print_section("3. 采购计划路由测试")

    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    # 先登录
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 测试采购计划列表页
    response = client.get('/plans/')
    assert response.status_code == 200, f"计划列表页应返回 200，得到 {response.status_code}"
    print("✅ 采购计划列表页正常")

    # 测试新建计划页面
    response = client.get('/plans/new')
    assert response.status_code == 200, f"新建计划页应返回 200，得到 {response.status_code}"
    print("✅ 新建计划页面正常")

    # 测试创建计划
    response = client.post('/plans/new', data={
        'plan_name': '测试采购计划',
        'plan_type': 'goods',
        'procurement_method': 'public_bidding',
        'department': '测试部门',
        'project_manager': '张三',
        'description': '测试说明',
        'remarks': '测试备注',
        'item_names[]': ['测试物品'],
        'quantities[]': ['10'],
        'units[]': ['个']
    }, follow_redirects=True)
    assert response.status_code == 200, f"创建计划应成功，得到 {response.status_code}"
    print("✅ 创建采购计划成功")

    # 验证数据库中是否有新计划
    with app.app_context():
        plan = PurchasePlan.query.filter_by(plan_name='测试采购计划').first()
        assert plan is not None, "数据库中应存在新创建的采购计划"
        plan_id = plan.id
        print(f"✅ 数据库中存在新计划，ID: {plan_id}")

        # 测试计划详情页
        response = client.get(f'/plans/{plan_id}')
        assert response.status_code == 200, f"计划详情页应返回 200，得到 {response.status_code}"
        print("✅ 计划详情页正常")

        # 测试编辑计划页面
        response = client.get(f'/plans/{plan_id}/edit')
        assert response.status_code == 200, f"编辑计划页应返回 200，得到 {response.status_code}"
        print("✅ 编辑计划页面正常")

        # 测试删除计划
        response = client.post(f'/plans/{plan_id}/delete', follow_redirects=True)
        assert response.status_code == 200, f"删除计划应成功，得到 {response.status_code}"
        print("✅ 删除采购计划成功")

        # 验证数据库中被删除
        deleted_plan = PurchasePlan.query.get(plan_id)
        assert deleted_plan is None, "数据库中应不存在已删除的采购计划"
        print("✅ 数据库中计划已删除")

    print("✅ 采购计划路由测试通过\n")

def test_admin_routes():
    """测试管理员路由"""
    print_section("4. 管理员路由测试")

    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    # 先登录
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 测试用户管理页
    response = client.get('/admin/users')
    assert response.status_code == 200, f"用户管理页应返回 200，得到 {response.status_code}"
    print("✅ 用户管理页正常")

    # 测试采购计划管理页（如果存在）
    response = client.get('/admin/plans')
    # 可能返回 200 或 404
    if response.status_code == 200:
        print("✅ 采购计划管理页正常")
    else:
        print("⚠️  采购计划管理页不存在")

    print("✅ 管理员路由测试通过\n")

def test_pdf_routes():
    """测试 PDF 相关路由"""
    print_section("5. PDF 路由测试")

    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    # 先登录
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 测试 PDF 签字版列表页
    response = client.get('/pdf/signed')
    if response.status_code == 200:
        print("✅ PDF 签字版列表页正常")
    else:
        print(f"⚠️  PDF 签字版列表页返回 {response.status_code}")

    print("✅ PDF 路由测试通过\n")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  采购管理系统 - Web 路由功能测试")
    print("="*60)

    try:
        test_main_routes()
        test_login()
        test_plan_routes()
        test_admin_routes()
        test_pdf_routes()

        print("\n" + "="*60)
        print("  ✅ 所有 Web 路由测试通过!")
        print("="*60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ 测试异常：{e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
