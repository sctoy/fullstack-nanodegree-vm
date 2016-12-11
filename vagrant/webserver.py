# This file is an exercise in creating a web server from scratch without the
# use of a frameworl like Flask or Django. This is good for reminding myself
# of the raw steps that must happen to make a web server work.

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import cgi

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

# Class that takes all of the built in capabilities of BaseHTTPRequestHandler
class webserverHandler(BaseHTTPRequestHandler):

	# do_GET provides the rules for getting the various URL a client requests
	def do_GET(self):
		try:
			# render /hello page which simply parrots user input
			if self.path.endswith("/hello"):
				# This handles the necessary communication btw client and server
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				# This is the simplistic html that creates the page on the client
				output = "<html><body>Hello!"
				output += "<form method='POST' enctype='multipart/form-data' \
					action='/hello'>"
				output += "<h2>What would you like me to say?</h2>" 
				output += "<input name='message' type='text' ><input type='submit'  \
					value='Submit'> </form>"
				output += "</body></html>"
				# This is the required instruction to show the 'output' on the client
				self.wfile.write(output)
				# This debug line will appear in the terminal
				print output # Debugging line
				return

			# render /hola page which parrots user input AND provides return to /hello
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body>&#161Hola! <a href = '/hello' > \
					Back to Hello</a>"
				output += "<form method='POST' enctype='multipart/form-data' \
					action='/hello'><h2>What would you like me to say?</h2>  \
					<input name='message' type='text' ><input type='submit'  \
					value='Submit'> </form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output # Debugging line
				return

			# render /restaurant page which lists restaurants
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body><h1>Restaurants</h1><p>"
				output += "<a href = '/restaurants/new'> Add a New Restaurant \
					</br></br></a>" 
				rests = session.query(Restaurant).all()
				for rest in rests:
					output += "%s" % rest.name
					output += "<br>"
					output += "<a href = '/restaurants/%s/edit' >Edit</a>" % \
						rest.id
					output += "&nbsp; &nbsp;"
					output += "<a href = '/restaurants/%s/delete' >Delete<p> \
						</a>" % rest.id
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			# render /new page which allows user to add restaurant to db
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = "<html><body><h1>New Restaurant Form</h1>"
				# Here is the first method other than 'GET'. 'POST' makes changes.
				output += "<form method='POST' enctype='multipart/form-data' \
					action='/restaurants/new' >" 
				output += "<input name='newRestaurantName' type='text' \
					placeholder = 'New Restaurant Name' >"
				output += "<input type='submit'  value='Create'> </form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return

			# render /edit page which allows user to edit restaurant name
			if self.path.endswith("/edit"):
				# .split breaks apart URL at the /s and then chooses the third [2]
				restIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id =
					restIDPath).one()
				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>"
					output += myRestaurantQuery.name
					output += "</h1>"
					output += "<form method='POST' enctype='multipart/form-data' \
						action='/restaurants/%s/edit' >" % restIDPath
					output += "<input name='newRestaurantName' type='text' \
						placeholder = '%s' >" % myRestaurantQuery.name
					output += "<input type='submit'  value='Rename'> </form>"
					output += "</body></html>"
					self.wfile.write(output)
					print output
					return

			# render /delete page to delete a restaurant
			if self.path.endswith("/delete"):
				restIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id =
					restIDPath).one()
				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>Are you sure you want to delete, "
					output += myRestaurantQuery.name
					output += "?</h1>"
					output += "<form method='POST' enctype='multipart/form-data' \
						action='/restaurants/%s/delete' >" % restIDPath
					output += "<input type= 'submit' value='Delete'>"
					output += "</form>"
					output += "</body></html>"
					self.wfile.write(output)
					print output
					return


		except IOError:
			self.send_error(404, "File not found %s" % self.path)
			
	# do_POST defines what to do with the various POST requests clients will make
	def do_POST(self):
		try:
			# Code to add a new restaurant to the DB
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('newRestaurantName')

				# Create new Restaurant class, then add new restaurant and commit
				newRestaurant = Restaurant(name = messagecontent[0])
				# session code comes from the imported sessionmaker code
				session.add(newRestaurant)
				session.commit()
				# This handles the necessary communication btw client and server
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()


			# Code to edit a restaurant
			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('newRestaurantName')
				restIDPath = self.path.split("/")[2]

				myRestaurantQuery = session.query(Restaurant).filter_by(id = 
					restIDPath).one()
				if myRestaurantQuery != []:
					myRestaurantQuery.name = messagecontent[0]
					session.add(myRestaurantQuery)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()


			# Code to delete a restaurant
			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('delRestaurantName')
				restIDPath = self.path.split("/")[2]

				myRestaurantQuery = session.query(Restaurant).filter_by(id = 
					restIDPath).one()
				if myRestaurantQuery != []:
					session.delete(myRestaurantQuery)
					session.commit()
					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

				
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()


	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()