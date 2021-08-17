from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    price = StringField('price', validators=[DataRequired()])
    currency = SelectField('currency', #coerce=lambda x: x == 'Yes',
                         choices=[('RUB'), ('EUR'), ('USD')])
    description = StringField('description', validators=[DataRequired()])
    