from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError

def natural_number():
    def _natural_number(form, field):
        if float(field.data) < 0:
            raise ValidationError('only natural number')
    return _natural_number
    
    
class OrderForm(FlaskForm):
    price = StringField('price', validators=[DataRequired(), natural_number() ])
    currency = SelectField('currency', #coerce=lambda x: x == 'Yes',
                         choices=[('RUB'), ('EUR'), ('USD')])
    description = StringField('description', validators=[DataRequired()])
    