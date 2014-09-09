from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, IntegerField, TextAreaField, SelectField
from wtforms.validators import *
from app.models import User, Task
from flask.ext.pagedown.fields import PageDownField

# TODO: Refactor the living bejeezus out of this...


class OptionsForm(Form):
    username = StringField('Username: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")
        ]

    )

    email = StringField('Email: ',
        validators=[
            Optional(),
            Email(message="Invalid email address")
        ])

    password = PasswordField('Password: ',
        validators=[
            Optional(),
            Length(min=2, max=256, message="Passwords must be between 2 and 256 characters")
        ]
    )

    confirm_password = PasswordField('Confirm Password: ', validators=[EqualTo('password', message="The passwords do not match"), Optional()])

    profile_privacy = SelectField('Profile Privacy: ', choices=[
        (0, "Public (any member can view your profile)"),
        (1, "Friends (only friends can view your profile)"),
        (2, "Private (only you can see your profile)")
    ], validators=[Optional()], coerce=int)

    default_task_privacy = SelectField("Default Task Privacy: ", choices=[
        (0, "Public (can be seen by any member)"),
        (1, "Friends (can be seen by friends of either you or the assignee)"),
        (2, "Private (can be seen only by you and the assignee)")
    ], default=0, validators=[Optional()], coerce=int)

    friend_request_email_alert = BooleanField("When someone sends me a friend request: ")
    friend_request_accept_email_alert = BooleanField("When a friend request that I've sent is accepted: ")

    message_new_email_alert = BooleanField("When I receive a new message (includes replies): ")

    task_created_email_alert = BooleanField("When a new task is created for me: ")
    task_edit_email_alert = BooleanField("When one of my tasks has been edited: ")
    task_accept_reject_email_alert = BooleanField("When one of my tasks has been accepted or rejected: ")

    task_start_email_alert = BooleanField("When a task I've assigned has been started: ")
    task_complete_email_alert = BooleanField("When a task I've assigned has been completed: ")

    task_new_post_email_alert = BooleanField("When a new post has been made on either one of my tasks or a task I've created: ")


class UpdateTaskForm(Form):

    title = StringField('Title: ',
        validators=[
            Required(),
            Length(max=256, message="Titles must have a length of at most 256 characters")
        ]
    )
    description = PageDownField('Description: <br>(Preview below)', validators=[Required()])
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
    description = PageDownField('Description: <br>(Preview below)', validators=[Required()])
    privacy = SelectField("Privacy: ", choices=[
        (0, "Public (can be seen by any member)"),
        (1, "Friends (can be seen by friends of either you or the assignee)"),
        (2, "Private (can be seen only by you and the assignee)")
    ], coerce=int, validators=[Optional()])
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
    bio = PageDownField('About Yourself: <br>(Preview below)', validators=[Optional()])


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
