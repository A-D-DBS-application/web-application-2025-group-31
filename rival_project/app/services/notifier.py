from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail

def send_notification(subject, recipient, template, **kwargs):
    msg = Message(subject, recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    mail.send(msg)