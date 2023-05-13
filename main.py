"""
Initializes a Flask app and sets up the necessary configuration to connect it to an Angular client. 

- Uses flask_cors to enable CORS with the client link specified in the configuration file.
- Sets a secret key for session encoding and enables cookies in the browser.
- Loads routes from the 'routes' module.
- Uses flask_socketio to connect to the Angular client.
- Requires an SSL certificate to run the app, which can be generated using 'mkcert'.

"""
from flask import Flask
from flask_session import Session
import routes
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import config
# flask boilerplate
app = Flask(__name__)
# cors to connect to angular server only
CORS(app,origins=[config.CLIENT_LINK], methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"])
# secret for session encoding, and allows us to set cookies in browser
app.config["SECRET_KEY"]=config.SESSION_SECRET_KEY
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
Session(app)
# load routes
routes.create_routes(app)
# socket io, connects to angular
socketio = SocketIO(app, cors_allowed_origins=config.CLIENT_LINK)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
    
# you need an ssl cert, used mkcert to generate it in root
# to run, use:
# flask run --cert=local-cert.pem --key=local-key.pem
