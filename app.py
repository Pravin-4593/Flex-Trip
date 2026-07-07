from dotenv import load_dotenv
load_dotenv()

import os
import cloudinary_config

from flask import Flask

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

from routes.auth import *
from routes.trip import *
from routes.profile import *
from routes.social import *

if __name__ == "__main__":
    app.run(debug=False)