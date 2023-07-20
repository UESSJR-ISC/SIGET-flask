from flask import Flask

from flask_session import Session

from server_config import *

from database import Database
from database import engine
from database import db_session

import siget_models

app = Flask(__name__, static_url_path=STATIC_URL_PATH, static_folder=STATIC_FOLDER)
app.config.from_object(__name__)

Database.metadata.create_all(engine)
Session(app)

@app.teardown_request
def remove_session(ex=None):
    db_session.remove()

from siget_routes import *

if __name__ == '__main__':
    app.run('0.0.0.0', 5000, debug=True)
