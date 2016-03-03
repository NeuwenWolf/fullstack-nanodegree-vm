from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, Item
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

#Not sure what this bit does.
app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"




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
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
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

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
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

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

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
	if result['status'] == '200':
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response
	
	
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
@app.route('/category/')
@app.route('/catalog/')
def index():
	categories = session.query(Category).all()
	allitems = session.query(Item).join(Item.category).order_by(Item.id).all()
	return render_template('index.html', categories = categories, allitems = allitems)
	
@app.route('/category/<path:category_name>/items/')
def category(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	items = session.query(Item).filter_by(category_id = category.id).all()
	return render_template('category.html', category=category, items=items)
	
@app.route('/category/<path:category_name>/<int:item_id>/<path:item_name>/')
def item(category_name, item_id, item_name):
	item = session.query(Item).filter_by(id = item_id).one()
	category = session.query(Category).filter_by(name = category_name).one()
	return render_template('item.html', item=item, category=category)
	
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
	if 'username' not in login_session:
		return redirect('/login')
	if request.method=='POST':
		newCategory=Category(name= request.form['name'])
		session.add(newCategory)
		session.commit()
		flash("The category "+newCategory.name+" has been created!")
		return redirect(url_for('index'))
	else:
		return render_template('newcat.html')

#@app.route('/category/edit/', methods=['GET','POST'])
#def editCat(category_name):
@app.route('/category/<path:category_name>/edit/', methods=['GET','POST'])
def editCategory(category_name):
	if 'username' not in login_session:
		return redirect('/login')
	categorytoedit = session.query(Category).filter_by(name= category_name).one()
	oldname=categorytoedit.name
	if request.method=='POST':
		if request.form['name']:
			categorytoedit.name = request.form['name']
		session.add(categorytoedit)
		session.commit()
		flash(oldname+" has been updated to "+categorytoedit.name+"!")
		return redirect(url_for('category', category_name=categorytoedit.name))
	else:
		return render_template('editcat.html', category=categorytoedit)

@app.route('/category/<path:category_name>/delete/', methods=['GET','POST'])
def deleteCat(category_name):
	if 'username' not in login_session:
		return redirect('/login')
	categorytodelete = session.query(Category).filter_by(name= category_name).one()
	
	if request.method=='POST':
		session.delete(categorytodelete)
		session.commit()
		flash("The entire "+categorytodelete.name+" catalog has been deleted!")
		return redirect(url_for('index'))
	else:
		return render_template('deletecat.html', category=categorytodelete)
		
@app.route('/category/<path:category_name>/new/', methods=['GET','POST'])
def newItem(category_name):
	if 'username' not in login_session:
		return redirect('/login')
	if request.method=='POST':
		category = session.query(Category).filter_by(name = category_name).one()
		newItem=Item(name= request.form['name'], price= (request.form['price']), description= request.form['description'], category_id = category.id)
		session.add(newItem)
		session.commit()
		flash(newItem.name+" has been created for the "+category.name+" category!")
		return redirect(url_for('category', category_name=category.name))
	else:
		category = session.query(Category).filter_by(name = category_name).one()
		return render_template('newitem.html', category_name=category_name, category=category)
	
@app.route('/category/<path:category_name>/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_name, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	category = session.query(Category).filter_by(name= category_name).one()
	itemtoedit = session.query(Item).filter_by(id = item_id).one()
	oldname = itemtoedit.name
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
	
@app.route('/category/<path:category_name>/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(category_name, item_id):
	if 'username' not in login_session:
		return redirect('/login')
	category = session.query(Category).filter_by(name= category_name).one()
	itemtodelete = session.query(Item).filter_by(id= item_id).one()
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
