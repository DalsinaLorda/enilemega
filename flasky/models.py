from datetime import datetime
from flasky import db, login_manager
from flask_login import UserMixin
import json

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
	)	

class User(db.Model, UserMixin):
	id= db.Column(db.Integer, primary_key=True)
	brand_name = db.Column(db.String(20), unique = True, nullable = False)
	username= db.Column(db.String(15), unique=True, nullable=False)
	email= db.Column(db.String(20), unique=True, nullable=False)
	password= db.Column(db.String(20), unique=True, nullable=False)
	country = db.Column(db.String(20), unique= False, nullable= False)
	location = db.Column(db.String(20), unique = False, nullable= False)
	lat = db.Column(db.String(20), unique = False, nullable= True)
	lng = db.Column(db.String(20), unique = False, nullable= True)
	contact = db.Column(db.Integer, unique=True ,nullable= False)
	rating = db.Column(db.Integer, unique= False, nullable= True, default=0)
	credit_card =db.Column(db.Integer, unique= True, nullable= False)
	image_file=db.Column(db.String(100), nullable=False, default='default.png')
	posts=db.relationship('Post', backref='author', lazy=True)
	
	messages_sent = db.relationship('Messages',
									foreign_keys='Messages.sender_id',
									backref='author',lazy='dynamic')
	
	messages_recieved = db.relationship('Messages',
									foreign_keys='Messages.recipient_id',
									backref='recipient',lazy='dynamic')
	last_message_read_time = db.Column(db.DateTime)
	
	def new_messages(self):
		last_read_time=self.last_message_read_time or datetime(1900, 1, 1)
		return Messages.query.filter_by(recipient=self).filter(
			Messages.timestamp > last_read_time).count()


	followed = db.relationship(
	'User', secondary=followers,
	primaryjoin=(followers.c.follower_id==id),
	secondaryjoin=(followers.c.followed_id==id),
	backref= db.backref('followers', lazy = 'dynamic'), lazy ='dynamic')

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def	is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id==user.id).count() > 0

	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id==Post.user_id)).filter(
				followers.c.follower_id==self.id)
		own = Post.query.filter_by(user_id = self.id)
		return followed.union(own).order_by(Post.date_posted.desc())		
		
							

	def __repr__(self):
		return'<User{}>'.format(self.username)

	
	def __repr__ (self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.brand_name}', '{self.country}', '{self.contact}')"



class Post(db.Model):
	id= db.Column(db.Integer, primary_key=True)
	date_posted= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name= db.Column(db.String(120), nullable=False)	
	price= db.Column(db.Text, nullable=False)
	discount= db.Column(db.Integer, nullable=False)
	stock= db.Column(db.Integer, nullable=False)
	color= db.Column(db.Text, nullable=False)
	description= db.Column(db.Text, nullable=False)
	brand= db.Column(db.String(20), nullable=False, unique=False)
	category= db.Column(db.String(20), nullable=False, unique=False)

#	brands=db.relationship('Brand', backref='post', lazy=True)
#	categories=db.relationship('Category', backref='post', lazy=True)

	image=db.Column(db.String(120), nullable=False)	
	image_1=db.Column(db.String(120), nullable=False)	
	image_2=db.Column(db.String(120), nullable=False)	
	user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
	
	
	def __repr__ (self):
		return f"Post('{self.name}', '{self.date_posted}', '{self.price}', '{self.discount}, '{self.stock}, '{self.color}, '{self.description}, '{self.image}, '{self.image_1}, '{self.image_2}', '{self.brand}', '{self.category}')"

class Brand(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(20), unique=False, nullable= False)
#	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

	def __repr__(self):
		return f"Brand('{self.name}')"		 
 
class Category(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(20), unique = True, nullable = False)
#	post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)

	def __repr__(self):
		return f"Category('{self.name}')"

class JsonEcodedDict(db.TypeDecorator):
	impl=db.Text

	def process_bind_param(self, value, dialect):
		if value is None:
			return'{}'
		else:
			return json.dumps(value)
	def process_result_value(self,value,dialect):
		if value is None:
			return {}
		else:
			return json.loads(value)

class CustomerOrder(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	invoice = db.Column(db.String(20), unique=True, nullable=False)
	status=db.Column(db.String(20),default='Pending', nullable=False)
	customer_id=db.Column(db.Text,nullable=False)
	date_created=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)
	orders=db.Column(JsonEcodedDict)
	def __repr__(self):
		return'<CustomerOrder %r>' % self.invoice

class Messages(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	body = db.Column(db.String(120))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	def __repr__(self):
    		return'<Messages %r>' % self.body


db.create_all()	