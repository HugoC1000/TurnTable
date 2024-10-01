from dotenv import load_dotenv
load_dotenv()

import os
from sqlalchemy import create_engine, Column, Integer, String, Time
from sqlalchemy import Date, Text, Boolean, JSON, ARRAY
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
    grade = Column(Integer)
    
class SchoolSchedule(Base):
    __tablename__ = 'school_schedules'

    id = Column(Integer, primary_key=True)
    schedule_date = Column(Date, nullable=False)
    uniform = Column(Text, nullable=False)
    school_open = Column(Boolean, nullable=False)
    courses = Column(JSON, nullable=True)  # Dictionary of course names and alternate rooms. Also implementation of AP Flex
    block_order = Column(ARRAY(Text), nullable=True)  # New column for block order (list of blocks, e.g., ['1A', '1B', '1C'])
    block_times = Column(ARRAY(Text), nullable=True)
    ap_flexes = Column(JSON, nullable=True)

class SchoolEvent(Base):
    __tablename__ = 'school_events'

    id = Column(Integer, primary_key=True)
    event_name = Column(String, nullable=False)          # Name of the event
    event_date = Column(Date, nullable=False)            # Date of the event
    block_order_override = Column(ARRAY(String), nullable=False)  # Blocks that the event overrides
    grades = Column(ARRAY(Integer), nullable=True)       # List of grades the event applies to; NULL for all grades
    location = Column(String, nullable=False)            # Location of the event
    start_time = Column(Time, nullable=False)            # Start time of the event
    end_time = Column(Time, nullable=False)              # End time of the event


class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    tag = Column(String)  # e.g., "Assignment", "Exam", "Project"
    notify_dm = Column(Boolean, default=False)
    notify_channel = Column(Boolean, default=False)
    
    class_block = Column(String)
    class_name = Column(String)
    
DB_URL = os.getenv("CORRECT_DATABASE_URL")
engine = create_engine(DB_URL)
# Create the tables in the database
Base.metadata.create_all(engine)
