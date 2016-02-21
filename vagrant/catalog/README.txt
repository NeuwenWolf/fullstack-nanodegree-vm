Place your catalog project in this directory.


Mockups
	html for each page
	design URLS





Routing
	flask

Templates & Forms

CRUD Functionality

API Endpoints

Styling & Messages



interfacing with DB through sql alchemy:
##This at start:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Category, Item

engine = create_engine('sqlite:///Catalog.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()



##Then can do operations like (add/create):

myFirstCategory = Category(name = "Snowboarding")
session.add(myFirstCategory)
session.commit()

#Read
session.query(Category).all()
firstResult = session.query(Category).first()

##Update:

find:
reset:
add:
commit:

goggles = session.query(Item).filter_by(name= 'Goggles')
specificGoggles = session.query(Item).filter_by(id = 8).one()
specificGoggles.price = 299  {does the int need quotes?}[I am doing integer prices so all displayed prices will need to be divided by 100 or otherwise formatted]
session.add(specificGoggles)
session.commit()

for goggle in goggles:
	if goggle.price != 299 {does the int need quotes?}
		goggle.price = 299
		session.add(goggle)
		session.commit()

##Delete
find
delete
commit

cheapSki = session.query(Item).filter_by(name = 'Budget Ski').one()
print cheapSki.catalog.name
session.delete(cheapSki)
session.commit()

## For loop for showing a list of everything:

items = session.query(Item).all()
for item in items:
	print item.name
	print item.description
	/n
