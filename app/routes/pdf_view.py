"""
PDF签字版查看路由
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app.models import PurchasePlan
from app import db

pdf_bp = Blueprint('pdf', __name__, url_prefix='/pdf')

@pdf_bp.route('/signed')
@login_required
def signed_pdf_view():
    """PDF签字版查看页面 - 显示当前用户的所有采购计划的签字版状态"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 查询当前用户的所有采购计划（管理员可以看到所有计划）
    if current_user.is_administrator():
        query = PurchasePlan.query
    else:
        query = PurchasePlan.query.filter_by(created_by=current_user.id)
    
    # 按创建时间倒序排列
    plans = query.order_by(PurchasePlan.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    response = make_response(render_template('pdf/signed_pdf_view.html', plans=plans))
    # 禁止浏览器缓存，确保每次都从服务器获取最新数据
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response