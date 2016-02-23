from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

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
	app.run(host = '0.0.0.0', port = 5000)
