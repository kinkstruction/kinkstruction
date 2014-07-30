from flask import url_for, g
from itsdangerous import Signer
from config import *
from flask.ext.mail import Message
from jinja2 import Template
import os


class VerificationMailer(object):
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail
        self.signer = Signer(ITSDANGEROUS_SECRET_KEY)

    def get_template(self, user):
        return """
        <p>
            Dear {{user.username}},
        </p>

        <p>
            You've received this email because someone using the email address {{user.email}}--hopefully you--opened up an account at kinkstruction.com.
            Please click the link below to validate your email address and activate your account.
        </p>

        <p>
            {{validation_url}}
        </p>

        <p>
            Sincerely,
        </p>
        <p>
            The Kinkstruction Admin
        </p>"""

    def send_mail(self, user):
        template = self.get_template("/templates/mail_sign_in.html")
        msg = Message('Kinkstruction Confirmation',
                   sender='verifications@kinkstruction.com',
                   recipients=[user.email])
        msg.html = Template(template).render(validation_url=self.generate_url(user), user=user)
        self.mail.send(msg)

    def generate_url(self, user):
        result = url_for("verify_email", _external=True, signed_username=self.signer.sign(user.username))
        return result

    def check_signed_username(self, user, signed_username):
        return self.signer.unsign(signed_username) == user.username
