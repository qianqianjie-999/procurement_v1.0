from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    SelectField, TextAreaField, DecimalField, DateField, IntegerField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


# ============================================================================
# 用户认证表单
# ============================================================================

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')


class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('修改密码')


# ============================================================================
# 采购计划表单
# ============================================================================

class PurchasePlanForm(FlaskForm):
    """
    采购计划主表表单

    注意：物资明细通过前端 JavaScript 动态管理，
    后端通过 request.form 获取 item_* 字段
    """
    # 采购计划基本信息
    plan_name = StringField('项目名称', validators=[DataRequired(), Length(1, 200)])
    project_manager = StringField('项目经理', validators=[Optional(), Length(1, 100)])

    # 时间信息
    start_date = DateField('开工日期', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('预计完工日期', format='%Y-%m-%d', validators=[Optional()])

    # 描述
    description = TextAreaField('采购说明', validators=[Optional()])

    # 提交按钮
    submit = SubmitField('保存')
    submit_and_submit = SubmitField('保存并提交审批')


class PurchaseItemForm(FlaskForm):
    """
    单个采购物资明细表单

    用于前端动态生成多行物资明细（匹配 Excel 模板）
    """
    # 物品基本信息
    item_name = StringField('物资名称', validators=[DataRequired(), Length(1, 200)])
    brand_model = StringField('品牌型号', validators=[Optional(), Length(1, 200)])
    specification = StringField('主要规格', validators=[Optional(), Length(1, 500)])

    # 数量和单位
    quantity = DecimalField('数量', places=4, validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('单位', validators=[Optional(), Length(1, 20)])

    # 批次数量和合同外数量（Excel 模板特有字段）
    batch_quantity = DecimalField('批次数量', places=4, validators=[Optional(), NumberRange(min=0)])
    extra_contract_quantity = DecimalField('合同外数量', places=4, validators=[Optional(), NumberRange(min=0)])

    # 时间信息
    required_date = DateField('计划到货时间', format='%Y-%m-%d', validators=[Optional()])

    # 行备注
    remarks = TextAreaField('备注', validators=[Optional()])


# ============================================================================
# 审批相关表单
# ============================================================================

class ApprovalForm(FlaskForm):
    """审批操作表单"""
    action = SelectField('审批操作', choices=[
        ('approve', '同意'),
        ('reject', '拒绝')
    ], validators=[DataRequired()])
    comments = TextAreaField('审批意见', validators=[Optional()])
    submit = SubmitField('提交审批')
