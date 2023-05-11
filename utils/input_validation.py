"""
Validates username, password to ensure alphanumerican and ok length
validates route structure is valid
"""
import re
def validate_username(username):
    """
    checks username length and alphanumerical
    """
    if not 2<len(username)<=20:
        return "Usernames must be between 2 and 20 characters"
    reg_exp="^[a-zA-z0-9]+$"
    if re.match(reg_exp,username):
        return "usernameValid"
    return "Usernames must use alphanumerical characters"
def validate_password(password):
    """
    checks password length and alphanumerical
    """
    if not 6<=len(password)<=30:
        return "Passwords must be between 6 and 30 characters"
    reg_exp="^[a-zA-Z0-9]+$"
    if re.match(reg_exp,password):
        return"passwordValid"
    return "Passwords must use alphanumerical characters"
def validate_route(route):
    """
    checks routename len and alphanumerical
    makes sure minutes field is valid,
    hours must be positive and less than 10k
    route location addy and place id must be valid values and not equal to ea other
    """
    route_name=route.get('routeName')
    route_minutes=route.get('routeTime').get('routeTimeMinutes')
    route_hours=route.get('routeTime').get('routeTimeHours')
    route_from_location_address=route.get('routeFrom').get('fromLocationAddress')
    route_to_location_address=route.get('routeTo').get('toLocationAddress')
    route_from_place_id=route.get('routeFrom').get('fromLocationPlaceId')
    route_to_place_id=route.get('routeTo').get('toLocationPlaceId')
    if len(route_name)<1 or len(route_name)>20 or route_name.isalnum() is False:
        return "Route names must be between 1 and 20 characters, and use alphanumerical values"
    if (not route_minutes and route_minutes != 0) or \
        route_minutes >= 60 or route_minutes < 0 or \
        (not route_hours and route_hours != 0) or \
        route_hours < 0 or route_hours >= 10000:
        return "Route times must be valid values"
    if not route_from_location_address or \
        not route_to_location_address or \
        not route_from_place_id or \
        not route_to_place_id or \
        route_from_place_id==route_to_place_id:
        return "You must select two valid places for directions"
    return "validRoute"
