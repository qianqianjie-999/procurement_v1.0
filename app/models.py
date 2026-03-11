from datetime import datetime
from decimal import Decimal
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# ============================================================================
# 用户模型
# ============================================================================

class User(db.Model, UserMixin):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    is_active_field = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Flask-Login UserMixin 提供：is_authenticated, is_active, is_anonymous, get_id()
    # 但保留 is_active 属性以支持账户禁用功能
    @property
    def is_active(self):
        return self.is_active_field

    # 关联关系
    purchase_plans = db.relationship('PurchasePlan', backref=db.backref('creator', lazy='joined'), lazy='dynamic',
                                     foreign_keys='PurchasePlan.created_by')

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_administrator(self):
        """检查是否为管理员"""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """加载用户回调函数"""
    return User.query.get(int(user_id))


# ============================================================================
# 采购计划模型
# ============================================================================

class PurchasePlan(db.Model):
    """采购计划主表"""
    __tablename__ = 'purchase_plans'

    # 计划类型选择项
    PLAN_TYPES = {
        'goods': '货物',
        'services': '服务',
        'projects': '工程'
    }

    # 状态选择项
    STATUSES = {
        'draft': '草稿',
        'pending': '待审批',
        'approved': '已批准',
        'rejected': '已拒绝',
        'cancelled': '已取消',
        'completed': '已完成'
    }

    id = db.Column(db.Integer, primary_key=True)
    plan_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 采购计划编号
    plan_name = db.Column(db.String(200), nullable=False)  # 采购计划名称
    project_manager = db.Column(db.String(100))  # 项目经理
    plan_type = db.Column(db.String(50), default='goods')  # 采购类型：goods, services, projects
    status = db.Column(db.String(20), default='draft')  # draft, pending, approved, rejected, cancelled, completed
    budget_amount = db.Column(db.Numeric(15, 2), default=Decimal('0.00'))  # 预算金额
    actual_amount = db.Column(db.Numeric(15, 2), default=Decimal('0.00'))  # 实际金额
    currency = db.Column(db.String(3), default='CNY')  # 币种

    # 采购方式
    procurement_method = db.Column(db.String(50))  # 公开招标，邀请招标，竞争性谈判，询价，单一来源

    # 时间信息
    start_date = db.Column(db.Date)  # 预计开始日期
    end_date = db.Column(db.Date)  # 预计结束日期

    # 关联用户
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 最终审批人

    # 部门信息
    department = db.Column(db.String(100))  # 申请部门

    # 备注和附件
    description = db.Column(db.Text)  # 采购说明
    remarks = db.Column(db.Text)  # 备注
    attachment_path = db.Column(db.String(500))  # 附件路径
    pdf_path = db.Column(db.String(500))  # PDF 文件路径
    scanned_path = db.Column(db.String(500))  # 扫描件 PDF 路径

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    submitted_at = db.Column(db.DateTime)  # 提交时间
    approved_at = db.Column(db.DateTime)  # 审批通过时间

    # 关联关系
    items = db.relationship('PurchaseItem', backref='plan', lazy='dynamic',
                           cascade='all, delete-orphan')
    approval_flows = db.relationship('ApprovalFlow', backref='plan', lazy='dynamic',
                                     cascade='all, delete-orphan')
    approval_logs = db.relationship('ApprovalLog', backref='plan', lazy='dynamic',
                                    cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_plan_status', 'status'),
        db.Index('idx_plan_dates', 'start_date', 'end_date'),
    )

    @property
    def plan_type_label(self):
        """获取采购类型的中文标签"""
        return self.PLAN_TYPES.get(self.plan_type, self.plan_type)

    @property
    def status_label(self):
        """获取状态的中文标签"""
        return self.STATUSES.get(self.status, self.status)

    def __repr__(self):
        return f'<PurchasePlan {self.plan_number} - {self.plan_name}>'

    def calculate_total_amount(self):
        """计算总金额（基于数量和单价）"""
        # 注：当前模型已移除单价字段，此方法保留用于未来扩展
        # 如需计算总金额，需在 PurchaseItem 中添加 unit_price 字段
        return Decimal('0.00')


# ============================================================================
# 采购明细模型
# ============================================================================

class PurchaseItem(db.Model):
    """采购物资明细表"""
    __tablename__ = 'purchase_items'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('purchase_plans.id'), nullable=False)

    # 物品信息
    item_number = db.Column(db.String(50))  # 物品编号
    item_name = db.Column(db.String(200), nullable=False)  # 物资名称
    brand_model = db.Column(db.String(200))  # 品牌型号
    specification = db.Column(db.String(500))  # 主要规格
    category = db.Column(db.String(100))  # 物品分类

    # 数量和单位
    quantity = db.Column(db.Numeric(12, 4), nullable=False, default=Decimal('1.0000'))
    unit = db.Column(db.String(20))  # 单位：个，台，套，等

    # 批次数量和合同外数量
    batch_quantity = db.Column(db.Numeric(12, 4))  # 批次数量
    extra_contract_quantity = db.Column(db.Numeric(12, 4))  # 合同外数量

    # 供应商信息（可选）
    supplier_name = db.Column(db.String(200))  # 推荐供应商
    supplier_contact = db.Column(db.String(100))  # 供应商联系方式

    # 需求信息
    required_date = db.Column(db.Date)  # 需求日期
    delivery_address = db.Column(db.String(500))  # 送货地址

    # 备注
    remarks = db.Column(db.Text)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_item_plan', 'plan_id'),
        db.Index('idx_item_category', 'category'),
    )

    def __repr__(self):
        return f'<PurchaseItem {self.item_name}>'

    def before_save(self):
        """保存前计算小计"""
        if self.quantity and self.unit_price:
            self.total_price = self.quantity * self.unit_price


# ============================================================================
# 审批流程模型
# ============================================================================

class ApprovalFlow(db.Model):
    """审批流程定义表"""
    __tablename__ = 'approval_flows'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('purchase_plans.id'), nullable=False)

    # 流程信息
    flow_name = db.Column(db.String(100), nullable=False)  # 流程名称
    flow_type = db.Column(db.String(50), default='standard')  # standard, urgent, special

    # 当前状态
    current_step = db.Column(db.Integer, default=1)  # 当前审批步骤
    total_steps = db.Column(db.Integer, nullable=False)  # 总步骤数
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, approved, rejected

    # 时间信息
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    steps = db.relationship('ApprovalStep', backref='flow', lazy='dynamic',
                           cascade='all, delete-orphan', order_by='ApprovalStep.step_order')

    __table_args__ = (
        db.Index('idx_flow_plan', 'plan_id'),
        db.Index('idx_flow_status', 'status'),
    )

    def __repr__(self):
        return f'<ApprovalFlow {self.flow_name} for Plan {self.plan_id}>'


class ApprovalStep(db.Model):
    """审批步骤表"""
    __tablename__ = 'approval_steps'

    id = db.Column(db.Integer, primary_key=True)
    flow_id = db.Column(db.Integer, db.ForeignKey('approval_flows.id'), nullable=False)

    # 步骤信息
    step_order = db.Column(db.Integer, nullable=False)  # 步骤顺序
    step_name = db.Column(db.String(100), nullable=False)  # 步骤名称
    step_type = db.Column(db.String(50))  # department, finance, manager, executive

    # 审批人
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 审批人 ID
    approver_role = db.Column(db.String(50))  # 审批人角色（备选）

    # 关联审批人
    approver = db.relationship('User', backref='approval_steps')

    # 步骤状态
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, skipped
    action = db.Column(db.String(20))  # approve, reject, delegate
    comments = db.Column(db.Text)  # 审批意见

    # 时间信息
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime)

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.Index('idx_step_flow', 'flow_id'),
        db.Index('idx_step_order', 'step_order'),
    )

    def __repr__(self):
        return f'<ApprovalStep {self.step_name} - Order {self.step_order}>'


# ============================================================================
# 审批日志模型
# ============================================================================

class ApprovalLog(db.Model):
    """审批日志表 - 记录所有审批操作"""
    __tablename__ = 'approval_logs'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('purchase_plans.id'), nullable=False)
    flow_id = db.Column(db.Integer, db.ForeignKey('approval_flows.id'), nullable=True)
    step_id = db.Column(db.Integer, db.ForeignKey('approval_steps.id'), nullable=True)

    # 操作信息
    action = db.Column(db.String(20), nullable=False)  # submit, approve, reject, delegate, cancel
    previous_status = db.Column(db.String(20))  # 操作前状态
    new_status = db.Column(db.String(20))  # 操作后状态

    # 操作人
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operator = db.relationship('User', foreign_keys=[operator_id], backref='approval_logs')

    # 审批意见
    comments = db.Column(db.Text)
    reason = db.Column(db.Text)  # 拒绝原因等

    # 附件（可选）
    attachment_path = db.Column(db.String(500))

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    step = db.relationship('ApprovalStep', backref='logs')
    flow = db.relationship('ApprovalFlow', backref='logs')

    __table_args__ = (
        db.Index('idx_log_plan', 'plan_id'),
        db.Index('idx_log_operator', 'operator_id'),
        db.Index('idx_log_created', 'created_at'),
    )

    def __repr__(self):
        return f'<ApprovalLog {self.action} by User {self.operator_id}>'


# ============================================================================
# 辅助函数
# ============================================================================

def init_db(app):
    """初始化数据库，创建所有表"""
    with app.app_context():
        db.create_all()


def drop_db(app):
    """删除所有表（慎用）"""
    with app.app_context():
        db.drop_all()
