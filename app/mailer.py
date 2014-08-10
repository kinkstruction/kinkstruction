from flask import url_for, g, current_app
from itsdangerous import Signer
from config import *
from flask.ext.mail import Message
from jinja2 import Template
from decorators import fire_and_forget


class Mailer(object):
    def __init__(self, app, mail):
        self.app = app
        self.mail = mail
        self.signer = Signer(ITSDANGEROUS_SECRET_KEY)

    @fire_and_forget
    def send_mail(self, email, subject, body):
        with self.app.app_context():
            msg = Message(subject, sender='admin@kinkstruction.com', recipients=[email], html=body)
            self.mail.send(msg)


class NewMessageMailer(Mailer):
    def get_template(self):
        return """
<p>
    Dear {{username}},
</p>
<p>
    You've received a message from {{sending_username}}:
</p>

    {% if message_body|length > 140 %}
    <blockquote>
        {{message_body[:140]}}...
    </blockquote>
    {% else %}
    <p>
        {{message_body}}
    </p>
    {% endif %}
<p>
    <a href="{{url}}">Click here</a> to view the message within Kinkstruction.
</p>
<p>
    Sincerely,
</p>
<p>
    The Kinkstruction Admin
</p>"""

    @fire_and_forget
    def send_mail(self, username, email, sending_username, message_id, message_body):
        with self.app.app_context():

            template = self.get_template()
            msg = Message('New Message At Kinkstruction From {{sending_username}}',
                       sender='admin@kinkstruction.com',
                       recipients=[email])
            msg.html = Template(template).render(username=username,
                sending_username=sending_username,
                message_id=message_id,
                message_body=message_body,
                url=url_for('message', id=message_id, _external=True))

            self.mail.send(msg)


class ResetPasswordMailer(Mailer):

    def get_template(self):
        return """
<p>
    Dear {{username}},
</p>
<p>
    You've received this email because someone using the email address {{email}}--hopefully you--wishes to reset your Kinkstruction password.
    If you wish to reset your password, please click on the link below:
</p>
<p>
    {{url}}
</p>
<p>
    Sincerely,
</p>
<p>
    The Kinkstruction Admin
</p>"""

    @fire_and_forget
    def send_mail(self, username, email, token):

        with self.app.app_context():

            template = self.get_template()
            msg = Message('Reset Your Kinkstruction Password',
                       sender='admin@kinkstruction.com',
                       recipients=[email])
            msg.html = Template(template).render(url=self.generate_url(token), username=username, email=email)
            self.mail.send(msg)

    def generate_url(self, token):

        return url_for('reset_password_from_email_with_token', token=token, _external=True)


class VerificationMailer(Mailer):

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
