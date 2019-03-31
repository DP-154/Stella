import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as SessionMaker

engine = create_engine(os.environ['DATABASE_URL'], echo=True)

session_maker = SessionMaker(bind=engine)
