from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length
from app.models import User, Task


# Can be used either for logging in or initially registering an account.
class LoginForm(Form):
    username = StringField('username',
        # validators=[InputRequired(), Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")]
            )
    password = PasswordField('password',
        # validators=[InputRequired, Length(min=6, max=256, message="Passwords must be between 6 and 256 characters")]
            )
    remember_me = BooleanField('remember_me', default=False)

class SignUpForm(Form):
    username = StringField('username',
        # validators=[InputRequired(), Length(min=2, max=256, message="Usernames must be between 2 and 256 characters")]
            )
    password = PasswordField('password',
        # validators=[InputRequired, Length(min=6, max=256, message="Passwords must be between 6 and 256 characters")]
            )
    email = StringField('email',
        # validators=[InputRequired()]
    )
    remember_me = BooleanField('remember_me', default=False)
