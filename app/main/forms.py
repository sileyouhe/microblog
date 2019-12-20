from flask_wtf import FlaskForm
# 两个需要的字段类
from wtforms import StringField,SubmitField,TextAreaField
# 验证是否为空
from wtforms.validators import ValidationError, DataRequired,Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

# 改自己的个人信息form
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    # 如果不写这个init函数，这个类会自动按父类的方法初始化（等于super那句）
    # 这里为了增加一个“初始用户名”的成员，所以才显式写出来
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))

# 发表博客的表格
class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

