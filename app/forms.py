from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, DateField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    full_name = StringField('姓名', validators=[Length(0, 100)])
    department = StringField('部门', validators=[Length(0, 100)])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已存在。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱已被注册。')

class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    full_name = StringField('姓名', validators=[Length(0, 100)])
    department = StringField('部门', validators=[Length(0, 100)])
    role = SelectField('角色', choices=[('user', '普通用户'), ('admin', '管理员')])
    is_active = BooleanField('激活状态')
    submit = SubmitField('保存')

# 采购计划表单
class PurchasePlanForm(FlaskForm):
    plan_name = StringField('项目名称', validators=[DataRequired(), Length(1, 200)])
    project_manager = StringField('项目经理', validators=[Length(0, 100)])
    plan_type = SelectField('采购类型', choices=[
        ('goods', '货物'),
        ('services', '服务'), 
        ('projects', '工程')
    ], default='goods')
    procurement_method = SelectField('采购方式', choices=[
        ('public_bidding', '公开招标'),
        ('invited_bidding', '邀请招标'),
        ('competitive_negotiation', '竞争性谈判'),
        ('inquiry', '询价'),
        ('single_source', '单一来源')
    ], validators=[Optional()])
    start_date = DateField('预计开始日期', validators=[Optional()])
    end_date = DateField('预计结束日期', validators=[Optional()])
    department = StringField('申请部门', validators=[Length(0, 100)])
    description = TextAreaField('采购说明', validators=[Length(0, 1000)])
    remarks = TextAreaField('备注', validators=[Length(0, 500)])
    submit = SubmitField('保存')
    submit_and_submit = SubmitField('提交审批')

# 采购明细表单  
class PurchaseItemForm(FlaskForm):
    item_name = StringField('物资名称', validators=[DataRequired()])
    brand_model = StringField('品牌型号', validators=[Length(0, 200)])
    specification = StringField('规格', validators=[Length(0, 200)])
    quantity = DecimalField('数量', validators=[DataRequired()], places=2)
    unit = StringField('单位', validators=[Length(0, 20)])
    batch_quantity = DecimalField('批次数量', validators=[Optional()], places=2)
    extra_contract_quantity = DecimalField('合同外数量', validators=[Optional()], places=2)
    required_date = DateField('需求日期', validators=[Optional()])
    remarks = StringField('备注', validators=[Length(0, 200)])