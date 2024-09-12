# database.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
from models import UserSchedule, SchoolSchedule  # Import models
from datetime import datetime 

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

def create_new_date(date_str, is_school_open, courses, block_order, block_times,uniform):
    """
    Create a new entry in the school_schedule table.
    
    Args:
        date_str (str): Date in "YYYY-MM-DD" format.
        is_school_open (bool): Whether the school is open on that date.
        courses (dict): Dictionary containing course names and alternate rooms. Example: {"Math": "Room 101"}.
        block_order (list): List of block order for the day. Example: ["A1", "B2", "C1", "D2"].
        block_times (list): List of block times for the day. Example: ["08:00-09:00", "09:10-10:10", ...].
        uniform(str): The uniform. 
    """
    # Convert string date to a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    
    try:
        # Check if the date already exists
        existing_date = session.query(SchoolSchedule).filter_by(schedule_date=date_obj).first()
        if existing_date:
            print(f"Date {date_str} already exists in the database.")
            return None

        # Create a new ScheduleDate entry
        new_date = SchoolSchedule(
            schedule_date=date_obj,
            uniform = uniform,
            school_open=is_school_open,
            courses=courses,
            block_order=block_order,
            block_times=block_times,
            
        )
        
        # Add the new entry to the session and commit it to the database
        session.add(new_date)
        session.commit()
        
        print(f"New date {date_str} added successfully.")
        return new_date

    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred on line 144: {e}")
        return None

def get_school_info_from_date(date):
    return session.query(SchoolSchedule).filter_by(schedule_date=date).first()

def edit_uniform_for_date(date,new_uniform):
        # Query the database for the existing schedule entry for that date
    schedule_entry = session.query(SchoolSchedule).filter_by(schedule_date=date).first()

    if not schedule_entry:
        return 1

    try:
        # Update the uniform
        schedule_entry.uniform = new_uniform

        # Commit the changes to the database
        session.commit()

        return 2
    except Exception as e:
        session.rollback()  # Rollback in case of an error
        print(f"An error occurred while updating the uniform: {e}")
        return None

def edit_block_order_for_date(date,new_block_order):
    # Query the database for the existing schedule entry for that date
    schedule_entry = session.query(SchoolSchedule).filter_by(schedule_date=date).first()

    if not schedule_entry:
        return 1

    try:
        # Update the block order
        
        print(new_block_order)
        schedule_entry.new_block_order = new_block_order

        # Commit the changes to the database
        session.commit()

        return 2
    except Exception as e:
        session.rollback()  # Rollback in case of an error
        print(f"An error occurred while updating the block order: {e}")
        return None
    
def edit_block_times_for_date(date,new_block_times):
        # Query the database for the existing schedule entry for that date
    schedule_entry = session.query(SchoolSchedule).filter_by(schedule_date=date).first()

    if not schedule_entry:
        return 1

    try:
        # Update the uniform
        schedule_entry.new_block_times = new_block_times

        # Commit the changes to the database
        session.commit()

        return 2
    except Exception as e:
        session.rollback()  # Rollback in case of an error
        print(f"An error occurred while updating the uniform: {e}")
        return None

def modify_or_create_new_date(date_obj, uniform, is_school, block_order_list, block_times_list):
        # Check if the date already exists
    schedule_entry = session.query(SchoolSchedule).filter_by(schedule_date=date_obj).first()

    if schedule_entry:
        # Update existing entry
        try:
            schedule_entry.uniform = uniform
            schedule_entry.school_open = is_school
            schedule_entry.block_order = block_order_list
            schedule_entry.block_times = block_times_list

            session.commit()
            return 1
        except Exception as e:
            session.rollback()  # Rollback in case of error
            print(f"An error occurred while updating the schedule: {e}")
            return 0
    else:
        # Create new entry
        try:
            new_schedule = SchoolSchedule(
                schedule_date=date_obj,
                uniform=uniform,
                school_open=is_school,
                block_order=block_order_list,
                block_times=block_times_list
            )

            session.add(new_schedule)
            session.commit()
            return 1
        except Exception as e:
            session.rollback()  # Rollback in case of error
            print(f"An error occurred while creating the schedule: {e}")
            return 0

create_new_date("2024-09-13",True,{"2B": {"PE 10 Brenko" : "Lawn Bowling Place"}},["2A","2B","2C","2D","school_event"],["08:20-09:30", "09:35-10:45", "-", "11:05-12:15", "-", "13:05-14:15", "14:20-15:30"],"PE Uniform allowed all day")