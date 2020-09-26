from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField,FileField,HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from flasky.models import User

class RegistrationForm(FlaskForm):
	brand_name= StringField('Buziness name', validators=[DataRequired(), Length(min=5, max= 20)])
	username=StringField('Username', validators=[DataRequired(), Length(min=5,max=15)])
	email=StringField('Email', validators=[DataRequired(), Length(min=8,max=20), Email()])
	country =StringField(' Country', validators=[DataRequired(), Length(min=2, max=20)])
	location= StringField('City', validators=[DataRequired()])
	latitude= HiddenField('lati', validators=[DataRequired()])
	longitude= HiddenField('logi', validators=[DataRequired()])
	contact= IntegerField('Contact', validators=[DataRequired()])
	credit_card = IntegerField('credit_card', validators=[DataRequired()])
	password=PasswordField('Password', validators=[DataRequired()])
	confirm_password=PasswordField('Confirm_Password', validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField('sign up')

	def validate_username(self, username):
		user=User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken ,plz choose another one!')


	def validate_email(self, email):
		user=User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken ,plz choose another one!')




class LoginForm(FlaskForm):
	
	email=StringField('Email', validators=[DataRequired(), Length(min=8,max=20), Email()])
	password=PasswordField('Password', validators=[DataRequired()])
	remember=BooleanField('Remember me')
	submit=SubmitField('Login')

class UpdateProfileForm(FlaskForm):
	picture=FileField( validators=[FileAllowed(['jpg','png'])])
	submit=SubmitField('Updateprofile')

	def validate_username(self, username):
		user=User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken ,plz choose another one!')


	def validate_email(self, email):
		user=User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken ,plz choose another one!')

class PostForm(FlaskForm):
	name=StringField('Name', validators=[DataRequired()])
	price=IntegerField('Price', validators=[DataRequired()])
	discount=IntegerField('Discount', validators=[DataRequired()])
	stock=IntegerField('Stock', validators=[DataRequired()])
	color=StringField('Color',validators=[DataRequired()])
	description=StringField('Description', validators=[DataRequired()])
	photo=FileField('image', validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
	photo_1=FileField('image', validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
	photo_2=FileField('image', validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
	submit=SubmitField('Add Product')		


class Addbrand(FlaskForm):
	name=StringField('Name', validators=[DataRequired()])
	submit=SubmitField('submit')

	

class Addcategory(FlaskForm):
	name=StringField('Name', validators=[DataRequired()])
	submit=SubmitField('submit')	

class MessageForm(FlaskForm):
	message=StringField('Message ', validators=[DataRequired(),
	Length(min=1, max=140)],  render_kw={"placeholder": 'paste invoice here..'})
	submit=SubmitField('Send invoice')

