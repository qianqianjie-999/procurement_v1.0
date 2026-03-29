from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import PurchasePlan

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """仪表板页面"""
    # 获取用户统计信息
    plan_stats = {
        'total': PurchasePlan.query.filter_by(created_by=current_user.id).count(),
        'approved': PurchasePlan.query.filter_by(created_by=current_user.id, status='approved').count(),
        'pending': PurchasePlan.query.filter_by(created_by=current_user.id, status='pending').count(),
        'draft': PurchasePlan.query.filter_by(created_by=current_user.id, status='draft').count(),
    }
    
    # 获取最近的采购计划（最多5条）
    recent_plans = PurchasePlan.query.filter_by(created_by=current_user.id)\
        .order_by(PurchasePlan.created_at.desc())\
        .limit(5)\
        .all()
    
    return render_template('main/dashboard.html', 
                         plan_stats=plan_stats, 
                         recent_plans=recent_plans)