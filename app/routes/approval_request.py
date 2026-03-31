"""
事务审批单路由蓝图

包含事务审批单的创建、列表、详情、导出 PDF、上传扫描件等功能
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, make_response, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import ApprovalRequest, User
from app.forms import ApprovalRequestForm
from app.utils.helpers import now

approval_request_bp = Blueprint('approval_request', __name__, url_prefix='/approval-requests')


def generate_request_number():
    """生成审批单编号"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"SP-{timestamp}"


@approval_request_bp.route('/')
@login_required
def index():
    """事务审批单列表页"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 20)

    # 获取筛选参数
    status_filter = request.args.get('status', '', type=str)

    # 查询当前用户的审批单
    query = ApprovalRequest.query.filter_by(created_by=current_user.id)

    # 管理员可以看到所有审批单
    if current_user.is_administrator():
        query = ApprovalRequest.query

    # 应用状态筛选
    if status_filter:
        query = query.filter_by(status=status_filter)

    query = query.order_by(ApprovalRequest.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    requests = pagination.items

    # 统计数据
    base_query = ApprovalRequest.query.filter_by(created_by=current_user.id)
    if current_user.is_administrator():
        base_query = ApprovalRequest.query

    stats = {
        'total': base_query.count(),
        'draft': base_query.filter_by(status='draft').count(),
        'pending': base_query.filter_by(status='pending').count(),
        'approved': base_query.filter_by(status='approved').count()
    }

    return render_template('approval_request/list.html',
                          requests=requests,
                          pagination=pagination,
                          stats=stats)


@approval_request_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """
    创建新的事务审批单

    GET: 显示空表单
    POST: 处理表单提交，保存审批单
    """
    form = ApprovalRequestForm()

    if request.method == 'POST':
        if form.validate():
            # 创建审批单
            approval_request = ApprovalRequest(
                request_number=generate_request_number(),
                subject=form.subject.data,
                content=form.content.data,
                department=form.department.data,
                applicant_name=form.applicant_name.data,
                created_by=current_user.id,
                status='draft'
            )

            # 检查是否点击了"提交审批"
            if 'submit_and_submit' in request.form:
                approval_request.status = 'pending'
                approval_request.submitted_at = datetime.utcnow()

            db.session.add(approval_request)
            db.session.commit()

            flash('事务审批单创建成功！', 'success')
            return redirect(url_for('approval_request.detail', id=approval_request.id))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    return render_template('approval_request/form.html', form=form)


@approval_request_bp.route('/<int:id>', methods=['GET'])
@login_required
def detail(id):
    """事务审批单详情页"""
    approval_request = ApprovalRequest.query.get_or_404(id)
    return render_template('approval_request/detail.html', approval_request=approval_request)


@approval_request_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    编辑事务审批单

    只有草稿状态可以编辑
    """
    approval_request = ApprovalRequest.query.get_or_404(id)

    # 权限检查
    if approval_request.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限编辑此审批单。', 'danger')
        return redirect(url_for('approval_request.index'))

    # 只有草稿状态可以编辑
    if approval_request.status not in ['draft']:
        flash('只有草稿状态的审批单可以编辑。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    form = ApprovalRequestForm(obj=approval_request)

    if request.method == 'POST':
        if form.validate():
            approval_request.subject = form.subject.data
            approval_request.content = form.content.data
            approval_request.department = form.department.data
            approval_request.applicant_name = form.applicant_name.data

            if 'submit_and_submit' in request.form:
                approval_request.status = 'pending'
                approval_request.submitted_at = datetime.utcnow()

            db.session.commit()
            flash('事务审批单更新成功！', 'success')
            return redirect(url_for('approval_request.detail', id=approval_request.id))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    return render_template('approval_request/form.html', form=form, request=approval_request)


@approval_request_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """删除事务审批单"""
    approval_request = ApprovalRequest.query.get_or_404(id)

    # 权限检查
    if approval_request.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限删除此审批单。', 'danger')
        return redirect(url_for('approval_request.index'))

    # 只有草稿状态可以删除
    if approval_request.status not in ['draft']:
        flash('只有草稿状态的审批单可以删除。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    db.session.delete(approval_request)
    db.session.commit()

    flash('事务审批单已删除。', 'success')
    return redirect(url_for('approval_request.index'))


@approval_request_bp.route('/<int:id>/submit', methods=['POST'])
@login_required
def submit(id):
    """提交事务审批单审批"""
    approval_request = ApprovalRequest.query.get_or_404(id)

    # 权限检查
    if approval_request.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限提交此审批单。', 'danger')
        return redirect(url_for('approval_request.index'))

    # 只有草稿状态可以提交
    if approval_request.status != 'draft':
        flash('只有草稿状态的审批单可以提交审批。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    approval_request.status = 'pending'
    approval_request.submitted_at = datetime.utcnow()
    db.session.commit()

    flash('事务审批单已提交审批。', 'success')
    return redirect(url_for('approval_request.detail', id=approval_request.id))


@approval_request_bp.route('/<int:id>/export-pdf', methods=['GET'])
@login_required
def export_pdf(id):
    """导出事务审批单为 PDF"""
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        flash('未安装 WeasyPrint，请先运行：pip install weasyprint', 'warning')
        return redirect(url_for('approval_request.index'))

    approval_request = ApprovalRequest.query.get_or_404(id)

    # 获取配置
    chinese_font_path = current_app.config.get('CHINESE_FONT_PATH')

    # 渲染 HTML 模板
    html_content = render_template('approval_request/pdf.html', approval_request=approval_request)

    # 生成 PDF
    try:
        html = HTML(string=html_content)

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

        response = make_response(pdf_file)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={approval_request.request_number}_approval_request.pdf'
        response.headers['Content-Length'] = str(len(pdf_file))

        return response

    except Exception as e:
        current_app.logger.error(f'PDF 生成失败：{str(e)}')
        flash(f'生成 PDF 失败：{str(e)}', 'danger')
        return redirect(url_for('approval_request.detail', id=id))


@approval_request_bp.route('/<int:id>/upload', methods=['POST'])
@login_required
def upload_scanned(id):
    """上传签字后的扫描件 PDF"""
    approval_request = ApprovalRequest.query.get_or_404(id)

    # 权限检查
    if approval_request.created_by != current_user.id and not current_user.is_administrator():
        flash('您没有权限上传此审批单的扫描件。', 'danger')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    # 检查是否有文件
    if 'scanned_file' not in request.files:
        flash('没有选择文件。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    file = request.files['scanned_file']

    if file.filename == '':
        flash('没有选择文件。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    # 验证文件类型
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_SCANNED_EXTENSIONS', {'pdf'})

    if not allowed_file(file.filename):
        flash('只允许上传 PDF 文件。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    # 获取存储路径
    scanned_storage_path = current_app.config.get('SCANNED_STORAGE_PATH')
    os.makedirs(scanned_storage_path, exist_ok=True)

    # 生成文件名
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    safe_filename = secure_filename(file.filename)
    if not safe_filename.lower().endswith('.pdf'):
        safe_filename = f"{approval_request.id}_{timestamp}.pdf"

    scanned_filename = f"{approval_request.id}_{timestamp}_{safe_filename}"
    scanned_filepath = os.path.join(scanned_storage_path, scanned_filename)
    scanned_relative_path = f"static/uploads/scanned/{scanned_filename}"

    try:
        # 保存文件
        file.save(scanned_filepath)

        # 检查文件大小
        file_size = os.path.getsize(scanned_filepath)
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)

        if file_size > max_size:
            os.remove(scanned_filepath)
            flash(f'文件过大，最大允许 10MB。', 'danger')
            return redirect(url_for('approval_request.detail', id=approval_request.id))

        # 删除旧扫描件
        if approval_request.scanned_path:
            project_root = os.path.dirname(current_app.root_path)
            old_scanned_path = os.path.join(project_root, approval_request.scanned_path)
            if os.path.exists(old_scanned_path):
                try:
                    os.remove(old_scanned_path)
                except Exception as e:
                    current_app.logger.warning(f'删除旧扫描件失败：{e}')

        approval_request.scanned_path = scanned_relative_path
        db.session.commit()

        current_app.logger.info(f'扫描件上传成功：{scanned_filepath}')
        flash('扫描件上传成功！', 'success')

    except Exception as e:
        current_app.logger.error(f'扫描件上传失败：{str(e)}')
        flash(f'上传失败：{str(e)}', 'danger')

    return redirect(url_for('approval_request.detail', id=approval_request.id))


@approval_request_bp.route('/<int:id>/view-scanned', methods=['GET'])
@login_required
def view_scanned(id):
    """在线查看已上传的扫描件 PDF"""
    approval_request = ApprovalRequest.query.get_or_404(id)

    if not approval_request.scanned_path:
        flash('未找到扫描件。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    scanned_filepath = os.path.join(current_app.root_path, approval_request.scanned_path)

    if not os.path.exists(scanned_filepath):
        flash('扫描件文件不存在。', 'danger')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    return send_file(
        scanned_filepath,
        as_attachment=False,
        download_name=f'{approval_request.request_number}_scanned.pdf'
    )


@approval_request_bp.route('/<int:id>/approve', methods=['POST'])
@login_required
def approve(id):
    """
    审批事务审批单

    只有管理员可以审批
    """
    approval_request = ApprovalRequest.query.get_or_404(id)

    # 权限检查
    if not current_user.is_administrator():
        flash('您没有权限审批事务审批单。', 'danger')
        return redirect(url_for('approval_request.index'))

    # 只有待审批状态可以审批
    if approval_request.status != 'pending':
        flash('只有待审批状态的审批单可以审批。', 'warning')
        return redirect(url_for('approval_request.detail', id=approval_request.id))

    action = request.form.get('action', 'approve')
    comment = request.form.get('comment', '')

    if action == 'approve':
        # 同意审批
        approval_request.status = 'approved'
        approval_request.approved_at = datetime.utcnow()
        approval_request.manager_comment = comment
        approval_request.manager_signed_at = datetime.utcnow()
        flash('事务审批单已批准。', 'success')
    elif action == 'reject':
        # 拒绝审批
        approval_request.status = 'rejected'
        approval_request.manager_comment = comment
        flash('事务审批单已被拒绝。', 'warning')

    db.session.commit()

    return redirect(url_for('approval_request.detail', id=approval_request.id))
