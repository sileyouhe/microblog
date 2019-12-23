import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    # 首选的是环境变量'secret_key',如果没有，就是一个字符串
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 获取数据库路径
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置每页显示的post的个数
    # 在这个文件里定义某些固定配置的好处是，以后要改都统一在这改
    POSTS_PER_PAGE = 3
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['271047842@qq.com']
    # 支持的语言列表
    LANGUAGES = ['en', 'zh']
    # 百度翻译的秘钥
    APPID = os.environ.get('APPID')
    TRANSLATOR_KEY = os.environ.get('Baidu_TRANSLATOR_KEY')


