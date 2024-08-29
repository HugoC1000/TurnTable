from dotenv import load_dotenv
load_dotenv()


import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserSchedule(Base):
    __tablename__ = 'user_schedules'
    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    # Schedule columns
    A1 = Column(String)
    B1 = Column(String)
    C1 = Column(String)
    D1 = Column(String)
    E1 = Column(String)
    A2 = Column(String)
    B2 = Column(String)
    C2 = Column(String)
    D2 = Column(String)
    E2 = Column(String)

# Connect to the Heroku PostgreSQL database
DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)

# Create the tables in the database
Base.metadata.create_all(engine)
