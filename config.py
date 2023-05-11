# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from dotenv import load_dotenv
load_dotenv()
import os

SESSION_SECRET_KEY=os.getenv("SESSION_SECRET_KEY")
CLIENT_LINK=os.getenv("CLIENT_LINK")
DB_LINK=os.getenv("DB_LINK")
MAPS_API_KEY=os.getenv("MAPS_API_KEY")
DOMAIN=os.getenv("DOMAIN")
