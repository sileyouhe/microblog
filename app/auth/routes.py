from flask import render_template,flash,redirect,url_for
from app.auth.forms import LoginForm,RegistrationForm,ResetPasswordRequestForm,ResetPasswordForm
from app import db
from app.auth import bp
from flask_login import current_user,login_user,logout_user
from app.models import User
from werkzeug.urls import url_parse
from flask import request
from app.auth.email import send_password_reset_email
from flask_babel import _, get_locale



@bp.route('/login', methods=['GET','POST'])
def login():
    # 如果已经登录，访问login页面将会重定向到index
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    # 如果输入的账号密码符合规范，则查询库里是否有这个账号密码
    # 如果没有，提示信息，回到登录界面
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        # 如果有，使用login_user函数完成登录
        login_user(user,remember=form.remember_me.data)
        # 看url里有没有next参数
        next_page = request.args.get('next')
        # 如果没有next参数，则回到index
        # 如果next参数包含域名，则回到index
        # 否则（有next，而且不是/Index）,转到next的那个页面
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html',
                           title=_('Sign In'),
                           form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)

# 忘记密码页面处理
# 提示输入邮箱
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # 如果已经登录就不能重置密码
    if current_user.is_authenticated:
        redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    # 没登录，查邮箱是否合法，合法就发邮件
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)

# 重置密码页面处理
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


