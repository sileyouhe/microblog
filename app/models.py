from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
import jwt
from time import time
from app import app

# 实现“关注”功能的多对多关系的关系表
# 这张表里左侧代表做出关注动作的用户，右侧代表被关注人
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # 声明与posts的一对多关系
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 声明与follow的多对多关系
    # 左侧用户关注着右侧用户
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime,default=datetime.utcnow)

    # 实现生成秘钥和验证秘钥的方法
    # 最后把生成的字节序列decode成了字符串，更方便传送
    def get_reset_password_token(self,expire_in=600):
        return jwt.encode(payload={'reset_password': self.id, 'exp': time() + expire_in},
                          key=app.config['SECRET_KEY'],algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, key=app.config['SECRET_KEY'],algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)



    def __repr__(self):
        return '<User {}>'.format(self.username)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)

    # 使用Gravatar服务为每个用户设置头像
    def avatar(self,size):
        # 把邮箱MD5编码
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        # 组装url,得到头像
        return 'https://www.gravatar.com/avatar/{}?d=mp&s={}'.format(
            digest, size)

    # 定义用户的关注方法
    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)
    # 定义用户的取消关注方法
    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)
    # 判断用户是否已经关注某人
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


    # 获取用户所有关注人的post和自己的post
    # 查询思路是：
    # 先找到所有被关注的人的post，再选出自己感兴趣的关注人的post
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # 想按时间顺序看post的时候，时间戳就派上用场了
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# 加载用户
@login.user_loader
def load_user(id):
    return User.query.get(int(id))



