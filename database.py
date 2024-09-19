# database.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
from models import UserSchedule, SchoolSchedule, SchoolEvent  # Import models
from datetime import datetime 
import os
from dotenv import load_dotenv

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Setup SQLAlchemy session
load_dotenv()

DB_URL = os.getenv("CORRECT_DATABASE_URL")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
session = Session()



def get_or_create_user_schedule(discord_id, username=None):
    user_schedule = session.query(UserSchedule).filter_by(discord_id=discord_id).first()
    if not user_schedule:
        user_schedule = UserSchedule(discord_id=discord_id, username=username or "Placeholder")
        session.add(user_schedule)
        session.commit()
    return user_schedule

def change_one_block(user_id,username,block,course_name):  
    
    try:
        # Fetch or create the user's schedule
        user_schedule = get_or_create_user_schedule(user_id, username=username)
        
        # Map the block to the correct attribute (e.g., "1A" -> "A1")
        block_attr = block[1] + block[0]

        # Update the corresponding block with the new course name
        setattr(user_schedule, block_attr, course_name)
        session.commit()
        return 1
    except:
        return 0

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
        schedule_entry.block_order = new_block_order

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
        schedule_entry.block_times = new_block_times

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

def add_or_update_alternate_room(date_obj, block, course_name, alternate_room):
    try:
        # Retrieve the existing schedule entry for the given date
        schedule_entry = session.query(SchoolSchedule).filter_by(schedule_date=date_obj).first()

        if not schedule_entry:
            print(f"No schedule found for {date_obj}.")
            return 0

        # Load the existing courses JSON data
        courses = schedule_entry.courses or {}

        # Update or add the alternate room in the relevant block
        if block not in courses:
            courses[block] = {}
        
        # Update or add the course and alternate room
        courses[block][course_name] = alternate_room

        print("Courses before commit:", courses)

        # Reassign the updated courses to the entry
        schedule_entry.courses = courses
        
        # Force SQLAlchemy to recognize changes in the JSON field
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(schedule_entry, "courses")

        # Flush and commit
        session.flush()  # Force flush before commit
        session.commit()

        # Verify the changes were committed
        schedule_entry = session.query(SchoolSchedule).filter_by(schedule_date=date_obj).first()
        print("Courses after commit:", schedule_entry.courses)
        
        return 1

    except Exception as e:
        session.rollback()
        print(f"An error occurred while updating alternate room: {e}")
        return 0

def create_new_school_event(event_name, date_str, block_order_override, grades, location, start_time_str, end_time_str):
    """
    Create a new entry in the school_event table.
    
    Args:
        event_name (str): Name of the event
        date_str (str): Date in "YYYY-MM-DD" format.
        block_order_override (list): Blocks the event is taking place in. 
        grades (list(int)): The grades attending the event
        location (str): Location of the event. 
        start_time_str (str): Start time of the event. In "HH:mm" format
        end_time_str (str): End time of the event. In "HH:mm" format. 
        
    """
    
    try: 
        # Convert string date to a datetime object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Convert start_time and end_time to time objects
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
    except:
        return "Error: date or times can not be converted into datetime object."
        
    
    try:
        # Check if the date already exists
        existing_event = session.query(SchoolEvent).filter_by(event_name=event_name).first()
        if existing_event:
            print(f"Event {event_name} already exists in the database.")
            return None

        # Create a new SchoolEvent entry
        new_event = SchoolEvent(
            event_date=date_obj,
            event_name=event_name,
            block_order_override=block_order_override,
            grades=grades,
            location=location,  # corrected field name
            start_time=start_time,
            end_time=end_time
        )
        
        # Add the new entry to the session and commit it to the database
        session.add(new_event)
        session.commit()
        
        print(f"New event '{event_name}' added successfully.")
        return new_event

    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        return None

def edit_school_event(old_event_name, new_event_name=None, new_date_str=None, new_block_order_override=None, 
                      new_grades=None, new_location=None, new_start_time_str=None, new_end_time_str=None):
    """
    Edit an existing school event entry in the school_event table.
    
    Args:
        old_event_name (str): Current name of the event to be edited.
        new_event_name (str, optional): New name of the event. Defaults to None.
        new_date_str (str, optional): New date in "YYYY-MM-DD" format. Defaults to None.
        new_block_order_override (list, optional): New blocks the event is taking place in. Defaults to None.
        new_grades (list(int), optional): New list of grades attending the event. Defaults to None.
        new_location (str, optional): New location of the event. Defaults to None.
        new_start_time_str (str, optional): New start time of the event in "HH:mm" format. Defaults to None.
        new_end_time_str (str, optional): New end time of the event in "HH:mm" format. Defaults to None.
    
    Returns:
        The updated event or None if an error occurred.
    """
    try:
        # Retrieve the existing event by the old event name
        event = session.query(SchoolEvent).filter_by(event_name=old_event_name).first()
        
        if not event:
            print(f"No event found with name '{old_event_name}'")
            return None
        
        # Update the event name if provided
        if new_event_name:
            event.event_name = new_event_name
        
        # Update other fields if new values are provided
        if new_date_str:
            event.event_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        if new_block_order_override:
            event.block_order_override = new_block_order_override
        if new_grades:
            event.grades = new_grades
        if new_location:
            event.location = new_location
        if new_start_time_str:
            event.start_time = datetime.strptime(new_start_time_str, "%H:%M").time()
        if new_end_time_str:
            event.end_time = datetime.strptime(new_end_time_str, "%H:%M").time()
        
        # Commit the changes to the database
        session.commit()
        print(f"Event '{old_event_name}' updated successfully.")
        return event

    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        return None



event_name = "University Fair"
date_str = "2024-09-19"  # Assuming tomorrow is 2024-09-13
block_order_override = ["2B"]
grades = [10]
location = "Saint Georges"
start_time_str = "09:35"
end_time_str = "11:15"

create_new_school_event(event_name, date_str, block_order_override, grades, location, start_time_str, end_time_str)
old_event_name = "CUE Fair"
new_event_name = "CUE Fair"
new_location = "SGS(Head to 2B class first)"

edit_school_event(old_event_name, new_location=new_location)