"""
用户认证路由蓝图

包含登录、登出、注册等功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录

    GET: 显示登录表单
    POST: 验证用户名密码，登录用户
    """
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if request.method == 'POST':
        if form.validate():
            # 查找用户
            user = User.query.filter_by(username=form.username.data).first()

            if user is None:
                flash('用户名或密码错误。', 'danger')
                return render_template('auth/login.html', form=form)

            # 验证密码
            if not user.check_password(form.password.data):
                flash('用户名或密码错误。', 'danger')
                return render_template('auth/login_enhanced.html', form=form)

            # 检查账户是否被禁用
            if not user.is_active:
                flash('您的账户已被禁用，请联系管理员。', 'danger')
                return render_template('auth/login_enhanced.html', form=form)

            # 登录用户
            login_user(user, remember=form.remember_me.data)

            # 获取下次访问的 URL
            next_page = request.args.get('next')

            flash(f'欢迎回来，{user.username}！', 'success')

            # 重定向到下一页或首页
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    return render_template('auth/login_enhanced.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出。', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册

    GET: 显示注册表单
    POST: 创建新用户并自动登录
    """
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate():
            # 检查用户名是否已存在
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None:
                flash('用户名已存在，请选择其他用户名。', 'warning')
                return render_template('auth/register.html', form=form)

            # 检查邮箱是否已存在
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                flash('邮箱已被注册，请更换其他邮箱。', 'warning')
                return render_template('auth/register.html', form=form)

            # 创建新用户
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data if hasattr(form, 'full_name') else None,
                department=form.department.data if hasattr(form, 'department') else None,
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash('注册成功！请登录。', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    return render_template('auth/register.html', form=form)
