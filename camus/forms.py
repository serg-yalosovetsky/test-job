from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class CreateRoomForm(FlaskForm):
    room_name = StringField('Room name', validators=[DataRequired()])
    password = PasswordField('Password')
    public = SelectField('Public', coerce=lambda x: x == 'Yes',
                         choices=[('No'), ('Yes')])
    guest_limit = SelectField('Guest limit', coerce=int,
                              choices=[(0, 'None'), (2, '2'), (3, '3'),
                                       (5, '5'), (10, '10')])
    submit = SubmitField('Create')


class JoinRoomForm(FlaskForm):

    password = PasswordField('Password')
    submit = SubmitField('Join')


class OrderForm(FlaskForm):
    price = StringField('price', validators=[DataRequired()])
    currency = SelectField('currency', #coerce=lambda x: x == 'Yes',
                         choices=[('RUB'), ('EUR'), ('USD')])
    description = StringField('description', validators=[DataRequired()])
    