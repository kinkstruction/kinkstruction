from flask import g, current_app
from flask.ext.mail import Message
from decorators import fire_and_forget


class Mailer(object):
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail

    @fire_and_forget
    def send_mail(self, email, subject, body):
        with self.app.app_context():
            msg = Message(subject, sender='admin@kinkstruction.com', recipients=[email], html=body)
            self.mail.send(msg)
