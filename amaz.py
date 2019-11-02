from flask import Flask,render_template,request,redirect,url_for,session
from models.a import update_stock,getfund,getuse,user_exists,save_user,product_exists,add_product,remove_from_db,product_list,add_to_cart,product_names_list,cart_info,remove_from_cart
from fuzzywuzzy import fuzz,process
from yahoo_fin import stock_info as si

app=Flask(__name__)
app.secret_key='abc'

@app.route('/')
def layout():
	return render_template("lay.html",title='Layout')

@app.route('/home2')
def home():
	if(session):
		userinfo = getuse(session['username'])

		
		#print(userinfo)
		
		stocklist = userinfo['stocklist']
		for i in range(len(stocklist)):
			stocklist[i]['live']=si.get_live_price(stocklist[i]['sname']).round(2)
			stocklist[i]['pl']= ((stocklist[i]['live']-stocklist[i]['price']).round(2))*stocklist[i]['quantity']
		return render_template("home2.html", userinfo = userinfo , stocklist = stocklist)

	else:
		return render_template("lay.html",title='Layout')

@app.route('/buy',methods=['GET','POST'])
def buy():
	if(session):
		userinfo = getuse(session['username'])
		if request.method == 'POST' :
			script=request.form['script']
			quantity=int(request.form['quantity'])
			price=float(si.get_live_price(script).round(2))
			funds=getfund(session['username'])
			if float(price)*float(quantity)> funds:	
				return("Not enough funds,Please add more funds to buy")
			else:	
				stock={}
				stock['sname']=script
				flag=0
				for stock_li in userinfo['stocklist']:
					if stock_li['sname']==script:
						flag=1
						stock['price']=round(((price*quantity)+(stock_li['price']*stock_li['quantity']))/(quantity+stock_li['quantity']),2)
						stock['quantity']=int(quantity+stock_li['quantity'])
						userinfo['stocklist'].remove(stock_li)
						userinfo['stocklist'].append(stock)
				if flag==0:	
					stock['price']=round(price,2)
					stock['quantity']=int(quantity)
					userinfo['stocklist'].append(stock)
				userinfo['funds']=round(funds-(float(price)*float(quantity)),2)
				update_stock(userinfo)
		return render_template("buy.html", userinfo = userinfo )
		
	else:
		return render_template("lay.html",title='Layout')
	return render_template("home2.html")


@app.route('/sell',methods=['GET','POST'])
def sell():
	if(session):
		userinfo = getuse(session['username'])
		if request.method == 'POST' :
			script=request.form['script']
			quantity=int(request.form['quantity'])
			price=float(si.get_live_price(script).round(2))
			funds=getfund(session['username'])
			stock={}
			stock['sname']=script
			flag=0
			for stock_li in userinfo['stocklist']:
				if stock_li['sname']==script:
					flag=1
					netstockq=stock_li['quantity']
			if flag==0:
				return("You don't own that stock")
			elif quantity> netstockq:	
				return("You are selling more stocks than you have")
			elif quantity==netstockq:
				userinfo['stocklist'].remove(stock_li)
			else:	
		
				stock['price']=round(((stock_li['price']*stock_li['quantity'])-(price*quantity))/(stock_li['quantity']-quantity),2)

				stock['quantity']=int(stock_li['quantity']-quantity)

				userinfo['stocklist'].remove(stock_li)
				userinfo['stocklist'].append(stock)
				userinfo['funds']=round(funds-(float(price)*float(quantity)),2)
				
				update_stock(userinfo)
		return render_template("sell.html", userinfo = userinfo )
		
	else:
		return render_template("lay.html",title='Layout')
	return render_template("home2.html")

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
		user_info['password']=request.form['password1']	
		password2=request.form['password2']
		user_info['stocklist']=[]
		user_info['funds']=20000
		if user_exists(user_info['username']) :
			return "username already exists"
		if user_info['password']!=password2 :
			return "passwords dont match"
		save_user(user_info)
		return "user signedup"
	if request.method == "GET" :
		return render_template("signup.html")
	return redirect(url_for('home'))




''''''
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
