# database.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
from models import UserSchedule, SchoolSchedule  # Import models

# Setup SQLAlchemy session
engine = create_engine('postgresql://u5hsl3t8vpl42s:pe6a13af81a75d26bf7ec16ed5614d296602e45c12f84e7dc965e840334951295@cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d66o2tq3s18vlt')
Session = sessionmaker(bind=engine)
session = Session()

def get_or_create_user_schedule(discord_id, username=None):
    user_schedule = session.query(UserSchedule).filter_by(discord_id=discord_id).first()
    if not user_schedule:
        user_schedule = UserSchedule(discord_id=discord_id, username=username or "Placeholder")
        session.add(user_schedule)
        session.commit()
    return user_schedule

def save_user_schedule(discord_id, schedule_data):
    user = session.query(UserSchedule).filter_by(discord_id=discord_id).first()
    if not user:
        user = UserSchedule(discord_id=discord_id, username="Placeholder")
        session.add(user)
    
    for block, course in schedule_data.items():
        setattr(user, block, course)
    
    session.commit()

def get_same_class(block, course_name):
    # Convert the block format (e.g., '1A' to 'A1') Colums in database are in A1,B1,C1, etc
    block =  block[1] + block[0]
    # block  = block.lower()
    # Perform the query using SQLAlchemy ORM
    try:
        # Check if the block exists in the UserSchedule model
        if hasattr(UserSchedule, block):
            # Query for users in the same class for that block
            results = session.query(UserSchedule.discord_id).filter(getattr(UserSchedule, block) == course_name).all()
            
            # Extract discord_id from the result set
            return [result.discord_id for result in results]
        else:
            print(f"Block {block} does not exist in the UserSchedule model")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def compare_schedule(discord_id1, discord_id2): 
    """
    Compare the course schedules of two users and return their schedules in two separate dictionaries.
    """

    discord_id1 = str(discord_id1)
    discord_id2 = str(discord_id2)
    # Retrieve user schedules from the database
    user1 = session.query(UserSchedule).filter_by(discord_id=discord_id1).first()
    user2 = session.query(UserSchedule).filter_by(discord_id=discord_id2).first()

    # Initialize dictionaries to store schedules
    schedule1 = {}
    schedule2 = {}

    # Check if the first user exists and populate schedule1
    if user1:
        schedule1 = {
            '1A': user1.A1,
            '1B': user1.B1,
            '1C': user1.C1,
            '1D': user1.D1,
            '1E': user1.E1,
            '2A': user1.A2,
            '2B': user1.B2,
            '2C': user1.C2,
            '2D': user1.D2,
            '2E': user1.E2
        }
    else:
        schedule1 = {'error': 'User 1 not found'}

    # Check if the second user exists and populate schedule2
    if user2:
        schedule2 = {
            '1A': user2.A1,
            '1B': user2.B1,
            '1C': user2.C1,
            '1D': user2.D1,
            '1E': user2.E1,
            '2A': user2.A2,
            '2B': user2.B2,
            '2C': user2.C2,
            '2D': user2.D2,
            '2E': user2.E2
        }
    else:
        schedule2 = {'error': 'User 2 not found'}

    # Return the schedules in a tuple
    return schedule1, schedule2