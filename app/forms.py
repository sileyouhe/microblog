
from flask_wtf import FlaskForm
# 两个需要的字段类
from wtforms import StringField,BooleanField,SubmitField,PasswordField,TextAreaField
# 验证是否为空
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,Length
from app.models import User
from flask_babel import lazy_gettext as _l


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    # 这里检测了一下是否符合email格式
    email = StringField('Email', validators=[DataRequired(), Email()])
    # 检测是否password格式，并且要求输入两次
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # 去数据库里查有没有一样的用户名
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    # 去数据库里查有没有一样的邮箱
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

# 改自己的个人信息form
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    # 如果不写这个init函数，这个类会自动按父类的方法初始化（等于super那句）
    # 这里为了增加一个“初始用户名”的成员，所以才显式写出来
    def __init__(self,original_username,*args,**kwargs):
        # 初始化父类
        super(EditProfileForm,self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

# 发表博客的表格
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


# 忘记密码的表格,要求输入邮箱
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

# 重置密码的表格
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
