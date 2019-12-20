from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread
from flask_babel import _

def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipient, text_body, html_body):
    msg = Message(subject=subject,recipients=recipient,
                      sender=sender)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

