from flask import Blueprint, render_template, jsonify
from flask_login import current_user
from app.models import PurchasePlan

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页路由"""
    # 如果已登录，显示统计信息
    plan_stats = None
    if current_user.is_authenticated:
        if current_user.is_administrator():
            # 管理员查看所有计划
            plan_stats = {
                'total': PurchasePlan.query.count(),
                'draft': PurchasePlan.query.filter_by(status='draft').count(),
                'pending': PurchasePlan.query.filter_by(status='pending').count(),
                'approved': PurchasePlan.query.filter_by(status='approved').count()
            }
        else:
            # 普通用户只查看自己的计划
            plan_stats = {
                'total': PurchasePlan.query.filter_by(created_by=current_user.id).count(),
                'draft': PurchasePlan.query.filter_by(created_by=current_user.id, status='draft').count(),
                'pending': PurchasePlan.query.filter_by(created_by=current_user.id, status='pending').count(),
                'approved': PurchasePlan.query.filter_by(created_by=current_user.id, status='approved').count()
            }

    return render_template('index.html', plan_stats=plan_stats)


@main_bp.route('/health')
def health():
    """健康检查路由"""
    return jsonify({
        'status': 'healthy',
        'message': 'Procurement System is running'
    })
