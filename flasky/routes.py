from datetime import datetime
import os
import secrets
from PIL import Image
from flask import render_template, redirect, request, url_for, flash, current_app, abort, session, jsonify
from flasky import app, db, bcrypt
from flasky.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm, Addbrand, Addcategory, MessageForm
from flasky.models import User, Post,Brand, Category, CustomerOrder, Messages
from flask_login import login_user, current_user, logout_user, login_required
import json

def save_images(photo):
	hash_photo=secrets.token_urlsafe(10)
	_, file_extension= os.path.splitext(photo.filename)
	photo_name= hash_photo + file_extension
	file_path= os.path.join( current_app.root_path, 'static/shoppics', photo_name)
	output_size = (160, 160)
	j = Image.open(photo)
	j.thumbnail(output_size)
	j.save(file_path)
	return photo_name



@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
	users = User.query.all()	
	brandz=Brand.query.all()
	cates=Category.query.all()
	posts=current_user.followed_posts().all()
	return render_template('home.html', posts=posts,users=users, brandz=brandz, cates=cates, title = 'Home')

@app.route("/shops", methods=["POST", "GET"])	
def shops():
	shops = User.query.all()
	return render_template('shops.html', shops = shops,legion='All Shops', title = 'Shops')


@app.route("/shops/<brand_name>")
def user(brand_name):
	user = User.query.filter_by(brand_name = brand_name).first()
	if user is None:
		abort(404)
	posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).all()
	return render_template('user.html', user= user, posts = posts) 


@app.route("/registry", methods=['GET', 'POST'])
def registry():
	if current_user.is_authenticated:
			return redirect (url_for('home'))
	form=RegistrationForm() 
	if form.validate_on_submit():
		hashed_pass=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user_1= User(brand_name =form.brand_name.data, username=form.username.data, email=form.email.data, country=form.country.data, location=form.location.data, lat=form.latitude.data, lng=form.longitude.data ,contact= form.contact.data, credit_card=form.credit_card.data, password=hashed_pass)
		db.session.add(user_1)
		db.session.commit()
		flash('your account has been created,plz now login!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
			return redirect(url_for('home'))
	form=LoginForm() 
	if form.validate_on_submit():
		user= User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			return redirect (url_for('home'))
		else:
			flash('login unsuccessful,please check email and password', 'danger')
	return render_template('login.html', title='login', form=form )


@app.route("/logout")
def logout():
	logout_user()
	return redirect (url_for('login'))



def save_profile(form_picture):
	random_hex=secrets.token_hex(8)
	_, f_ext=os.path.splitext(form_picture.filename)
	picture_fn=random_hex+f_ext
	picture_path=os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	image_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(image_size)
	i.save(picture_path)
	return picture_fn


@app.route("/account/", methods=['GET', 'POST'] )
@login_required
def account():
	image_file=url_for('static', filename='profile_pics/' + current_user.image_file )
	form=UpdateProfileForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file=save_profile(form.picture.data)
			current_user.image_file=picture_file
		db.session.commit()
		return redirect (url_for('account'))
	if current_user.is_authenticated:
		posts = Post.query.filter_by(author = current_user).order_by(Post.date_posted.desc()).all()
		return render_template('account.html', title='Account', image_file = image_file, posts = posts, form=form)



@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	image=url_for('static', filename='shoppics/' )
	brandis = Brand.query.all()
	categoryis=Category.query.all()
	form=PostForm(request.form)
	if request.method == "POST":
		name = form.name.data
		price = form.price.data
		discount = form.discount.data
		stock = form.stock.data
		color = form.color.data
		brand = request.form.get('brand')
		category = request.form.get('category')
		description = form.description.data
	
		photo = save_images(request.files.get('photo'))
		photo_1 = save_images(request.files.get('photo_1'))
		photo_2 = save_images(request.files.get('photo_2'))
		post = Post(name=name, price=price, discount=discount, stock=stock, color=color, brand=brand, category=category, description=description,  image=photo, image_1=photo_1, image_2=photo_2, author=current_user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', brandis=brandis, categoryis=categoryis, form=form, legion='Add item')


@app.route("/post/<int:post_id>")
def post(post_id):
	post=Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.name, post=post)


@app.route("/post/<int:post_id>/edit", methods=['GET'])
@login_required
def edit_post(post_id):
	image=url_for('static', filename='shoppics/' )
	post=Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form=PostForm()
	if form.validate_on_submit():
		post.name = form.name.data
		post.price = form.price.data
		post.discount = form.discount.data
		post.stock = form.stock.data
		post.color = form.color.data
		post.description = form.description.data
		if request.files.get('photo'):
			try:
				os.unlink(os.path.join(current_app.root_path, "static/shoppics/" + post.image))
				post.photo = save_images(request.files.get('photo'))
			except:
				post.photo = save_images(request.files.get('photo'))
		db.session.commit()
		flash('Your product has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == "GET":
		form.name.data = post.name
		form.price.data = post.price
		form.discount.data = post.discount
		form.stock.data = post.stock
		form.color.data = post.color
		form.description.data = post.description	
	return render_template('create_post.html', title='EDIT Post', form=form, legion='Edit item')


@app.route("/post/<int:post_id>/delete_edit", methods=['GET'])
@login_required
def delete_post(post_id):
	post=Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your item has be deleted!', 'success')
	return redirect(url_for('admin'))


@app.route("/admin", methods=['GET', 'POST'])
def admin():
	posts = Post.query.filter_by(author = current_user).order_by(Post.date_posted.desc()).all()
	return render_template('admin.html', posts=posts, title = 'Admin')



@app.route("/menu", methods=['GET', 'POST'])
@login_required
def menu():
	posts = Post.query.filter_by(author = current_user).order_by(Post.date_posted.desc()).all()
	return render_template('menu.html', posts=posts, title = 'Profile')


@app.route("/nearbyshops/<string:location>", methods=['GET', 'POST'])
@login_required
def nearbyshops(location):
	nearbyshops = User.query.filter_by(location = current_user.location).all()
	if not nearbyshops:
    		abort(403)		
	return render_template('shops.html', nearbyshops=nearbyshops,legion='NearbyShops', title = 'NearbyShops')


@app.route("/follow/<brand_name>")
def follow(brand_name):
	user = User.query.filter_by(brand_name = brand_name).first()
	if user is None:
		flash('Shop {} not found.'.format(brand_name))
		return redirect(url_for('home'))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('shops', brand_name=brand_name))
	current_user.follow(user)
	db.session.commit()
	flash ('You are following {}!'.format(brand_name))
	return redirect(request.referrer)
    		

@app.route("/unfollow/<brand_name>")
def unfollow(brand_name):
	user = User.query.filter_by(brand_name = brand_name).first()
	if user is None:
		flash('Shop {} not found.'.format(brand_name))
		return redirect(url_for('home'))
	if user == current_user:
		flash('You cannot unfollow youself!')
		return redirect(url_for('shops', brand_name=brand_name))
	current_user.unfollow(user)
	db.session.commit()
	flash('You are not following{}'.format(brand_name))
	return redirect(request.referrer)


@app.route("/brand/<string:brand>", methods=['GET', 'POST'])
def brand(brand):
	brandz=Brand.query.all()
	cates=Category.query.all()	
	bybrand=Post.query.filter_by(brand=brand).all()
	return render_template('getCart.html', bybrand=bybrand, cates=cates, brandz=brandz, title = 'brands')


@app.route("/Add_brand", methods=["POST", "GET"])
def newbrand():
	form = Addbrand(request.form)
	if request.method=="POST":
		brands = Brand(name=form.name.data)
		db.session.add(brands)
		flash('The Brand {{ name }} has been added to the database!')
		db.session.commit()
		return redirect(url_for('home'))
	return render_template('addbrand.html', form=form, title='Add brands')

@app.route("/Brands", methods=["POST", "GET"])
def brands():
	show_brands=Brand.query.all()
	return render_template('brands.html', show_brands=show_brands,title='Brands')	


@app.route("/Add_category", methods=["POST", "GET"])
def newcategory():
	form = Addcategory(request.form)
	if request.method=="POST":
		category = Category(name=form.name.data)
		category = Category(name=form.name.data)
		db.session.add(category)
		flash('The category {{ name }} has been added to the database!')
		db.session.commit()
		return redirect(url_for('home'))
	return render_template('addcat.html', form=form, title='Add category')



@app.route("/category/<string:category>", methods=['GET', 'POST'])
def category(category):
	brandz=Brand.query.all()
	cates=Category.query.all()	
	bycat=Post.query.filter_by(category=category).all()
	return render_template('getBrand.html', brandz=brandz, cates=cates, bycat=bycat, title = 'category')


@app.route("/AllCategory", methods=["POST", "GET"])
def allcategories():
	show_categories=Category.query.all()
	return render_template('brands.html', show_categories=show_categories, title='Categories')

def MegerDicts(dict1, dict2):
	if isinstance(dict1, list ) and isinstance(dict2, list):
		return dict1 + dict2 			
	elif isinstance(dict1, dict) and isinstance(dict2, dict):
    		return dict(list(dict1.items())+ list(dict2.items()))
	return False


@app.route("/addcart", methods=["POST"])
def AddCart():
	try:
		product_id = request.form.get('product_id')
		quantity = request.form.get('quantity')
		color = request.form.get('colors')
		product = Post.query.filter_by(id=product_id).first()
		if product_id and quantity and color and request.method == "POST":
			DictItems = {product_id:{'name':product.name,'price':product.price, 'discount':product.discount, 'color':color, 'quantity':quantity, 'image':product.image, 'colors':product.color, 'author':product.author.brand_name}}
			if 'Shoppingcart' in session:
				print(session['Shoppingcart'])
				if product_id in session['Shoppingcart']:
					print('this product is already in your card')
				else:
					session['Shoppingcart']= MegerDicts(session['Shoppingcart'], DictItems)
					return redirect(request.referrer)
			else:
				session['Shoppingcart']	= DictItems
				print(DictItems)
				return redirect(request.referrer)

	except Exception as e:
		print(e)
	finally:
		return redirect(request.referrer)		

@app.route('/cards')
def getCard():
	if 'Shoppingcart' not in session or len(session['Shoppingcart']) <=0:
		return redirect(url_for('home'))
	subtotal = 0
	grandtotal = 0
	for key, product in session['Shoppingcart'].items():
		discount =(product['discount']/100) * float(product['price'])
		subtotal += float(product['price']) * int(product['quantity'])
		subtotal -= discount
		tax = ("%0.2f" % (.006 * float(subtotal)))
		grandtotal = float("%.2f" % (1.06 * subtotal))
	return render_template('carts.html', tax=tax, grandtotal=grandtotal)

@app.route("/getorder")
@login_required
def getOrder():
	if current_user.is_authenticated:
		customer_id= current_user.id
		invoice=secrets.token_hex(5)
		try:
			order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
			db.session.add(order)
			db.session.commit()
			session.pop('Shoppingcart')
			flash('Your order has been sent', 'success')
			return redirect(url_for('orders/invoice'))
		except Exception as e:
			print(e)
			flash('Something went wrong while getting order', "danger")
			return redirect(url_for('getCard'))

@app.route("/orders/<string:invoice>", methods=['GET'])
def orders(invoice):
	form = MessageForm()
	if current_user.is_authenticated:
		grandTotal=0
		subTotal=0
		orders = CustomerOrder.query.filter_by(invoice=invoice).order_by(CustomerOrder.id.desc()).first()
		orderid = orders.customer_id
		customer=User.query.filter_by(id=orderid).first()
		for _key, product in orders.orders.items():
			discount= (product['discount']/100) * float(product['price'])
			subTotal +=float(product['price']) * int(product['quantity'])
			subTotal-=discount
			tax=("%0.2f" % (.006 * subTotal))
			grandTotal = ("%.2f" % (1.06 * float(subTotal)))
	else:
		return redirect(url_for('home'))
	return render_template('order.html', invoice=invoice,form=form, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders)

@app.route("/requests/<string:sailer>", methods=['GET'])
def requests(sailer):
	if current_user.is_authenticated:
		grandTotal=0
		subTotal=0
		seller_id=current_user.id
		seller=User.query.filter_by(id=seller_id).first()
		sales = CustomerOrder.query.filter_by(customer_id=sailer).order_by(CustomerOrder.id.desc()).first()
		for _key, product in sales.orders.items():
			discount= (product['discount']/100 * float(product['price']))
			subTotal =float(product['price']* int(product['quantity']))
			subTotal-=discount
			tax=("%.2f" % (1.06 * subTotal))
			grandTotal = ("%.2f" % (1.06 * float(subTotal)))
	else:
		return redirect(url_for('home'))
	return render_template('order.html', tax=tax,subTotal=subTotal,grandTotal=grandTotal,seller=seller,sales=sales)
		


@app.route('/empty')
def empty_card():
	try:
		session.clear()
		return redirect(url_for('home'))
	except Exception as e:
		print(e)

@app.route('/updatecart/<int:code>', methods=["POST"])
def updatecart(code):
	if 'Shoppingcart' not in session or len(session['Shoppingcart']) <=0:
		return redirect(url_for('home'))
	if request.method=="POST":
		quantity=request.form.get('quantity')
		color=request.form.get('color')
		try:
			session.modified = True
			for key, item in session['Shoppingcart'].items():
				if int(key)==code:
					item['color']=color
					flash('item is updated!')
					item['quantity']=quantity
					return redirect(url_for('getCard'))
		except Exception as e:
			print(e)
			return redirect(url_for('getCard'))


@app.route('/delete/<int:id>')
def deleteitem(id):
	if 'Shoppingcart' not in session or len(session['Shoppingcart']) <=0:
		return redirect(url_for('home'))
	try:
		session.modified=True
		for key, item in session['Shoppingcart'].items():
			if int(key)==id:
				session['Shoppingcart'].pop(key, None)
				return redirect(url_for('getCard'))
	except Exception as e:
		print(e)
		return redirect(url_for('getCard'))

@app.route('/sendmessage/<recipient>', methods=['POST','GET'])
def send_message(recipient):
	user = User.query.filter_by(brand_name=recipient).first_or_404()
	form = MessageForm()
	if form.validate_on_submit():
		msg = Messages(author=current_user, recipient=user, body=form.message.data)
		db.session.add(msg)
		db.session.commit()
		flash('Your message was sent')
		return redirect(url_for('home'))
	return render_template('send_message.html', title='Send message',user=user, form=form, recipient=recipient)	


@app.route('/messages')
def messages():
	current_user.last_message_read_time = datetime.utcnow()
	db.session.commit()
	messages = current_user.messages_recieved.order_by(
		Messages.timestamp.desc()).all()
	return render_template('messages.html', messages=messages, title='Messages')

@app.route("/invoices")
def invoices():
	index = current_user.id
	invoices =CustomerOrder.query.filter_by(customer_id=index).first()
	return render_template('invoices.html' ,invoices=invoices,title='invoice')