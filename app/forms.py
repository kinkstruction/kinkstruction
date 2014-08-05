from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import *
from app.models import User, Task


class NewMessageForm(Form):
    title = StringField('Title: ',
        validators=[Required(), Length(max=256)]
    )
    body = TextAreaField('Body: ', validators=[Required()])


# Can be used either for logging in or initially registering an account.
class LoginForm(Form):
    username = StringField('Username: ',
        validators=[
            Required(),
            Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")
        ]

    )

    password = PasswordField('Password: ',
        validators=[
            Required(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    remember_me = BooleanField('remember_me', default=False)


class EditProfileForm(Form):
    username = StringField('Username: ',
        validators=[
            Required(),
            Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")
        ]

    )

    password = PasswordField('Password: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('password', message="The passwords do not match")])

    email = StringField('Email Address: ', validators=[Email(message="Invalid email address"), Required()])

    age = IntegerField('Age: ',
        validators=[
            Optional(),
            NumberRange(min=18, message="You must be 18 years of age or older to join Kinkstruction.com")
        ]
    )

    gender = StringField('Gender: ', validators=[Optional(), Length(max=24)])
    role = StringField('Role: ', validators=[Optional(), Length(max=24)])
    bio = TextAreaField('About Yourself: ', validators=[Optional()])


class SignUpForm(Form):

    username = StringField('Username: ',
        validators=[
            Required(),
            Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")
        ]

    )

    password = PasswordField('Password: ',
        validators=[
            Required(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('password', message="The passwords do not match")])

    email = StringField('Email Address: ', validators=[Email(message="Invalid email address"), Required()])

    age = IntegerField('Age: ',
        validators=[
            Optional(),
            NumberRange(min=18, message="You must be 18 years of age or older to join Kinkstruction.com")
        ]
    )

    gender = StringField('Gender: ', validators=[Optional(), Length(max=24)])
    role = StringField('Role: ', validators=[Optional(), Length(max=24)])
    bio = TextAreaField('About Yourself: ', validators=[Optional()])

    remember_me = BooleanField('remember_me', default=False)
