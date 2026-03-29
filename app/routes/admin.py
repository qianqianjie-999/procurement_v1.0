"""
管理员功能路由蓝图

包含用户管理、系统设置等功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, PurchasePlan
from app.forms import UserForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    """确保只有管理员可以访问这些路由"""
    if not current_user.is_administrator():
        flash('您没有权限访问此页面。', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/users')
def users():
    """用户管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
def toggle_user_active(user_id):
    """切换用户激活状态"""
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