BUGS:
most recently created category doesn't show up in index


TO USE:

Run dbsetup.py to initialize the Database. (type python dbsetup.py)

Run application.py to initialize the webserver

Navigate to http://localhost:5000/ to access the app.




Mockups
	!html for each page
	!design URLS





Routing
	!flask

Templates & Forms
	!

CRUD Functionality
	!

API Endpoints
	!

Styling & Messages
	! (can i style the messages?)
AUTHORIZATION



This application allows you to create a basic Catalog including categories, and items within the categories.

Categories must have unique names.

You can add categories, and items to categories, using the in-app buttons.

Prices are stored as integers and divided by 100 when displayed to the user.  There is an in-app hint to help you remember to enter your prices x100.

There is also a JSON API Endpoint for each category, listing each item in the category (/category/<path:category_name>/JSON/) 
and also an endpoint for each item (/category/<path:category_name>/<int:item_id>/<path:item_name>/JSON/)

AUTHORIZATION is to be implemented to limit the user's ability to edit certain pages and items that don't belong to them.

