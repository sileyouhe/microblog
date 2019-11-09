from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask import request
import os

# 初始化flask应用
app = Flask(__name__)
# 初始化各种flask扩展
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
# 让flask-login知道处理登录的页面是/login
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
# 初始化mail服务
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# 初始化bootstrap，用来美化页面
bootstrap = Bootstrap(app)

# 初始化flask-moment，这是一个本地化时区的库
moment = Moment(app)

# 初始化flask-babel，这是一个本地化语言的库
babel = Babel(app)
# 响应更换语言的请求
# 要更换什么语言，我们从用户的request里看header里的accept_languages参数
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])



from app import routes,models,errors
