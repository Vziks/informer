from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectField
from wtforms.validators import InputRequired, Length


class ProjectForm(FlaskForm):
    name = StringField(validators=[
        InputRequired(),
        Length(min=2, max=30)
    ])
    sys_name = StringField(validators=[
        InputRequired(),
        Length(min=2, max=30)
    ])