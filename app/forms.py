from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, IntegerField, TextAreaField, SelectField
from wtforms.validators import *
from app.models import User, Task

# TODO: Refactor the living bejeezus out of this...


class OptionsForm(Form):
    username = StringField('Username: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")
        ]

    )

    password = PasswordField('Password: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('password', message="The passwords do not match"), Optional()])


class UpdateTaskForm(Form):

    title = StringField('Title: ',
        validators=[
            Required(),
            Length(max=256, message="Titles must have a length of at most 256 characters")
        ]
    )
    description = TextAreaField('Description: ', validators=[Required()])
    privacy = SelectField('Privacy: ', choices=[
        (0, "Public (can be seen by any member)"),
        (1, "Friends (can be seen by friends of either you or the assignee)"),
        (2, "Private (can be seen only by you and the assignee)")
    ], coerce=int, validators=[Optional()])


class CreateTaskForm(Form):
    title = StringField('Title: ',
        validators=[
            Required(),
            Length(max=256, message="Titles must have a length of at most 256 characters")
        ]
    )
    description = TextAreaField('Description: ', validators=[Required()])
    privacy = SelectField("Privacy: ", choices=[
        (0, "Public (can be seen by any member)"),
        (1, "Friends (can be seen by friends of either you or the assignee)"),
        (2, "Private (can be seen only by you and the assignee)")
    ], default=0, validators=[Optional()])
    points = IntegerField('Points: ', default=0, validators=[NumberRange(min=0)])


class UpdateTaskLogForm(Form):
    log = TextAreaField('Log: ', validators=[Optional()])


class ResetPasswordForm(Form):

    password = PasswordField('Password: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    new_password = PasswordField('Password: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('new_password', message="The passwords do not match")])


class ResetPasswordFromEmailForm(Form):
    password = PasswordField('Password: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('password', message="The passwords do not match")])


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
    orientation = StringField('Orientation: ', validators=[Optional(), Length(max=24)])
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
    orientation = StringField('Orientation: ', validators=[Optional(), Length(max=24)])
    bio = TextAreaField('About Yourself: ', validators=[Optional()])

    remember_me = BooleanField('remember_me', default=False)
