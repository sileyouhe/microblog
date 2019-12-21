from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel,lazy_gettext as _l
from flask import request,current_app
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()#初始化Flask-Login
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

def create_app(config_class=Config):
    # 初始化flask应用
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化各种flask扩展
    db.init_app(app)
    migrate.init_app(app,db)
    login.init_app(app)
    # 初始化mail服务
    app.config['MAIL_SERVER'] = 'smtp.qq.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    mail = Mail(app)

# 初始化bootstrap，用来美化页面
    bootstrap.init_app(app)

# 初始化flask-moment，这是一个本地化时区的库
    moment.init_app(app)

# 初始化flask-babel，这是一个本地化语言的库
    babel.init_app(app)

    # 把原先的error.py错误处理改成蓝图
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # 把原先的登录、注册、重置密码三大块合并成用户验证蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 把剩下的功能合并为核心蓝图
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

# 响应更换语言的请求
# 要更换什么语言，我们从用户的request里看header里的accept_languages参数
@babel.localeselector
def get_locale():
    best_match = request.accept_languages.best_match(current_app.config['LANGUAGES'])
    return best_match




from app import models


