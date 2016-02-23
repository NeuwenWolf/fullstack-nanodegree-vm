import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#### End of beginning config code ####

class Category(Base):
    __tablename__ = 'category'

    name = Column(String(80), unique=True, nullable = False)

    id = Column(Integer, primary_key = True)
	
	

		
		
class Item(Base):
	__tablename__ = 'item'

	name = Column(String(80), nullable = False)
		
	price = Column(Integer, nullable = False)

	id = Column(Integer, primary_key = True)

	description = Column(String(250), nullable = False)	

	category_id = Column(Integer, ForeignKey('category.id'))
		
	category = relationship(Category)

	@property
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
