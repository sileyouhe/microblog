from app import create_app, db, cli
from app.models import User, Post

# 真正的初始化是在这里开始的
app = create_app()
cli.register(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post' :Post}


