"""
server routes for client to make requests to
allows for logging in, registering, session checking
retrieving, creating, deleting routes
logging out
"""
import uuid
from flask import request,make_response
import bcrypt
from db import users_collection,get_user_routes,push_user_route,delete_user_route
from utils.input_validation import validate_username,validate_password,validate_route
from flask_cors import cross_origin
from sessions import create_session,get_session,delete_session
from maps import init_get_directions
import config

def create_routes(app):
    """
    declares routes, allows us to put routes in here instead of apps.py
    cross origin allows us to check for cookies
    """
    @app.route("/login", methods=["POST"])
    @cross_origin(supports_credentials=True)
    def login():
        """
        gets data from user, checks if username password are valid
        checks user pass to hashed pw in db
        creates session if valid, sets cookie w/ session id
        """
        try:
            if request.method == "POST":
                request_data = request.get_json()
                username = request_data.get('username')
                password = request_data.get('password')
                if validate_username(username) != "usernameValid":
                    return {'status': "loginFailure", 'message': validate_username(username)}
                if validate_password(password) != "passwordValid":
                    return {'status': "loginFailure", 'message': validate_password(password)}
                user_search_results = users_collection.find_one({'username': username})
                if user_search_results:
                    hashed = user_search_results.get('password')
                    if bcrypt.checkpw(password.encode('utf-8'), hashed):
                        session_id = create_session(username)
                        response = make_response({
                            'status': "loginSuccess", 'message': "Login request success"})
                        response.set_cookie('session_id', str(session_id).encode('utf-8'),
                                            samesite='None', secure='True', domain=config.DOMAIN)
                        return response
                    return {'status': "loginFailure", 'message': "That password is incorrect"}
                return {'status': "loginFailure", 'message': "That username was not found"}
        except Exception as e:
            print(str(e))
            return {'status': "loginFailure", 'message': f"An error occurred: {str(e)}"}
        return {'status': "loginFailure", 'message': "Login request failed"}

    @app.route("/register", methods=["POST"])
    @cross_origin(supports_credentials=True)
    def register():
        """
        gets data from user, checks if username password are valid
        checks if a user of that username exists
        hashes pw, inserts it into db.
        if successful, creates session/ cookie, inserts into browser
        returns fail otherwise
        """
        try:
            if request.method == "POST":
                request_data = request.get_json()
                username = request_data.get('username')
                password = request_data.get('password')
                if validate_username(username) != "usernameValid":
                    return {'status': "registerFailure", 'message': validate_username(username)}
                if validate_password(password) != "passwordValid":
                    return {'status': "registerFailure", 'message': validate_password(password)}
                user_search_result = users_collection.find_one({'username': username})
                if user_search_result:
                    return {
                        'status': "registerFailure",
                        'message': "A user with that username already exists"
                    }
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                insert_result = users_collection.insert_one(
                    {'username': username, 'password': hashed, 'routes': []})
                if insert_result:
                    session_id = create_session(username)
                    response = make_response({
                        'status': "registerSuccess", 'message': "Register request success"})
                    response.set_cookie('session_id', str(session_id).encode('utf-8'),
                                        samesite='None', secure='True', domain=config.DOMAIN)
                    return response
                return {
                    'status': "registerFailure", 'message': "Register was unsuccessful, try again later"}
        except Exception as e:
            return {'status': "registerFailure", 'message': str(e)}

    @app.route("/checkSession",methods=["GET"])
    @cross_origin(supports_credentials=True)
    def check_session():
        """
        pulls session id from cookie
        if its not valid in db, deletes the cookie
        otherwise returns success
        """
        if request.method=="GET":
            if 'session_id' in request.cookies:
                session_id=request.cookies.get('session_id')
                user_session=get_session(session_id)
                if user_session is None:
                    response=make_response({'status':"notLoggedIn"})
                    response.delete_cookie('session_id')
                    return response
                username=user_session.get('username')
                return {"status":'signedIn', 'message':'Cookies found','username':username}
            return {"status":'notSignedIn','message':'No cookies in browser'}
        return {"status":"notSignedIn",'message':"requestFailed"}

    @app.route("/getRoutes",methods=["GET"])
    @cross_origin(supports_credentials=True)
    def get_routes():
        """
        checks session cookie
        if valid, gets username and their routes
        uses db.py to pull user routes
        """
        if request.method == "GET":
            if 'session_id' in request.cookies:
                session_id = request.cookies.get('session_id')
                user_session = get_session(session_id)
                if user_session is None:
                    return {"status":"sessionNotFound"}
                username = user_session.get('username')
                user_routes = get_user_routes(username)
                return {"status": "sessionFound", 'userRoutes': user_routes}
            return {"status":"sessionNotFound"}
        return {"status": "getRoutesReqFailed"}

    @app.route('/createRoute',methods=["POST"])
    @cross_origin(supports_credentials=True)
    def create_route():
        """
        checks valid session
        checks if length of user routes is lower than 10
        we are creating a route
        need properties: routename,routefrom,routeto,desiredroutetime,routeurl,routeid
        we are gonna modify the users request to be suitable for route
        get the route hours and mins from user, transform to secs, set it in req data
        remove route time prop since unnecessary
        pull route time with init_get_directions from google maps
        if its valid, store it with maps url in req data, otherwise return fail
        create route id w uuid, store it in req data
        use push user route to store route in db, if success return
        otherwise return fail
        """
        if request.method== "POST":
            if 'session_id' in request.cookies:
                session_id=request.cookies.get('session_id')
                user_session= get_session(session_id)
                if user_session is None:
                    return {"status":"sessionNotFound"}
                username=user_session.get('username')
                user_routes = get_user_routes(username)
                if len(user_routes)>=10:
                    return {"status":"You have a reached your maximum of 10 routes"}
                request_data = request.get_json()
                route_hours=request_data.get("routeTime").get('routeTimeHours')
                route_minutes=request_data.get('routeTime').get('routeTimeMinutes')
                validation_result=validate_route(request_data)
                if validation_result !="validRoute":
                    return {'status':validation_result}
                desired_route_time=route_hours*60*60+route_minutes*60
                request_data["desiredRouteTime"]=desired_route_time
                del request_data["routeTime"]
                route_result=init_get_directions(request_data.get("routeFrom").get('fromLocationPlaceId'),request_data.get('routeTo').get('toLocationPlaceId'),request_data.get("routeFrom").get('fromLocationAddress'),request_data.get("routeTo").get('toLocationAddress'))
                if route_result=="legNotFound" or route_result=="routeNotFound":
                    return {"status":"invalidRoute"}
                request_data["realRouteTime"]=route_result["travel_time"]
                request_data["routeUrl"]=route_result["maps_url"]
                request_data["routeId"]=str(uuid.uuid4())
                if push_user_route(username,request_data)=="routePushed":
                    return{"status":"routePushed"}
                return {"status":"routeNotPushed"}
            return {"status":"sessionNotFound"}
        return {"status":"createRoutesReqFailed"}
    @app.route('/deleteRoute',methods=["POST"])
    @cross_origin(supports_credentials=True)
    def delete_route():
        """
        get session, get route id
        make request to db to delete it from routes property
        """
        if request.method=="POST":
            if 'session_id' in request.cookies:
                session_id=request.cookies.get('session_id')
                user_session=get_session(session_id)
                username=user_session.get('username')
                if user_session is None:
                    return {"status":"sessionNotFound"}
                request_data=request.get_json()
                route_id=request_data.get('routeId')
                result=delete_user_route(username,route_id)
                return{"status":result}
            return {"status":"sessionNotFound"}
        return {"status":"deleteRouteReqFailed"}
    @app.route('/logout',methods=["GET"])
    @cross_origin(supports_credentials=True)
    def log_out():
        """
        if session id is present, deletes it in db
        makes response to delete browser cookie
        """
        if request.method=="GET":
            if 'session_id' in request.cookies: 
                session_id=request.cookies.get('session_id')
                delete_session(session_id)
                response=make_response({'status':"loggedOut"})
                response.delete_cookie('session_id')
                return response
            return {"status":"noSession"}
        return {"status":"logOutReqFailed"}
