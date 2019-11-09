from flask import render_template,flash,redirect,url_for
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm
from app import app,db
from flask_login import current_user,login_user,logout_user,login_required
from app.models import User,Post
from werkzeug.urls import url_parse
from flask import request
from datetime import datetime
from app.email import send_password_reset_email
from flask_babel import _

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# 带上login_required装饰器代表上面的索引都需要登录后访问
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))

    # 看url里有没有带page信息，没有就默认是1
    page = request.args.get('page',1,type=int)
    # 显示第page页的内容
    posts = current_user.followed_posts().paginate(
        page,app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None


    return render_template('index.html',
                           title='Home',
                           form=form,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url
                           )


@app.route('/login', methods=['GET','POST'])
def login():
    # 如果已经登录，访问login页面将会重定向到index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # 如果输入的账号密码符合规范，则查询库里是否有这个账号密码
    # 如果没有，提示信息，回到登录界面
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        # 如果有，使用login_user函数完成登录
        login_user(user,remember=form.remember_me.data)
        # 看url里有没有next参数
        next_page = request.args.get('next')
        # 如果没有next参数，则回到index
        # 如果next参数包含域名，则回到index
        # 否则（有next，而且不是/Index）,转到next的那个页面
        if not next_page or url_parse(next_page).netloc !=  '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register',form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    # 用username查询数据库，找到返回，没找到就404
    user = User.query.filter_by(username=username).first_or_404()
    # 看url里有没有带page信息，没有就默认是1
    page = request.args.get('page', 1, type=int)
    # 显示第page页的内容
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username,page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html',
                           user=user,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


# 跟踪用户的上次访问时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# 用户写个人简介的页面
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        # 这是主动修改的情况
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        # 这是没修改东西，单纯点了一下按钮来到了这个页面的情况
        # 把数据库里预存的数据展现在页面上
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


# 关注页面
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('you cannot follow yourself!')
        return redirect(url_for('index', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Congrats, you are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('you cannot unfollow yourself!')
        return redirect(url_for('index', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('you are not following {}!'.format(username))
    return redirect(url_for('user', username=username))


# 浏览其他用户的post，便于找到想follow的人
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',
                           title='Explore',
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)

# 忘记密码页面处理
# 提示输入邮箱
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # 如果已经登录就不能重置密码
    if current_user.is_authenticated:
        redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    # 没登录，查邮箱是否合法，合法就发邮件
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

# 重置密码页面处理
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


