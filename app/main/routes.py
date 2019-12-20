from flask import render_template,flash,redirect,url_for,current_app
from app.main.forms import EditProfileForm,PostForm
from app import db
from app.main import bp
from flask_login import current_user,login_required
from app.models import User,Post
from flask import request
from datetime import datetime
from werkzeug.urls import url_parse
from flask_babel import _
from guess_language import guess_language
from flask import g
from flask_babel import get_locale
from flask import jsonify
from app.translate import translate

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
# 带上login_required装饰器代表上面的索引都需要登录后访问
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))

    # 看url里有没有带page信息，没有就默认是1
    page = request.args.get('page',1,type=int)
    # 显示第page页的内容
    posts = current_user.followed_posts().paginate(
        page,current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None


    return render_template('index.html',
                           title=_('Home'),
                           form=form,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url
                           )


@bp.route('/user/<username>')
@login_required
def user(username):
    # 用username查询数据库，找到返回，没找到就404
    user = User.query.filter_by(username=username).first_or_404()
    # 看url里有没有带page信息，没有就默认是1
    page = request.args.get('page', 1, type=int)
    # 显示第page页的内容
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html',
                           user=user,
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


# 跟踪用户的上次访问时间
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())
    #if g.locale.startswith('zh'):
        #g.locale = 'zh-CN'


# 用户写个人简介的页面
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        # 这是主动修改的情况
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        # 这是没修改东西，单纯点了一下按钮来到了这个页面的情况
        # 把数据库里预存的数据展现在页面上
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


# 关注页面
@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('you cannot follow yourself!'))
        return redirect(url_for('main.index', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('you cannot unfollow yourself!'))
        return redirect(url_for('main.index', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


# 浏览其他用户的post，便于找到想follow的人
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'],False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',
                           title=_('Explore'),
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)

# 客户端请求翻译的路由
@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})
