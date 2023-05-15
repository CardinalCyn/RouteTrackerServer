#flask-sessions mongodb doesn't work, so i have to create my own library :/
"""
session handler for mongo db, has properties id,username,creation and exp
when user wants to login, creates session, and sets exp
pulls data from session id to find user of session id
delete session id when expired, or when to log out
deletes expired sessions on certain interval
"""
import datetime
import uuid
from db import sessions_collection
from apscheduler.schedulers.background import BackgroundScheduler

def create_session(username):
    """
    creates session
    session id is uuid
    created at is now, exp is 1 week from now
    """
    now=datetime.datetime.now()
    session_id=uuid.uuid4()
    session= {
        '_id':str(session_id),
        'username':username,
        "created_at":now,
        'expiration':now+datetime.timedelta(weeks=1)
    }
    sessions_collection.insert_one(session)
    return session_id

def get_session(session_id):
    """
    looks for session, deletes it if expired
    returns session otherwise
    """
    session= sessions_collection.find_one({"_id":session_id})
    if session is None:
        return None
    if session["expiration"]<datetime.datetime.now():
        sessions_collection.delete_one({"_id":session_id})
        return None
    return session
def delete_session(session_id):
    """deletes sessions of id passed in"""
    sessions_collection.delete_one({"_id":session_id})
def delete_expired_sessions():
    """
    goes through sessions colelction, deletes all that are expired from now
    """
    sessions_collection.delete_many({'expiration':{"$lt":datetime.datetime.now()}})

# scheduler to delete expired sessions every 10 min
scheduler=BackgroundScheduler()
scheduler.add_job(delete_expired_sessions,'interval',minutes=10)
scheduler.start()
