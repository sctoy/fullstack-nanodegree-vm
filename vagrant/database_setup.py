import os
import sys
# This brings in the various classes we will use from SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String
# This brings in the declarative_base class from SQLAlchemy
# which is the fundamental building block that mapped classes inherit
from sqlalchemy.ext.declarative import declarative_base
# This allows us to create foreign key relationships
from sqlalchemy.orm import relationship
# This allows us to create a new database
from sqlalchemy import create_engine

# This allows our class to inherit the features of SQLAlchemy
# This lets SQLAlchemy know that classes defined as base are special
# SQLAlchemy classes
Base = declarative_base() 

#######end of opening file configuration instructions #######

# Setup Restaurant table in DB
class Restaurant(Base):
	__tablename__ = 'restaurant'
	
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)

	# This is the decorated function that informs the JSON feed
	@property
	def serialize(self):
		#Returns object data in easily serializable format
		return {
			'name'			:self.name,
			'id'			:self.id,
		}


# Setup MenuItem table in DB
class MenuItem(Base):
	__tablename__ = 'menu_item' 
	
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	course = Column(String(250))
	description = Column(String(250))
	price = Column(String(8))
	restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
	restaurant = relationship(Restaurant)

	# This is the decorated function that informs the JSON feed
	@property
	def serialize(self):
		#Returns object data in easily serializable format
		return {
			'name'			:self.name,
			'description'	:self.description,
			'id'			:self.id,
			'price'			:self.price,
			'course'		:self.course,
		}

#######start of closing file configuration instructions #######
# This creates a new database. We could also connect to existing db here
# if one had already been created
engine = create_engine('sqlite:///restaurantmenu.db')

# This takes the classes we create above and adds them as tables to the db
# that was just created in the line above
Base.metadata.create_all(engine)