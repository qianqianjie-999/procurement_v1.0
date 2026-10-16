"""
管理员功能路由蓝图

包含用户管理、系统设置等功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (
    User, PurchasePlan, ApprovalLog, ApprovalRequest, ApprovalStep,
)
from app.forms import UserForm
from wtforms import ValidationError

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    """确保只有管理员可以访问这些路由"""
    if not current_user.is_administrator():
        flash('您没有权限访问此页面。', 'danger')
        return redirect(url_for('main.index'))

def validate_ajax_csrf():
    """验证AJAX请求的CSRF token

    优先从请求头取（GET/DELETE 等无 body 请求只能从头取），
    其次才从 JSON/表单请求体取，不依赖 request.is_json。
    """
    csrf_token = request.headers.get('X-CSRF-Token') or request.headers.get('X-CSRFToken')
    if not csrf_token:
        if request.is_json:
            csrf_token = (request.get_json(silent=True) or {}).get('csrf_token')
        else:
            csrf_token = request.form.get('csrf_token')
    if not csrf_token:
        return False
    from flask_wtf.csrf import validate_csrf
    try:
        validate_csrf(csrf_token)
        return True
    except ValidationError:
        return False

@admin_bp.route('/users')
def users():
    """用户管理页面"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['POST'])
def create_user():
    """管理员创建用户"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    data = request.json

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    department = data.get('department', '').strip()
    role = data.get('role', 'user')

    if not username or not email or not password:
        return jsonify({'success': False, 'message': '用户名、邮箱和密码不能为空'})

    if len(username) < 3 or len(username) > 20:
        return jsonify({'success': False, 'message': '用户名长度应为 3-20 个字符'})

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少 6 位'})

    if role not in ['user', 'admin']:
        return jsonify({'success': False, 'message': '无效的角色'})

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'})

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'})

    user = User(
        username=username,
        email=email,
        full_name=full_name if full_name else None,
        department=department if department else None,
        role=role
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'success': True, 'message': f'用户 {username} 创建成功'})

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
def toggle_user_active(user_id):
    """切换用户激活状态"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能禁用自己的账户'})
    
    user.is_active_field = not user.is_active_field
    db.session.commit()
    
    status = '已激活' if user.is_active_field else '已禁用'
    return jsonify({'success': True, 'message': f'用户 {user.username} {status}', 'active': user.is_active_field})

@admin_bp.route('/users/<int:user_id>/set-role', methods=['POST'])
def set_user_role(user_id):
    """设置用户角色"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能修改自己的角色'})
    
    role = request.json.get('role', 'user')
    if role not in ['user', 'admin']:
        return jsonify({'success': False, 'message': '无效的角色'})
    
    user.role = role
    db.session.commit()
    
    role_name = '管理员' if role == 'admin' else '普通用户'
    return jsonify({'success': True, 'message': f'用户 {user.username} 角色已更新为 {role_name}'})

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户详情（供编辑模态框填充）"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    user = User.query.get_or_404(user_id)
    return jsonify({'success': True, 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息（姓名、邮箱、部门、角色、状态、可选新密码）"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    user = User.query.get_or_404(user_id)
    data = request.json or {}

    # 姓名
    if 'full_name' in data:
        user.full_name = data['full_name'].strip() or None

    # 邮箱（需保持唯一，排除自身）
    if 'email' in data:
        new_email = data['email'].strip()
        if not new_email:
            return jsonify({'success': False, 'message': '邮箱不能为空'}), 400
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
        user.email = new_email

    # 部门
    if 'department' in data:
        user.department = data['department'].strip() or None

    # 角色
    if 'role' in data:
        new_role = data['role']
        if new_role not in ['user', 'admin']:
            return jsonify({'success': False, 'message': '无效的角色'}), 400
        if user.id == current_user.id and new_role != 'admin':
            return jsonify({'success': False, 'message': '不能取消自己的管理员角色'}), 400
        user.role = new_role

    # 启用/禁用状态
    if 'is_active' in data:
        if user.id == current_user.id and not data['is_active']:
            return jsonify({'success': False, 'message': '不能禁用自己的账户'}), 400
        user.is_active_field = bool(data['is_active'])

    # 可选新密码
    new_password = data.get('new_password')
    if new_password:
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少 6 位'}), 400
        user.set_password(new_password)

    db.session.commit()
    return jsonify({'success': True, 'message': '用户更新成功', 'user': user.to_dict()})

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户（不能删自己；存在任何业务关联记录时禁止删除）"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    if user_id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除自己的账户'}), 400

    user = User.query.get_or_404(user_id)

    # users 表被 5 个外键引用（数据库均为 RESTRICT），任一存在记录都不能删，
    # 否则 commit 时会抛外键约束错误（500）。这里统一前置校验并给出可读提示。
    refs = []
    created_plans = PurchasePlan.query.filter_by(created_by=user_id).count()
    if created_plans:
        refs.append(f'{created_plans} 条采购计划')
    approved_plans = PurchasePlan.query.filter_by(approved_by=user_id).count()
    if approved_plans:
        refs.append(f'{approved_plans} 条审批记录')
    logs = ApprovalLog.query.filter_by(operator_id=user_id).count()
    if logs:
        refs.append(f'{logs} 条审批日志')
    approval_requests = ApprovalRequest.query.filter_by(created_by=user_id).count()
    if approval_requests:
        refs.append(f'{approval_requests} 条审批申请')
    steps = ApprovalStep.query.filter_by(approver_id=user_id).count()
    if steps:
        refs.append(f'{steps} 个审批节点')

    if refs:
        return jsonify({
            'success': False,
            'message': f'该用户关联了 {"、".join(refs)}，无法删除。建议改用「禁用」保留历史记录。'
        }), 400

    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': f'用户 {user.username} 已删除'})

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_user_password(user_id):
    """管理员重置用户密码"""
    if not validate_ajax_csrf():
        return jsonify({'success': False, 'message': 'CSRF验证失败'}), 403

    user = User.query.get_or_404(user_id)
    data = request.json or {}
    new_password = data.get('new_password', '')

    if not new_password:
        return jsonify({'success': False, 'message': '新密码不能为空'}), 400
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少 6 位'}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': '密码重置成功'})

@admin_bp.route('/reports')
def reports():
    """统计报表页面"""
    # 获取基础统计数据
    total_users = User.query.count()
    total_plans = PurchasePlan.query.count()
    approved_plans = PurchasePlan.query.filter_by(status='approved').count()
    pending_plans = PurchasePlan.query.filter_by(status='pending').count()
    
    # 按状态统计
    status_stats = {
        'draft': PurchasePlan.query.filter_by(status='draft').count(),
        'pending': pending_plans,
        'approved': approved_plans,
        'rejected': PurchasePlan.query.filter_by(status='rejected').count(),
        'cancelled': PurchasePlan.query.filter_by(status='cancelled').count(),
        'completed': PurchasePlan.query.filter_by(status='completed').count(),
    }
    
    # 按用户统计（前10名）
    top_users = db.session.query(
        User.username,
        db.func.count(PurchasePlan.id).label('plan_count')
    ).join(PurchasePlan, User.id == PurchasePlan.created_by)\
     .group_by(User.id, User.username)\
     .order_by(db.desc('plan_count'))\
     .limit(10).all()
    
    # 按项目名称统计（前10名）
    top_projects = db.session.query(
        PurchasePlan.plan_name,
        db.func.count(PurchasePlan.id).label('plan_count')
    ).group_by(PurchasePlan.plan_name)\
     .order_by(db.desc('plan_count'))\
     .limit(10).all()
    
    # 按项目经理统计（前10名）
    top_managers = db.session.query(
        PurchasePlan.project_manager,
        db.func.count(PurchasePlan.id).label('plan_count')
    ).filter(PurchasePlan.project_manager.isnot(None))\
     .group_by(PurchasePlan.project_manager)\
     .order_by(db.desc('plan_count'))\
     .limit(10).all()
    
    return render_template('admin/reports.html', 
                         total_users=total_users,
                         total_plans=total_plans,
                         status_stats=status_stats,
                         top_users=top_users,
                         top_projects=top_projects,
                         top_managers=top_managers)

@admin_bp.route('/settings')
def settings():
    """系统设置页面"""
    return render_template('admin/settings.html')

# @admin_bp.route('/pdf-export')
# @login_required
# def pdf_export():
#     """PDF查看页面 - 显示当前用户的所有采购计划的签字版状态"""
#     page = request.args.get('page', 1, type=int)
#     per_page = 20
#     
#     # 查询当前用户的所有采购计划
#     query = PurchasePlan.query.filter_by(created_by=current_user.id)
#     
#     # 管理员可以看到所有计划
#     if current_user.is_administrator():
#         query = PurchasePlan.query
#     
#     # 按创建时间倒序排列
#     plans = query.order_by(PurchasePlan.created_at.desc())\
#         .paginate(page=page, per_page=per_page, error_out=False)
#     
#     return render_template('admin/pdf_export.html', plans=plans)