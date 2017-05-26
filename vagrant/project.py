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

@app.route('/') # Need to edit this so it brings up a list of restaurants
# Lists all of the menu items for one restaurant
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
	return render_template('menu.html', restaurant = restaurant, items = items)

# Function to create a newMenuItem 
@app.route('/restaurants/<int:restaurant_id>/new/', methods = ['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
    	newItem = MenuItem(
    		name = request.form['name'], restaurant_id = restaurant_id)
    	session.add(newItem)
    	session.commit()
        flash("New Menu Item Created!")
    	return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
    	return render_template('newmenuitem.html', restaurant_id = restaurant_id)

# Function to editMenuItem 
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', 
    methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("Menu Item Edited!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id,
            menu_id = menu_id, item = editedItem)


# Function to deleteMenuItem 
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', 
    methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deletedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Menu Item Deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id = restaurant_id,
            menu_id = menu_id, item = deletedItem)


# Code that runs if this file is run directly (e.g. >>> python project.py)
if __name__ == '__main__':
    # Key to lock down the app. Not sure how or where this is used or called,
    # but one place is when you issue a POST command. Without this POSTs fail.
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
