# flask serverside code for GoogleMapsRouteTimer

# to use this app, you'll need to generate a certificate and key in the server root for https, as well as create config.py with properties:
# SESSION_SECRET_KEY='random session secret'
# CLIENT_LINK="https://localhost:4200"
# DB_LINK='mongodb://localhost:27017/'
# MAPS_API_KEY='your google maps api key here'
# DOMAIN='127.0.0.1'

# to run the server, i use flask run --cert local-cert.pem --key local-key.pem
# i use mkcert to generate the ssl files necessary

# the app currently complains about the socket io transport method, idk how to solve it in development

# app.py: uses cors to enable to requests to a client of a diff origin, and configures session settings to enable cross origin cookies.
# routes are loaded in app.py in order to make it more modular
# socket io is also used to emit an event to client to make it reload routes, and requires cors to do so

# db.py: connects to mongo db, responsible for returning user's routes array, creating route, and deleting route from mongo db

# maps.py: handles api reqs to google maps. uses place ids from client req to make api request to server and generate time to travel between points
# also has scheduler to update all route times among all users on an interval, as well as emit that to the client that the routes have been updated

# sessions.py: handles sessions code, since flask-session mongodb is deprecated/ unusable. creates sessions using flask-session, then i use a separate collection in mongodb to store
# session information. routes.py uses this to create sessions, delete sessions, and return user info based on the session id created. expired sessions are deleted on an interval

# routes.py: handles api routes for the client to use.
# login route: checks user input if valid len and alphanum. if valid, searches collection w/ property of username, and if found, checks hashed pw in db vs the one sent in body. 
# if successful, creates a cookie and makes session in db
# register route: checks user input if valid len and alphanum. if valid, checks if username already exists. if it doesnt, it hashes the pw and stores username, pw and empty routes into mongo user collection. sets cook and session afterwards
# checkSession route: checks if the user is logged in or not. if theres a session id in the req headers, itll check sessions_collection. if a session_id is in db, and not expired,
# it will return username, otherwise it will delete the cookie in the browser and return fail response
# getRoutes route: checks session, pulls username from session coll, and the pulls the user routes from user coll
# createRoute route: checks session, pulls username, and user's routes. check if len of routes>=10, returns if not. pulls the routetimehours and minutes from request,
# and converts it into seconds, and sets the seconds as desired route time. deletes previous prop of routetimehrs and mins since its not necessary. uses maps.py func to get
# time of route from the req body placeIds sent, as well as url to link to google maps directions of the places sent by req body. also generates and stores a uuid for the route id.
# these are all modifications to the req body, which is sent back to the client. 
# deleteRoute route: checks session, gets username. deletes the route w/ routeId sent by client.
# logout route: checks session, deletes in session coll, and sends response to client to delete the cookie in browser