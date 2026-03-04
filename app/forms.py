from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadForm(FlaskForm):
    file = FileField('Beatmap file (zip or osz)', validators=[
        FileRequired(message='Please select a file'),
        FileAllowed(['zip', 'osz'], message='Only .zip or .osz files are allowed')
    ])
    uploader = StringField('Uploader (optional)')
    submit = SubmitField('Upload')

class UserForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(message="Username is required."),
                    Length(min=2,
                           max=25,
                           message="Username must be between 2 and 25 characters.")]
                            )
    email = StringField(
        'Email',
        validators=[DataRequired(message="Email is required."),
                    Regexp(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9]+$',
                    message="Email must be in the format example@domain.domain extension.")]
                            )
    password = StringField(
        'Password',
        validators=[DataRequired(message="Password is required."),
                    Length(min=6,
                           max=20,
                           message="Password must be between 6 and 20 characters.")]
                           )
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    identity = StringField(
        'Username or Email',
        validators=[DataRequired(message="Username or Email is required.")]
    )

    password = StringField(
        'Password',
        validators=[DataRequired(message="Password is required.")]
    )

    submit = SubmitField('Login')
