from flask import Flask,render_template,request,redirect,url_for,session
from models.a import user_exists,save_user,product_exists,add_product,remove_from_db,product_list,add_to_cart,product_names_list,cart_info,remove_from_cart
from fuzzywuzzy import fuzz,process

app=Flask(__name__)
app.secret_key='abc'

@app.route('/')
def layout():
	return render_template("lay.html",title='Layout')


@app.route('/home2')
def home():
	return render_template("home2.html",title='Home')

@app.route('/aboutme')
def about() :
	return render_template("aboutme.html",title='About')

@app.route('/contact')
def contact() :
	return render_template("contact.html",title='Contact')

@app.route('/login',methods=['GET','POST'])

def login() :

	if request.method == 'POST' :
		
		username=request.form['username']
		password=request.form['password']

		result=user_exists(username)
		if result:
			if result['password']!=password :
				return "password doesnot match .Go back and reeenter the password"
			session['username']=username
						
			return redirect(url_for('home'))
		return "username does not exist"	
	return redirect(url_for('home'))



@app.route('/signup',methods=['GET','POST'])

def signup():
	if request.method== "POST" :

		user_info=dict()
		user_info['username']=request.form['username']
		user_info['password']=request.form['password']
		
		user_info['cart']=[]
		if user_exists(user_info['username']) :
			return "username already exists"
		

		save_user(user_info)
		return "user signedup"
	if request.method == "GET" :
		return render_template("signup.html")
	return redirect(url_for('home'))


@app.route('/products',methods=['GET','POST'])

def products() :
	if request.method =='POST' :
		product_info={}
		product_info['name']=request.form['name']
		product_info['price']=int(request.form['price'])
		product_info['description']=request.form['descr']
		product_info['seller']=session['username']

		if product_exists(product_info['name']) :
			return "product_exists"

		add_product(product_info)
		return redirect(url_for('products'))
	products=product_list()
	print("\n" + str(products) + "\n")
	return render_template('products.html',products=products)

@app.route('/remove_products',methods=['GET','POST'])

def remove_products() :
	if request.method == 'POST' :
		name=request.form['name']
		remove_from_db(name)
		return redirect(url_for('products'))
	return redirect(url_for('products')) 



@app.route('/cart',methods=['GET','POST'])

def cart() :
	if request.method=='POST' :
		name=request.form['name']
		add_to_cart(name)
		return redirect(url_for('cart'))
	products=cart_info()
	return render_template('cart.html',products=products)




@app.route('/remove_cart',methods=['GET','POST'])

def remove_cart() :
	if request.method=='POST' :
		product=request.form['name']

		remove_from_cart(product)

		return redirect(url_for('cart'))	
	return redirect(url_for('cart'))



@app.route('/logout')
def logout() :
	session.clear()
	return redirect(url_for('home'))



# @app.route('/search',methods=['GET','POST'])
# def search() :
# 	if request.method=='POST':
# 		choice=request.form["product"]
# 		choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
		
# 		m=process.extractOne(choice,choices )
# 		return m
# 	return redirect(url_for('home'))


@app.route('/search',methods=['GET','POST'])
def search() :
	if request.method=='POST':
		choice=request.form["product"]

		products=product_names_list()
		#print(products)
		print(process.extract(choice,products))
		return "okay"
		
	return redirect(url_for('home'))


	

app.run(debug=True)
