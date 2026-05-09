"""
用户认证路由蓝图

包含登录、登出、注册等功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.utils.captcha import generate_captcha, validate_captcha
from app.utils.rate_limit import check_rate_limit
from app.utils.security import login_rate_limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录

    GET: 显示登录表单
    POST: 验证用户名密码，登录用户
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    locked_out, remaining_time = login_rate_limiter.is_locked_out()
    if locked_out:
        flash(f'登录失败次数过多，请 {remaining_time} 秒后再试。', 'danger')
        return render_template('auth/login_enhanced.html', form=LoginForm())

    form = LoginForm()

    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(username=form.username.data).first()

            if user is None:
                login_rate_limiter.record_failed_login()
                remaining = login_rate_limiter.get_remaining_attempts()
                flash(f'用户名或密码错误。剩余尝试次数: {remaining}', 'danger')
                return render_template('auth/login_enhanced.html', form=form)

            if not user.check_password(form.password.data):
                login_rate_limiter.record_failed_login()
                remaining = login_rate_limiter.get_remaining_attempts()
                flash(f'用户名或密码错误。剩余尝试次数: {remaining}', 'danger')
                return render_template('auth/login_enhanced.html', form=form)

            if not user.is_active:
                flash('您的账户已被禁用，请联系管理员。', 'danger')
                return render_template('auth/login_enhanced.html', form=form)

            login_rate_limiter.reset_attempts()
            login_user(user, remember=form.remember_me.data)

            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.username}！', 'success')

            if next_page and _is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('表单验证失败，请检查输入。', 'danger')

    return render_template('auth/login_enhanced.html', form=form)


def _is_safe_redirect_url(url):
    """验证重定向URL是否安全（仅允许相对路径）"""
    if not url:
        return False
    if url.startswith('/'):
        return True
    return False


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
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    allowed, remaining_time = check_rate_limit()
    if not allowed:
        flash(f'注册过于频繁，请 {remaining_time} 秒后再试。', 'danger')
        captcha_img = generate_captcha()
        return render_template('auth/register.html', form=RegistrationForm(), captcha_img=captcha_img)

    form = RegistrationForm()

    if request.method == 'GET':
        captcha_img = generate_captcha()
        return render_template('auth/register.html', form=form, captcha_img=captcha_img)

    if request.method == 'POST':
        if form.validate():
            if not validate_captcha(form.captcha.data):
                flash('验证码错误，请重新输入。', 'danger')
                captcha_img = generate_captcha()
                return render_template('auth/register.html', form=form, captcha_img=captcha_img)

            user = User.query.filter_by(username=form.username.data).first()
            if user is not None:
                flash('用户名已存在，请选择其他用户名。', 'warning')
                captcha_img = generate_captcha()
                return render_template('auth/register.html', form=form, captcha_img=captcha_img)

            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                flash('邮箱已被注册，请更换其他邮箱。', 'warning')
                captcha_img = generate_captcha()
                return render_template('auth/register.html', form=form, captcha_img=captcha_img)

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

    captcha_img = generate_captcha()
    return render_template('auth/register.html', form=form, captcha_img=captcha_img)


@auth_bp.route('/captcha')
def captcha():
    captcha_img, code = generate_captcha()
    return captcha_img
