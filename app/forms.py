from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import (DataRequired,
                                Length,
                                Regexp,
                                Optional,
                                ValidationError)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from PIL import Image
import re

EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9]+$')


def check_avatar(form, field):
    if not field.data:
        return

    try:
        field.data.stream.seek(0)
        img = Image.open(field.data.stream)
        width, height = img.size

        ratio = width / height
        if ratio < 0.8 or ratio > 1.25:
            raise ValidationError(
                "Avatar must have an aspect ratio between 0.8:1 and 1.25:1")
    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")


def check_banner(form, field):
    if not field.data:
        return

    try:
        field.data.stream.seek(0)
        img = Image.open(field.data.stream)
        width, height = img.size

        ratio = width / height
        if ratio < 2 or ratio > 6:
            raise ValidationError(
                "Banner must have a minimum aspect ratio of 4:1 (width:height)"
                )
    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")


class UploadForm(FlaskForm):
    file = FileField('Beatmap file (zip or osz)', validators=[
        FileRequired(message='Please select a file'),
        FileAllowed(['zip', 'osz'],
                    message='Only .zip or .osz files are allowed')
    ])
    submit = SubmitField('Upload')


class UserForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(message="Username is required."),
                    Length(min=2,
                           max=25,
                           message="Username must be between "
                           "2 and 25 characters."),
                    Regexp(
                            r'^\S(?:.*\S)?$',
                            message="Cannot start or end with spaces.")]
                            )
    email = StringField(
        'Email',
        validators=[DataRequired(message="Email is required."),
                    Regexp(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9]+$',
                    message="Email must be in the format "
                    "example@domain.domain extension.")]
                            )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required."),
                    Length(min=6,
                           max=20,
                           message="Password must be between "
                           "6 and 20 characters.")]
                           )
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    identity = StringField(
        "Username or Email",
        validators=[
            DataRequired(message="Username or Email is required."),
            Length(
                min=2,
                max=50,
                message="Username or Email must be between "
                "2 and 50 characters."
            )
        ]
    )

    def validate_username_or_email(self, field):
        value = field.data.strip()

        if '@' in value:
            if not EMAIL_REGEX.match(value):
                raise ValidationError("Please enter a valid email address.")

    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required."),
                    Length(min=6,
                           max=20,
                           message="Password must be between "
                           "6 and 20 characters.")]
                           )

    submit = SubmitField('Login')


class UserEditForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[Optional(),
                    Length(min=2,
                           max=25,
                           message="Username must be between "
                           "2 and 25 characters.")]
                            )
    email = StringField(
        'Email',
        validators=[Optional(),
                    Regexp(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9]+$',
                    message="Email must be in the format "
                    "example@domain.domain extension.")]
                            )
    new_password = PasswordField(
        'New password',
        validators=[Optional(),
                    Length(min=6,
                           max=20,
                           message="Password must be between "
                           "6 and 20 characters.")]
    )
    avatar = FileField('Change avatar', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'],
                    message='Only png, jpg, jpeg, webp files are allowed'),
        check_avatar
    ])
    banner = FileField('Change banner', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'],
                    message='Only png, jpg, jpeg, webp files are allowed'),
        check_banner
    ])
    submit = SubmitField('Change')
    reset_avatar = SubmitField('Reset avatar')
    reset_banner = SubmitField('Reset banner')


class DiscussionForm(FlaskForm):
    title = StringField(
        'Title',
        validators=[DataRequired(message="Title is required"),
                    Length(min=1,
                           max=50,
                           message="Title must be between "
                                   "1 and 25 characters.")],
        render_kw={
            "class": "title-textarea"
        }
    )
    content = TextAreaField(
        'Content',
        validators=[DataRequired(message="Content is required."),
                    Length(min=1,
                           max=10000000,
                           message="Content must be between "
                           "1 and 1000 characters.")],
        render_kw={
            "rows": 14,
            "class": "content-textarea"
        }
    )
    submit = SubmitField('Create')


class CommentForm(FlaskForm):
    content = TextAreaField(
        'Comment',
        validators=[
            DataRequired(message="Comment cannot be empty"),
            Length(min=1, max=2000, message="Comment must be between "
                   "1 and 2000 characters")
        ]
    )
    submit = SubmitField('Post Comment')


class SearchForm(FlaskForm):
    search = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


class VerifyForm(FlaskForm):
    code = StringField(
        'Code',
        validators=[
            DataRequired(message="Codes require"),
            Length(6, 6)
        ]
    )
    submit = SubmitField('Verify')
