"""
    Handles api requests to google maps
    converts place ids to make api request, and retrieves the travel time
    updates all route times every 10 minutes
"""
import requests
from db import users_collection
from apscheduler.schedulers.background import BackgroundScheduler
import config
def encode_address(address):
    """
    Used for generating a google maps link for the user to be able to click on for directions
    converts the place name into one usable in links
    """
    address=address.replace(" ","+")
    address=address.replace(",","%2")
    return address

def init_get_directions(from_place_id,to_place_id,from_location_address,to_location_address):
    """
        Takes in place ids and address names
        makes an api request to google api to get travel time for from and to location
        also transforms addresses into one usable for links, returns a valid maplink
    """
    maps_url=""
    if from_location_address and to_location_address:
        from_encoded_address=encode_address(from_location_address)
        to_encoded_address=encode_address(to_location_address)
        maps_url = (
            'https://www.google.com/maps/dir/?api=1&origin='+
            from_encoded_address+'&origin_place_id='+from_place_id
            +'&destination='+to_encoded_address+
            '&destination_place_id='+to_place_id
        )
    api_url=(
        'https://maps.googleapis.com/maps/api/directions/json?origin=place_id:'
        +from_place_id+"&destination=place_id:"
        +to_place_id+"&mode=driving&traffic_model=best_guess&departure_time=now&key="+config.MAPS_API_KEY
    )
    response=requests.get(api_url,timeout=5)
    data=response.json()
    route = data.get("routes")
    if route:
        legs = route[0].get("legs", [])
        if legs:
            duration = legs[0].get("duration", {})
            travel_time = duration.get("value", 0)
            return {"travel_time":travel_time,"maps_url":maps_url}
        print("legNotFound")
        return "legNotFound"
    print("routeNotFound")
    return "routeNotFound"
def update_all_route_times():
    """
    iterates over all users in user collection and their routes
    gets their place ids, and uses init_get_directions to get travel time
    updates the rotues with the new time
    emits socket io event to client to retrieve updated routes
    """
    # import cant be in top level. we pull socket io from main.
    # if we put it toplevel, we get circular import err
    from main import socketio
    users = users_collection.find({}) # get all users
    for user in users:
        routes = user.get("routes")
        new_routes=[]
        for route in routes:
            route_to = route.get("routeTo")
            route_from = route.get("routeFrom")
            to_place_id = route_to.get("toLocationPlaceId")
            from_place_id = route_from.get("fromLocationPlaceId")
            real_route_time = init_get_directions(from_place_id, to_place_id,"","")
            route['realRouteTime']=real_route_time.get("travel_time")
            new_routes.append(route)
        users_collection.update_one({"username":user["username"]},{"$set":{"routes":new_routes}})
    socketio.emit('reloadRoutes',{'status':"success"})
# scheduler, runs every 10 mins to update all routes

scheduler=BackgroundScheduler()
scheduler.add_job(update_all_route_times,'interval',minutes=200)
scheduler.start()
