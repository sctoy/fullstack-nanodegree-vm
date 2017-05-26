from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Creates an instance of the Flask class we imported from flask above
app = Flask(__name__)

# This tells the program which db to communicate
engine = create_engine('sqlite:///restaurantmenu.db')
# This line binds the db to the Base class from our database_setup so
# SQLAlchemy knows how to handle this
Base.metadata.bind = engine
# This creates a link between code executions and the engine we just created
# This allows us to hold various commands in a session prior to a commit
DBSession = sessionmaker(bind = engine)
# This is the local instance of DBSession
session = DBSession()


@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', restaurants = restaurants)

@app.route('/restaurants/new/', methods = ['GET','POST'])
def newRestaurant():
	if request.method == 'POST':
		newRest = Restaurant(
			name = request.form['name'])
		session.add(newRest)
		session.commit()
		flash("New Restaurant Created!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newrestaurant.html')

@app.route('/restaurants/<int:restaurant_id>/edit/', methods = ['GET','POST'])
def editRestaurant(restaurant_id):
	editedRest = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedRest.name = request.form['name']
		session.add(editedRest)
		session.commit()
		flash("Restaurant Name Edited")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editrestaurant.html', item = editedRest)

@app.route('/restaurants/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
	deletedRest = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		session.delete(deletedRest)
		session.commit()
		flash("Restaurant Deleted!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('deleterestaurant.html', item = deletedRest)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant = restaurant, items = items)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods = ['GET','POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(
			name = request.form['name'],
			price = request.form['price'],
			course = request.form['course'],
			description = request.form['description'],
			restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash("New Menu Item Created!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', 
	methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
			editedItem.price = request.form['price']
			editedItem.course = request.form['course']
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		flash("Menu Item Edited!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('editmenuitem.html', restaurant_id = restaurant_id,
			menu_id = menu_id, item = editedItem)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/',
	methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	deletedItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("Menu Item Deleted!")
		return redirect(url_for('showMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', restaurant_id = restaurant_id,
			menu_id = menu_id, item = deletedItem)

# Here we will make our JSON Feeds

# An API Endpoint JSON (GET Request) for all restaurants
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurant = [r.serialize for r in restaurants])  

# An API Endpoint JSON (GET Request) for all of the menu items for one restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return jsonify(MenuItems = [i.serialize for i in items])  

# MenuItem JSON code
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItems = menuItem.serialize)  


# This launches the code on this page if the page is called directly
if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)