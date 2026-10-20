from datetime import datetime

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from app.models import PurchasePlan, ApprovalFlow, ApprovalStep

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """仪表板页面 - 重设计版面：KPI 总览 + 最近计划 + 待办审批 + 状态分布"""
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 数据范围：管理员看全部，普通用户看自己的
    if current_user.is_administrator():
        base_query = PurchasePlan.query
        scope_label = '全部数据'
    else:
        base_query = PurchasePlan.query.filter_by(created_by=current_user.id)
        scope_label = '我的数据'

    # 各状态计划数（单次分组查询）
    status_counts = dict(
        base_query
        .with_entities(PurchasePlan.status, func.count(PurchasePlan.id))
        .group_by(PurchasePlan.status)
        .all()
    )
    plan_stats = {
        'total': sum(status_counts.values()),
        'draft': status_counts.get('draft', 0),
        'pending': status_counts.get('pending', 0),
        'approved': status_counts.get('approved', 0),
        'rejected': status_counts.get('rejected', 0),
        'completed': status_counts.get('completed', 0),
        'cancelled': status_counts.get('cancelled', 0),
    }

    # 本月新增
    month_new = base_query.filter(PurchasePlan.created_at >= month_start).count()

    # 最近采购计划
    recent_plans = base_query.order_by(
        PurchasePlan.created_at.desc()
    ).limit(8).all()

    # 待我审批（流程进行中且分配给我的待办步骤）
    my_tasks = (
        db.session.query(ApprovalStep, ApprovalFlow, PurchasePlan)
        .join(ApprovalFlow, ApprovalStep.flow_id == ApprovalFlow.id)
        .join(PurchasePlan, ApprovalFlow.plan_id == PurchasePlan.id)
        .filter(
            ApprovalStep.approver_id == current_user.id,
            ApprovalStep.status == 'pending',
            ApprovalFlow.status.in_(['pending', 'in_progress']),
        )
        .order_by(ApprovalStep.assigned_at.desc())
        .limit(6)
        .all()
    )

    # 状态分布（用于迷你条形图，按固定顺序）
    status_dist = [
        ('pending', '待审批', plan_stats['pending'], 'warning'),
        ('approved', '已批准', plan_stats['approved'], 'success'),
        ('draft', '草稿', plan_stats['draft'], 'secondary'),
        ('rejected', '已拒绝', plan_stats['rejected'], 'danger'),
        ('completed', '已完成', plan_stats['completed'], 'info'),
        ('cancelled', '已取消', plan_stats['cancelled'], 'dark'),
    ]

    return render_template(
        'main/dashboard.html',
        plan_stats=plan_stats,
        month_new=month_new,
        recent_plans=recent_plans,
        my_tasks=my_tasks,
        status_dist=status_dist,
        scope_label=scope_label,
        now=now,
    )
