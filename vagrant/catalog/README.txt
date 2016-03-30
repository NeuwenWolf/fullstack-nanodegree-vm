KEY NOTES:

Web app runs on port 8080

BUGS:
When entering item names etc. and unique constraint fails, it does not fail gracefully and the app needs to be rebooted.
Could add error handling for this.


TO USE:

Run dbsetup.py to initialize the Database. (type python dbsetup.py)

Run application.py to initialize the webserver

Navigate to http://localhost:8080/ to access the app.








This application allows you to create a basic Catalog including categories, and items within the categories.

Categories must have unique names.

You can add categories, and items to categories, using the in-app buttons.

Prices are stored as integers and divided by 100 when displayed to the user.  There is an in-app hint to help you remember to enter your prices x100.

There is also a JSON API Endpoint for each category, listing each item in the category (/category/<path:category_name>/JSON/) 
and also an endpoint for each item (/category/<path:category_name>/<int:item_id>/<path:item_name>/JSON/)

Authentication is provided via Google+ only so you will require an account with Google to access the advanced app functionality.



