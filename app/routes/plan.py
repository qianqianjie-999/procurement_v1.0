"""
采购计划路由蓝图

包含采购计划的新建、编辑、删除、列表、详情等功能
"""
import json
from datetime import datetime
from sqlalchemy import desc
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, make_response
from flask_login import login_required, current_user
from app import db
from app.models import PurchasePlan, PurchaseItem, User, ApprovalLog
from app.forms import PurchasePlanForm, PurchaseItemForm
from app.utils.helpers import generate_plan_number, now


plan_bp = Blueprint('plan', __name__, url_prefix='/plans')


def parse_items_from_form():
    """
    从表单数据中解析物资明细数组（匹配 Excel 模板）

    前端提交的字段格式：
    - item_ids[]: [1, 2, 3] 或空数组（新建时）
    - item_names[]: ['物资 1', '物资 2']
    - brand_models[]: ['品牌型号 1', '品牌型号 2']
    - specifications[]: ['规格 1', '规格 2']
    - quantities[]: [10, 20]
    - units[]: ['个', '台']
    - batch_quantities[]: [5, 10]
    - extra_contract_quantities[]: [0, 0]
    - required_dates[]: ['2024-01-01', '2024-02-01']
    - remarks[]: ['备注 1', '备注 2']

    Returns:
        list: 物资明细字典列表
    """
    from flask import current_app

    items = []

    # 获取所有数组字段
    item_ids = request.form.getlist('item_ids[]')
    item_names = request.form.getlist('item_names[]')
    brand_models = request.form.getlist('brand_models[]')
    specifications = request.form.getlist('specifications[]')
    quantities = request.form.getlist('quantities[]')
    units = request.form.getlist('units[]')
    batch_quantities = request.form.getlist('batch_quantities[]')
    extra_contract_quantities = request.form.getlist('extra_contract_quantities[]')
    required_dates = request.form.getlist('required_dates[]')
    remarks = request.form.getlist('remarks[]')

    # 调试日志
    current_app.logger.info(f'表单提交数据：item_names={item_names}, quantities={quantities}')

    # 获取行数（以物品名称为准）
    row_count = len(item_names)

    for i in range(row_count):
        # 跳过空行
        if not item_names[i].strip():
            continue

        item_data = {
            'id': int(item_ids[i]) if i < len(item_ids) and item_ids[i].strip() else None,
            'item_name': item_names[i].strip() if i < len(item_names) else '',
            'brand_model': brand_models[i].strip() if i < len(brand_models) else '',
            'specification': specifications[i].strip() if i < len(specifications) else '',
            'quantity': float(quantities[i]) if i < len(quantities) and quantities[i] else 0,
            'unit': units[i].strip() if i < len(units) else '',
            'batch_quantity': float(batch_quantities[i]) if i < len(batch_quantities) and batch_quantities[i] else None,
            'extra_contract_quantity': float(extra_contract_quantities[i]) if i < len(extra_contract_quantities) and extra_contract_quantities[i] else None,
            'required_date': required_dates[i].strip() if i < len(required_dates) and required_dates[i] else None,
            'remarks': remarks[i].strip() if i < len(remarks) else ''
        }

        items.append(item_data)

    current_app.logger.info(f'解析后的物资明细：{items}')
    return items


def save_items(plan, items_data):
    """
    保存物资明细到数据库

    Args:
        plan: PurchasePlan 实例
        items_data: 物资明细字典列表
    """
    # 获取现有的物品 ID 列表
    existing_ids = set()

    for item_data in items_data:
        if item_data.get('id'):
            # 更新现有物品
            item = PurchaseItem.query.get(item_data['id'])
            if item and item.plan_id == plan.id:
                existing_ids.add(item.id)
                item.item_name = item_data['item_name']
                item.brand_model = item_data['brand_model']
                item.specification = item_data['specification']
                item.quantity = item_data['quantity']
                item.unit = item_data['unit']
                item.batch_quantity = item_data.get('batch_quantity')
                item.extra_contract_quantity = item_data.get('extra_contract_quantity')
                if item_data.get('required_date'):
                    item.required_date = datetime.strptime(item_data['required_date'], '%Y-%m-%d')
                item.remarks = item_data['remarks']
                item.updated_at = datetime.utcnow()
        else:
            # 创建新物品
            new_item = PurchaseItem(
                plan_id=plan.id,
                item_name=item_data['item_name'],
                brand_model=item_data['brand_model'],
                specification=item_data['specification'],
                quantity=item_data['quantity'],
                unit=item_data['unit'],
                batch_quantity=item_data.get('batch_quantity'),
                extra_contract_quantity=item_data.get('extra_contract_quantity'),
                remarks=item_data['remarks']
            )
            if item_data.get('required_date'):
                new_item.required_date = datetime.strptime(item_data['required_date'], '%Y-%m-%d')
            db.session.add(new_item)
            # 刷新以获取新物品的 ID
            db.session.flush()
            existing_ids.add(new_item.id)

    # 删除不在提交数据中的物品
    for item in plan.items:
        if item.id not in existing_ids:
            db.session.delete(item)


@plan_bp.route('/')
@login_required
def index():
    """采购计划列表页"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 20)

    # 获取筛选参数
    status_filter = request.args.get('status', '', type=str)
    search = request.args.get('search', '', type=str)

    # 查询当前用户的采购计划
    query = PurchasePlan.query.filter_by(created_by=current_user.id)

    # 管理员可以看到所有计划
    if current_user.is_administrator():
        query = PurchasePlan.query

    # 应用状态筛选
    if status_filter:
        query = query.filter_by(status=status_filter)

    # 应用搜索（计划名称或编号）
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                PurchasePlan.plan_name.like(search_pattern),
                PurchasePlan.plan_number.like(search_pattern)
            )
        )

    query = query.order_by(PurchasePlan.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    plans = pagination.items

    # 统计数据（不受筛选影响，显示用户所有计划）
    base_query = PurchasePlan.query.filter_by(created_by=current_user.id)
    if current_user.is_administrator():
        base_query = PurchasePlan.query

    stats = {
        'total': base_query.count(),
        'draft': base_query.filter_by(status='draft').count(),
        'pending': base_query.filter_by(status='pending').count(),
        'approved': base_query.filter_by(status='approved').count()
    }

    return render_template('plan/plan_list.html',
                          plans=plans,
                          pagination=pagination,
                          stats=stats,
                          plan_types=dict(PurchasePlan.PLAN_TYPES))


@plan_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """
    创建新的采购计划

    GET: 显示空表单
    POST: 处理表单提交，保存采购计划和物资明细
    """
    form = PurchasePlanForm()

    if request.method == 'POST':
        # 验证主表单
        if form.validate():
            # 解析物资明细
            items_data = parse_items_from_form()

            # 检查是否有物资明细
            if not items_data:
                flash('请至少添加一项物资明细。', 'warning')
                return render_template('plan/plan_form.html', form=form, items=[], edit_mode=False)

            # 创建采购计划
            plan = PurchasePlan(
                plan_number=generate_plan_number(),
                plan_name=form.plan_name.data,
                project_manager=form.project_manager.data,
                description=form.description.data,
                created_by=current_user.id,
                status='draft'  # 默认为草稿状态
            )

            # 设置日期
            if form.start_date.data:
                plan.start_date = form.start_date.data
            if form.end_date.data:
                plan.end_date = form.end_date.data

            # 检查是否点击了"保存并提交审批"
            if 'submit_and_submit' in request.form:
                plan.status = 'pending'
                plan.submitted_at = datetime.utcnow()

            db.session.add(plan)
            db.session.flush()  # 获取 plan.id

            # 保存物资明细
            save_items(plan, items_data)

            # 计算实际金额
            plan.actual_amount = plan.calculate_total_amount()

            db.session.commit()

            flash('采购计划创建成功！', 'success')
            return redirect(url_for('plan.detail', id=plan.id))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    # GET 请求或验证失败，显示表单
    # 初始化一行空物资
    initial_items = [{
        'item_name': '',
        'brand_model': '',
        'specification': '',
        'quantity': 1,
        'unit': '',
        'batch_quantity': None,
        'extra_contract_quantity': None,
        'required_date': None,
        'remarks': ''
    }]

    return render_template('plan/plan_form.html', form=form, items=initial_items, edit_mode=False)


@plan_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    编辑采购计划

    GET: 显示预填充表单
    POST: 处理表单提交，更新采购计划和物资明细
    """
    plan = PurchasePlan.query.get_or_404(id)

    # 权限检查：只有创建者或管理员可以编辑
    if plan.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限编辑此采购计划。', 'danger')
        return redirect(url_for('plan.index'))

    # 草稿状态才能编辑
    if plan.status not in ['draft', 'rejected']:
        flash('只有草稿或被拒绝的计划可以编辑。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    form = PurchasePlanForm(obj=plan)

    if request.method == 'POST':
        if form.validate():
            # 解析物资明细
            items_data = parse_items_from_form()

            if not items_data:
                flash('请至少添加一项物资明细。', 'warning')
                return render_template('plan/plan_form.html', form=form, items=list(plan.items), edit_mode=True, plan=plan)

            # 更新采购计划
            plan.plan_name = form.plan_name.data
            plan.project_manager = form.project_manager.data
            plan.description = form.description.data

            # 设置日期
            plan.start_date = form.start_date.data
            plan.end_date = form.end_date.data

            # 如果重新提交，更新状态
            if 'submit_and_submit' in request.form:
                plan.status = 'pending'
                plan.submitted_at = datetime.utcnow()
            elif plan.status == 'pending':
                # 如果只是保存，保持草稿状态
                plan.status = 'draft'

            plan.updated_at = datetime.utcnow()

            # 保存物资明细
            save_items(plan, items_data)

            # 计算实际金额
            plan.actual_amount = plan.calculate_total_amount()

            db.session.commit()

            flash('采购计划更新成功！', 'success')
            return redirect(url_for('plan.detail', id=plan.id))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    # GET 请求或验证失败，显示表单
    items = []
    for item in plan.items:
        items.append({
            'id': item.id,
            'item_name': item.item_name,
            'brand_model': item.brand_model,
            'specification': item.specification,
            'quantity': float(item.quantity),
            'unit': item.unit,
            'batch_quantity': float(item.batch_quantity) if item.batch_quantity else None,
            'extra_contract_quantity': float(item.extra_contract_quantity) if item.extra_contract_quantity else None,
            'required_date': item.required_date.strftime('%Y-%m-%d') if item.required_date else None,
            'remarks': item.remarks
        })

    return render_template('plan/plan_form.html',
                          form=form,
                          items=items,
                          edit_mode=True,
                          plan=plan)


@plan_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """采购计划详情页"""
    plan = PurchasePlan.query.get_or_404(id)
    # 预先加载审批日志，按时间倒序排序
    approval_logs = plan.approval_logs.order_by(desc(ApprovalLog.created_at)).all()
    # 预先加载物资明细
    items = plan.items.all()
    return render_template('plan/plan_detail.html', plan=plan, approval_logs=approval_logs, items=items)


@plan_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """删除采购计划"""
    plan = PurchasePlan.query.get_or_404(id)

    # 权限检查
    if plan.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限删除此采购计划。', 'danger')
        return redirect(url_for('plan.index'))

    # 只有草稿状态可以删除
    if plan.status not in ['draft', 'cancelled']:
        flash('只有草稿或已取消的计划可以删除。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    db.session.delete(plan)
    db.session.commit()

    flash('采购计划已删除。', 'success')
    return redirect(url_for('plan.index'))


@plan_bp.route('/<int:id>/submit', methods=['POST'])
@login_required
def submit(id):
    """提交采购计划审批"""
    plan = PurchasePlan.query.get_or_404(id)

    # 权限检查
    if plan.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限提交此采购计划。', 'danger')
        return redirect(url_for('plan.index'))

    # 只有草稿状态可以提交
    if plan.status != 'draft':
        flash('只有草稿状态的计划可以提交审批。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    # 检查是否有物资明细
    if plan.items.count() == 0:
        flash('采购计划必须包含至少一项物资。', 'warning')
        return redirect(url_for('plan.edit', id=plan.id))

    plan.status = 'pending'
    plan.submitted_at = datetime.utcnow()
    db.session.commit()

    flash('采购计划已提交审批。', 'success')
    return redirect(url_for('plan.detail', id=plan.id))


@plan_bp.route('/<int:id>/preview', methods=['GET'])
@login_required
def preview(id):
    """
    采购计划预览页 - 精确还原 Excel 模板样式

    显示与 Excel 模板样式完全一致的采购计划预览页面
    """
    plan = PurchasePlan.query.get_or_404(id)
    items = plan.items.order_by(PurchaseItem.id).all()

    return render_template('plan/plan_preview.html', plan=plan, items=items)


@plan_bp.route('/<int:id>/export-pdf', methods=['GET'])
@login_required
def export_pdf(id):
    """
    导出采购计划为 PDF - 直接下载不保存
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        flash('未安装 WeasyPrint，请先运行：pip install weasyprint', 'warning')
        return redirect(url_for('plan.plan_list'))

    plan = PurchasePlan.query.get_or_404(id)
    items = plan.items.order_by(PurchaseItem.id).all()

    # 获取配置
    chinese_font_path = current_app.config.get('CHINESE_FONT_PATH')

    # 渲染简化的 HTML 模板（专为 PDF 优化）
    html_content = render_template('plan/plan_pdf.html', plan=plan, items=items)

    # 生成 PDF - 优化性能
    try:
        html = HTML(string=html_content)

        # 优化：使用 FontConfiguration 预加载字体，加快渲染速度
        font_config = FontConfiguration()
        if chinese_font_path:
            css = CSS(string=f"""
                @font-face {{
                    font-family: 'SimSun';
                    src: url('file://{chinese_font_path}');
                }}
                body {{ font-family: 'SimSun', sans-serif; }}
            """, font_config=font_config)
            pdf_file = html.write_pdf(
                stylesheets=[css],
                font_config=font_config,
                optimize_size=('fonts', 'images'),
                zoom=1.0
            )
        else:
            pdf_file = html.write_pdf(optimize_size=('fonts', 'images'))

        # 直接返回 PDF 下载，不保存到服务器
        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={plan.plan_number}_purchase_plan.pdf'
        response.headers['Content-Length'] = str(len(pdf_file))

        return response

    except Exception as e:
        current_app.logger.error(f'PDF 生成失败：{str(e)}')
        flash(f'生成 PDF 失败：{str(e)}', 'danger')
        return redirect(url_for('plan.preview', id=id))


@plan_bp.route('/<int:id>/upload', methods=['POST'])
@login_required
def upload_scanned(id):
    """
    上传签字后的扫描件 PDF

    处理用户上传的扫描件文件，保存到服务器并更新数据库
    """
    import os
    from datetime import datetime
    from werkzeug.utils import secure_filename

    plan = PurchasePlan.query.get_or_404(id)

    # 权限检查：只有创建者或管理员可以上传
    if plan.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限上传此计划的扫描件。', 'danger')
        return redirect(url_for('plan.detail', id=plan.id))

    # 检查是否有文件
    if 'scanned_file' not in request.files:
        flash('没有选择文件。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    file = request.files['scanned_file']

    if file.filename == '':
        flash('没有选择文件。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    # 验证文件类型
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_SCANNED_EXTENSIONS', {'pdf'})

    if not allowed_file(file.filename):
        flash('只允许上传 PDF 文件。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    # 获取存储路径
    scanned_storage_path = current_app.config.get('SCANNED_STORAGE_PATH')
    os.makedirs(scanned_storage_path, exist_ok=True)

    # 生成文件名：采购计划 ID_时间戳.pdf
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    safe_filename = secure_filename(file.filename)
    # 确保文件名以.pdf 结尾
    if not safe_filename.lower().endswith('.pdf'):
        safe_filename = f"{plan.id}_{timestamp}.pdf"

    scanned_filename = f"{plan.id}_{timestamp}_{safe_filename}"
    scanned_filepath = os.path.join(scanned_storage_path, scanned_filename)
    scanned_relative_path = f"static/scanned/{scanned_filename}"

    try:
        # 保存文件
        file.save(scanned_filepath)

        # 检查文件大小
        file_size = os.path.getsize(scanned_filepath)
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)

        if file_size > max_size:
            # 文件过大，删除并返回错误
            os.remove(scanned_filepath)
            flash(f'文件过大，最大允许 10MB。当前大小：{file_size / 1024 / 1024:.2f}MB', 'danger')
            return redirect(url_for('plan.detail', id=plan.id))

        # 更新数据库，如果有旧的扫描件，删除旧文件
        if plan.scanned_path:
            project_root = os.path.dirname(current_app.root_path)
            old_scanned_path = os.path.join(project_root, plan.scanned_path)
            if os.path.exists(old_scanned_path):
                try:
                    os.remove(old_scanned_path)
                except Exception as e:
                    current_app.logger.warning(f'删除旧扫描件失败：{e}')

        plan.scanned_path = scanned_relative_path
        db.session.commit()

        current_app.logger.info(f'扫描件上传成功：{scanned_filepath}')
        flash('扫描件上传成功！', 'success')

    except Exception as e:
        current_app.logger.error(f'扫描件上传失败：{str(e)}')
        flash(f'上传失败：{str(e)}', 'danger')

    return redirect(url_for('plan.detail', id=plan.id))


@plan_bp.route('/<int:id>/download-scanned', methods=['GET'])
@login_required
def download_scanned(id):
    """
    下载已上传的扫描件 PDF
    """
    from flask import send_file
    import os

    plan = PurchasePlan.query.get_or_404(id)

    if not plan.scanned_path:
        flash('未找到扫描件。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    # 构建文件路径 - 使用项目根目录（app 的父目录）
    project_root = os.path.dirname(current_app.root_path)
    scanned_filepath = os.path.join(project_root, plan.scanned_path)

    if not os.path.exists(scanned_filepath):
        flash('扫描件文件不存在。', 'danger')
        return redirect(url_for('plan.detail', id=plan.id))

    return send_file(
        scanned_filepath,
        as_attachment=True,
        download_name=f'{plan.plan_number}_scanned.pdf'
    )


@plan_bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    """
    审批采购计划

    只有管理员或授权审批人可以审批
    """
    plan = PurchasePlan.query.get_or_404(id)

    # 权限检查：只有管理员可以审批
    if not current_user.is_administrator():
        flash('您没有权限审批采购计划。', 'danger')
        return redirect(url_for('plan.detail', id=plan.id))

    # 只有待审批状态可以审批
    if plan.status != 'pending':
        flash('只有待审批状态的计划可以审批。', 'warning')
        return redirect(url_for('plan.detail', id=plan.id))

    action = request.form.get('action', 'approve')
    comments = request.form.get('comments', '')

    # 记录审批日志
    approval_log = ApprovalLog(
        plan_id=plan.id,
        action=action,
        previous_status=plan.status,
        operator_id=current_user.id,
        comments=comments
    )
    db.session.add(approval_log)

    if action == 'approve':
        # 同意审批
        plan.status = 'approved'
        plan.approved_by = current_user.id
        plan.approved_at = datetime.utcnow()
        flash('采购计划已批准。', 'success')
    elif action == 'reject':
        # 拒绝审批
        plan.status = 'rejected'
        flash('采购计划已被拒绝。', 'warning')

    db.session.commit()

    return redirect(url_for('plan.detail', id=plan.id))
