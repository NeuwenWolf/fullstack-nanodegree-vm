import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#### End of config code ####

#creating the users table
class User(Base):
	__tablename__ = 'user'
	
	name = Column(String(80), nullable = False)
	
	email = Column(String(80), nullable = False)
	
	picture = Column(String(250))
	
	id = Column(Integer, primary_key = True)

#creating the Category table. Categories must have unique names for routing to function properly
class Category(Base):
	__tablename__ = 'category'
	
	name = Column(String(80), unique=True, nullable = False)
	
	id = Column(Integer, primary_key = True)
	
	user_id = Column(Integer, ForeignKey('user.id'))
	
	user = relationship(User)
	
	
#creating the items table. all items require a name, price and description
class Item(Base):
	__tablename__ = 'item'

	name = Column(String(80), nullable = False)
		
	price = Column(Integer, nullable = False)

	id = Column(Integer, primary_key = True)

	description = Column(String(250), nullable = False)	
	
	user_id = Column(Integer, ForeignKey('user.id'))

	category_id = Column(Integer, ForeignKey('category.id'))
		
	category = relationship(Category)
	
	user = relationship(User)

	@property
	#make data serializable for json API
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name': self.name,
			'description': self.description,
			'id': self.id,
			'price': self.price,
			'category': self.category.name,
			
		}
	
	
	
	
	
	

#### AT END OF FILE ####
engine = create_engine(
    'sqlite:///catalog.db')

Base.metadata.create_all(engine)
