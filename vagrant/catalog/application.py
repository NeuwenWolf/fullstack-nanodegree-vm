from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, Item, User
#imports for OAuth
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

#Get the db interface going
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    #next commented line is some debug code 
	#return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Connect a user using google's OAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate the state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain an authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is actually valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, jump ship.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user deets
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    #check if user exists before creating a new one
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

#Disconnect a connected google OAuth user
@app.route('/gdisconnect')
def gdisconnect():
	credentials = login_session.get('credentials')
	print 'In gdisconnect access token is %s' % credentials.access_token
	print 'User name is: ' 
	print login_session['username']
	if credentials is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = credentials.access_token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	print 'status is'
	print result['status']
	#if the logout worked, set a flash message and delete all of the stored information in login_session
	if result['status'] == '200':
		flash("you are now logged out %s" % login_session['username'])
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']		
		return redirect ('/catalog')
	else:
	#if the logout failed, let the user know. This shouldn't really occur in the wild much.  
	#Should stress test this in reality as not being able to log out would be extraordinarily frustrating (
	#e.g. using a public library computer and running out of time)
		response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response

#Grab a user's ID
def getUserId(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

#Grab a user's stored information
def getUserInfo(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	return user
		
#Create a new user in a general way that will support multiple OAuth providers
def createUser(login_session):
	newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

#Making an API Endpoint (GET request)
@app.route('/category/<path:category_name>/items/JSON/')
def categoryJSON(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	items = session.query(Item).filter_by(category_id = category.id).all()
	return jsonify(CategoryItems=[i.serialize for i in items])
	
@app.route('/category/<path:category_name>/<int:item_id>/<path:item_name>/JSON/')
def itemJSON(category_name, item_id, item_name):
	item = session.query(Item).filter_by(id = item_id).one()
	return jsonify(CategoryItem=item.serialize)
	
#main routing
@app.route('/')
@app.route('/index')
@app.route('/category/')
@app.route('/catalog/')
def index():
	categories = session.query(Category).all()
	allitems = session.query(Item).join(Item.category).order_by(Item.id).all()
	if 'username' not in login_session:
		return render_template('publicindex.html', categories = categories, allitems = allitems)
	else:
		return render_template('index.html', categories = categories, allitems = allitems)
	
	
#Routing for categories. Using unique category names otherwise this routing would break
@app.route('/category/<path:category_name>/items/')
def category(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	items = session.query(Item).filter_by(category_id = category.id).all()
	creator = getUserInfo(category.user_id)
	if 'username' not in login_session or creator.id != login_session['user_id']:
		return render_template('publiccategory.html', category=category, items=items)
	else:
		return render_template('category.html', category=category, items=items, creator = creator)
	
	
#Routing for items.  Since multiple items of same name could exist, am using item_id in the route to prevent bugs since that's unique.
@app.route('/category/<path:category_name>/<int:item_id>/<path:item_name>/')
def item(category_name, item_id, item_name):
	item = session.query(Item).filter_by(id = item_id).one()
	category = session.query(Category).filter_by(name = category_name).one()
	creator = getUserInfo(category.user_id)
	if 'username' not in login_session or creator.id != login_session['user_id']:
		return render_template('publicitem.html', item=item, category=category)
	else:
		return render_template('item.html', item=item, category=category)
	
	
#making a new Category
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
	if 'username' not in login_session:
		return redirect('/login')
	if request.method=='POST':
		newCategory=Category(name= request.form['name'], user_id = login_session['user_id'])
		session.add(newCategory)
		session.commit()
		flash("The category "+newCategory.name+" has been created!")
		return redirect(url_for('index'))
	else:
		return render_template('newcat.html')

#editing an existing category
@app.route('/category/<path:category_name>/edit/', methods=['GET','POST'])
def editCategory(category_name):
	if 'username' not in login_session:
		return redirect('/login')
	categorytoedit = session.query(Category).filter_by(name= category_name).one()
	oldname=categorytoedit.name
	if categorytoedit.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this category. Please create your own category in order to edit.')}</script><body onload = 'myFunction()''>"
	if request.method=='POST':
		if request.form['name']:
			categorytoedit.name = request.form['name']
		session.add(categorytoedit)
		session.commit()
		flash(oldname+" has been updated to "+categorytoedit.name+"!")
		return redirect(url_for('category', category_name=categorytoedit.name))
	else:
		return render_template('editcat.html', category=categorytoedit)

#Deleting a category
@app.route('/category/<path:category_name>/delete/', methods=['GET','POST'])
def deleteCat(category_name):
	categorytodelete = session.query(Category).filter_by(name= category_name).one()
	if 'username' not in login_session:
		return redirect('/login')
	if categorytodelete.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to delete this category. Please create your own category in order to delete.')}</script><body onload = 'myFunction()''>"
	if request.method=='POST':
		session.delete(categorytodelete)
		session.commit()
		flash("The entire "+categorytodelete.name+" catalog has been deleted!")
		return redirect(url_for('index'))
	else:
		return render_template('deletecat.html', category=categorytodelete)
		
#making a new item
@app.route('/category/<path:category_name>/new/', methods=['GET','POST'])
def newItem(category_name):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method=='POST':
		category = session.query(Category).filter_by(name = category_name).one()
		newItem=Item(name= request.form['name'], price= (request.form['price']), description= request.form['description'], category_id = category.id, user_id = login_session['user_id'])
		session.add(newItem)
		session.commit()
		flash(newItem.name+" has been created for the "+category.name+" category!")
		return redirect(url_for('category', category_name=category.name))
	else:
		category = session.query(Category).filter_by(name = category_name).one()
		return render_template('newitem.html', category_name=category_name, category=category)
	
#editing an existing item
@app.route('/category/<path:category_name>/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_name, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	category = session.query(Category).filter_by(name= category_name).one()
	itemtoedit = session.query(Item).filter_by(id = item_id).one()
	oldname = itemtoedit.name
	if itemtoedit.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own items in order to edit.')}</script><body onload = 'myFunction()''>"
	if request.method=='POST':
		if request.form['name']:
			itemtoedit.name = request.form['name']
		if request.form['price']:
			itemtoedit.price = request.form['price']
		if request.form['description']:
			itemtoedit.description = request.form['description']
		session.add(itemtoedit)
		session.commit()
		flash(oldname+" in the "+category.name+" catalog has been updated to "+itemtoedit.name+"!")
		return redirect(url_for('category', category_name=category.name))
	else:
		return render_template('edit.html', category=category, item=itemtoedit)
	
#deleting an existing item
@app.route('/category/<path:category_name>/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(category_name, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	category = session.query(Category).filter_by(name= category_name).one()
	itemtodelete = session.query(Item).filter_by(id= item_id).one()
	if itemtodelete.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own items in order to delete.')}</script><body onload = 'myFunction()''>"
	if request.method=='POST':
		session.delete(itemtodelete)
		session.commit()
		flash(itemtodelete.name+" has been deleted from the "+category.name+" catalog!")
		return redirect(url_for('category', category_name=category.name))
	else:
		return render_template('delete.html', category=category, item=itemtodelete)
	

if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'h34h k4o3 12ld k3l8'
	app.run(host = '0.0.0.0', port = 8080)
