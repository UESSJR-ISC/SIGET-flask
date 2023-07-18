import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.ext.declarative import declarative_base

Database = declarative_base()

if not "DOCKER" in os.environ:
    DB_PATH = "SIGET.sqlite"

else:
    DB_PATH = "/siget-vol/SIGET.sqlite"

engine = create_engine("sqlite:///" + DB_PATH)
db_session = scoped_session(sessionmaker(bind=engine))