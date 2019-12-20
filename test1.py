from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread
from guess_language import guess_language

msg = 'hello world god is a girl I dont understand'
msg1 = '哇哈哈哈今天是个好日子'

language = guess_language(msg1)
print(language)

