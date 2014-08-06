from flask import url_for, g, current_app
from itsdangerous import Signer
from config import *
from flask.ext.mail import Message
from jinja2 import Template
from decorators import fire_and_forget


class AbstractMailer(object):
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail
        self.signer = Signer(ITSDANGEROUS_SECRET_KEY)

    def get_template(self, user):
        raise Exception("The method get_template() in AbstractMailer must be overridden!")

    def send_mail(self, username, email):
        raise Exception("The method send_mail() in AbstractMailer must be overridden!")


class VerificationMailer(AbstractMailer):

    def get_template(self):
        return """
        <p>
            Dear {{username}},
        </p>

        <p>
            You've received this email because someone using the email address {{email}}--hopefully you--opened up an account at kinkstruction.com.
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

    @fire_and_forget
    def send_mail(self, username, email):

        with self.app.app_context():

            template = self.get_template()
            msg = Message('Kinkstruction Confirmation',
                       sender='verifications@kinkstruction.com',
                       recipients=[email])
            msg.html = Template(template).render(validation_url=self.generate_url(username), username=username, email=email)
            self.mail.send(msg)

    def generate_url(self, username):

        with self.app.app_context():
            result = url_for("verify_email", _external=True, signed_username=self.signer.sign(username))
            return result

    def check_signed_username(self, username, signed_username):
        return self.signer.unsign(signed_username) == username
