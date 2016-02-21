from flask import Flask, render_template, url_for, request, redirect, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/category/')
def index():
	categories = session.query(Category).all()
	allitems = session.query(Item).join(Item.category).order_by(Item.id).all()
	return render_template('index.html', categories = categories, allitems = allitems)
	
@app.route('/category/<path:category_name>/items')
def category(category_name):
	category = session.query(Category).filter_by(name = category_name).one()
	items = session.query(Item).filter_by(category_id = category.id)
	return render_template('category.html', category=category, items=items)
	
@app.route('/category/<path:category_name>/<int:item_id>/<path:item_name>')
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
		flash(newCategory.name+" has been created!")
		return redirect(url_for('index'))
	else:
		return render_template('newcat.html')
	
@app.route('/category/<path:category_name>/new/', methods=['GET','POST'])
def newItem(category_name):
	if request.method=='POST':
		category = session.query(Category).filter_by(name = category_name).one()
		newItem=Item(name= request.form['name'], price= (request.form['price']), description= request.form['description'], category_id = category.id)
		session.add(newItem)
		session.commit()
		return redirect(url_for('category', category_name=category_name))
	else:
		category = session.query(Category).filter_by(name = category_name).one()
		return render_template('newitem.html', category_name=category_name, category=category)
	
#@app.route('/category/<path:category_name>/<int:item_id>/new/')
#def editCatalogItem(category_name, item_id):
#	return render_template('new.html')
	
@app.route('/category/<path:category_name>/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_name, item_id):
	category = session.query(Category).filter_by(name= category_name).one()
	itemtoedit = session.query(Item).filter_by(id = item_id).one()
	if request.method=='POST':
		if request.form['name']:
			itemtoedit.name = request.form['name']
		if request.form['price']:
			itemtoedit.price = request.form['price']
		if request.form['description']:
			itemtoedit.description = request.form['description']
		session.add(itemtoedit)
		session.commit()
		flash(itemtoedit.name+" has been updated!")
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
		return redirect(url_for('category', category_name=category.name))
	else:
		return render_template('delete.html', category=category, item=itemtodelete)
	

if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'h34h k4o3 12ld k3l8'
	app.run(host = '0.0.0.0', port = 5000)
