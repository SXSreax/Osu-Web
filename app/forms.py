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