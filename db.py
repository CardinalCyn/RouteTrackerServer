"""
Connects to db, and uses the users and sessions collections in the db

defines functions used in other modules:

"""
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import config
client = MongoClient(config.DB_LINK, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db=client["GoogleMapsRouteTracker"]
    users_collection=db["users"]
    sessions_collection=db["sessions"]
except Exception as e:
    print("Error connecting to MongoDB:", e)

def get_user_routes(username):
    """
    searches users coll for users, returns none if it cant find user by their username
    returns their routes otherwise
    """
    user_result=users_collection.find_one({"username":username})
    if user_result is None:
        return None
    return user_result.get('routes')

def push_user_route(username,route):
    """
    searches for user of a username,and pushes the desired route into their routes property
    returns routePushed if successful operation, notFound if not found
    """
    result=users_collection.find_one_and_update({"username":username},{"$push":{"routes":route}})
    if result:
        return "routePushed"
    return "userNotFound"
#

def delete_user_route(username,route_id):
    """
    searches user for user, gets their routes property.
    filters the route to delete from the routes array.
    """
    user = users_collection.find_one({"username": username})
    if user is None:
        return "userNotFound"
    routes = user["routes"]
    filtered_routes = [route for route in routes if route["routeId"] != route_id]
    result=users_collection.update_one(
        {"username": username}, {"$set": {"routes": filtered_routes}}
    )
    if result.modified_count>0:
        return "successfulDeletion"
    return "deleteRouteReqFailed"
