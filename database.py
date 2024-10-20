# database.py

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
from models import UserSchedule, SchoolSchedule, SchoolEvent, Reminder, UserPreferences  # Import models
from datetime import datetime, time
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


# User Schedule Related Commands
def get_or_create_user_schedule(discord_id, username=None):
    user_schedule = session.query(UserSchedule).filter_by(discord_id=discord_id).first()
    if not user_schedule:
        user_schedule = UserSchedule(discord_id=discord_id, username=username or "Placeholder")
        session.add(user_schedule)
        session.commit()
    # print("Entered this succesfully")
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


# School Info
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


# School Events
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

def delete_school_event_db(event_name):
    """
    Delete a school event entry from the school_event table.
    
    Args:
        event_name (str): Name of the event to be deleted.
    
    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    try:
        # Retrieve the event by the event name
        event = session.query(SchoolEvent).filter_by(event_name=event_name).first()
        
        if not event:
            print(f"No event found with name '{event_name}'")
            return False
        
        # Delete the event
        session.delete(event)
        session.commit()
        print(f"Event '{event_name}' deleted successfully.")
        return True

    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        return False

def get_school_events_for_date(date_str):
    """
    Retrieve school events scheduled for a specific date.

    Args:
        target_date (date): The date for which to retrieve school events.

    Returns:
        list: A list of dictionaries where each dictionary represents an event.
    """
    
    date_obj = date_str
    
    try:
        # Query the database for events on the target_date
        events = session.query(SchoolEvent).filter_by(event_date=date_obj).all()

        # Format the results into a list of dictionaries
        event_list = [{
            'name': event.event_name,
            'block': event.block_order_override,  # List of blocks the event affects
            'start_time': event.start_time.strftime("%H:%M") if event.start_time else None,
            'end_time': event.end_time.strftime("%H:%M") if event.end_time else None,
            'location': event.location,
            'grades': event.grades  # List of grades or -1 if applies to all grades
        } for event in events]

        return event_list

    except Exception as e:
        print(f"An error occurred while retrieving events: {e}")
        return []


def create_new_reminder_db(reminder_title, description, due_date_str, tag, reminder_for, user_created, grade=None, class_block=None, class_name=None):
    """
    Create a new entry in the reminders table.
    
    Args:
        reminder_title (str): Title of the reminder.
        description (str): Description of the reminder.
        due_date_str (str): Due date in "YYYY-MM-DD" format.
        tag (str): Either "Assignment", "Exam", "Project", or "Uniform".
        display_for (str): Either "All", "Grade-Wide", "Specific Class".
        user_created (str): Username of the person creating the reminder.
        grade (int, optional): Grade level reminder (required if display_for is "Grade-Wide").
        class_block (str, optional): The class block (required if display_for is "Specific Class").
        class_name (str, optional): The course name (required if display_for is "Specific Class").
    
    Returns:
        The newly created reminder or None if an error occurred.
    """
    
    try:
        # Convert the string date to a datetime object
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"Error: Could not convert due date '{due_date_str}' to a date object. Error: {e}")
        return None
    
    try:
        # Check if a reminder with the same title already exists
        existing_reminder = session.query(Reminder).filter_by(reminder_title=reminder_title).first()
        if existing_reminder:
            print(f"Reminder '{reminder_title}' already exists in the database.")
            return None
        
        # Handle display_for logic
        if reminder_for == "Grade-Wide" and grade is None:
            raise ValueError("Grade must be specified when 'Grade-Wide' is selected.")
        elif reminder_for == "Specific Class" and (class_block is None or class_name is None):
            raise ValueError("Both class_block and class_name must be provided when 'Specific Class' is selected.")
        elif reminder_for not in ["All", "Grade-Wide", "Specific Class"]:
            raise ValueError(f"Invalid display_for value: '{reminder_for}'. Must be 'All', 'Grade-Wide', or 'Specific Class'.")
        
        # Create a new Reminder object
        new_reminder = Reminder(
            reminder_title=reminder_title,
            text=description.strip(),
            due_date=due_date,
            tag=tag,
            display_for=reminder_for,
            grade=grade if reminder_for == "Grade-Wide" else None,
            class_block=class_block if reminder_for == "Specific Class" else None,
            class_name=class_name if reminder_for == "Specific Class" else None,
            last_user_modified=user_created  # Track who created the reminder
        )
        
        # Add the new reminder to the session and commit to the database
        session.add(new_reminder)
        session.commit()
        
        print(f"New reminder '{reminder_title}' added successfully.")
        return new_reminder

    except ValueError as ve:
        print(f"Validation error: {ve}")
        return None
    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        return None

    
def edit_reminder_db(reminder_id, user_changed, new_reminder_title=None, new_description=None, new_due_date_str=None, 
                      new_tag=None, new_reminder_for=None, new_grade=None, new_block=None, new_course_name=None):
    """
    Edit an existing reminder entry in the reminders table.
    
    Args:
        reminder_id (int): ID of the reminder to be edited.
        user_changed (str): Username of the person who executed the command.
        new_reminder_title (str, optional): New title of the reminder. Defaults to None.
        new_description (str, optional): New description of the reminder. Defaults to None.
        new_due_date_str (str, optional): New due date in "YYYY-MM-DD" format. Defaults to None.
        new_tag (str, optional): New tag of the reminder. Must be one of ["Assignment", "Exam", "Project", "Uniform", "Other"]. Defaults to None.
        new_reminder_for (str, optional): Either "All", "Grade-Wide", or "Specific Class". Defaults to None.
        new_grade (int, optional): Grade level reminder (required if display_for is "Grade-Wide"). Defaults to None.
        new_block (str, optional): New class block, e.g., "1A", "2B", etc. (required if display_for is "Specific Class"). Defaults to None.
        new_course_name (str, optional): New course name (required if display_for is "Specific Class"). Defaults to None.
    
    Returns:
        The updated reminder or None if an error occurred.
    """
    try:
        # Retrieve the existing reminder by ID
        reminder = session.query(Reminder).filter_by(id=reminder_id).first()
        
        if not reminder:
            print(f"No reminder found with ID '{reminder_id}'")
            return None
        
        # Update the reminder fields if new values are provided
        if new_reminder_title:
            reminder.reminder_title = new_reminder_title
        if new_description:
            reminder.text = new_description
        if new_due_date_str:
            reminder.due_date = datetime.strptime(new_due_date_str, "%Y-%m-%d").date()
        if new_tag:
            reminder.tag = new_tag
        if new_reminder_for:
            reminder.display_for = new_reminder_for
            
            # Handle changes based on display_for
            if new_reminder_for == "Grade-Wide" and new_grade is not None:
                reminder.grade = new_grade
                reminder.class_block = None
                reminder.class_name = None
            elif new_reminder_for == "Specific Class" and new_block and new_course_name:
                reminder.class_block = new_block
                reminder.class_name = new_course_name
                reminder.grade = None
            elif new_reminder_for == "All":
                reminder.grade = None
                reminder.class_block = None
                reminder.class_name = None
            else:
                raise ValueError("Invalid or incomplete information provided for 'display_for'.")
        
        # Update the last user who modified the reminder
        reminder.last_user_modified = user_changed
        
        # Commit the changes to the database
        session.commit()
        print(f"Reminder '{reminder.reminder_title}' updated successfully.")
        return reminder

    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred: {e}")
        return None

    
def delete_reminder_db(reminder_id):
    
    """
    Edit an existing school event entry in the school_event table.
    
    Args:
        reminder_id (int): Reminder id of the reminder to be edited. 
    Returns:
        The updated event or None if an error occurred.
    """
    
    
    event = session.query(Reminder).filter_by(id =reminder_id).first()

    # If no reminder is found, send an error message
    if event is None:
        return None

    # Delete the reminder from the database
    session.delete(event)
    session.commit()

    # Send a confirmation message
    return event

def get_reminders_for_user(user_id, user_courses, user_grade):
    """
    Retrieve reminders that are relevant to a user based on their grade and enrolled courses.

    Args:
        user_id (int): The ID of the user whose reminders need to be fetched.
        user_courses()
        user_grade
    
    Returns:
        List[Reminder]: A list of reminders relevant to the user.
    """

    try:
        # Retrieve reminders visible to all users
        all_reminders = session.query(Reminder).filter_by(display_for="All").all()

        # Retrieve reminders for the user's grade
        grade_wide_reminders = session.query(Reminder).filter_by(display_for="Grade-Wide", grade=user_grade).all()

        # Retrieve class-specific reminders based on the user's enrolled courses
        class_specific_reminders = []
        for block, course in user_courses.items():
            print(block, course)
            course_reminders = session.query(Reminder).filter_by(display_for="Specific Class", class_block=block, class_name=course).all()
            class_specific_reminders.extend(course_reminders)

        # Combine all the relevant reminders into a single list
        relevant_reminders = all_reminders + grade_wide_reminders + class_specific_reminders
        return relevant_reminders

    except Exception as e:
        session.rollback() 
        print(f"An error occurred while retrieving reminders: {e}")
        return []
    

def get_reminders_for_user_on_date(user_id, date, user_courses, user_grade):
    """
    Retrieve reminders relevant to a user for tomorrow's date, based on their grade and enrolled courses.

    Args:
        user_id (int): The ID of the user whose reminders need to be fetched.
        user_courses (dict): A dictionary of the user's enrolled courses.
        user_grade (int): The user's grade level.

    Returns:
        List[Reminder]: A list of reminders relevant to the user for tomorrow.
    """
    try:

        # Retrieve reminders visible to all users and due tomorrow
        all_reminders = session.query(Reminder).filter_by(display_for="All", due_date=date).all()

        # Retrieve reminders for the user's grade and due tomorrow
        grade_wide_reminders = session.query(Reminder).filter_by(display_for="Grade-Wide", grade=user_grade, due_date=date).all()

        # Retrieve class-specific reminders based on the user's enrolled courses and due tomorrow
        class_specific_reminders = []
        for block, course in user_courses.items():
            # print(block, course)
            course_reminders = session.query(Reminder).filter_by(display_for="Specific Class", class_block=block, class_name=course, due_date=date).all()
            # print(date)
            class_specific_reminders.extend(course_reminders)

        # Combine all the relevant reminders into a single list
        relevant_reminders = all_reminders + grade_wide_reminders + class_specific_reminders
        # print(relevant_reminders)
        return relevant_reminders

    except Exception as e:
        session.rollback()
        print(f"An error occurred while retrieving the reminders for {date}: {e}")
        return []

def delete_uniform_reminder(date_obj):
    """
    Deletes the uniform reminder for a given date if it exists.

    Args:
        date_obj (datetime.date): The date of the reminder to be deleted.

    Returns:
        bool: True if a reminder was deleted, False otherwise.
    """
    try:
        # Query the reminder by date, tag, and display_for
        reminder = session.query(Reminder).filter_by(due_date=date_obj, tag="Uniform", display_for="All").first()
        
        if reminder:
            # Delete the reminder if found
            session.delete(reminder)
            session.commit()
            return True
        return False  # No reminder found for the given date
    
    except Exception as e:
        session.rollback()  # Rollback in case of error
        print(f"An error occurred while deleting the uniform reminder: {e}")
        return False


def get_user_pref():
    try:
        user_preferences = session.query(UserPreferences).all()
        return user_preferences

    except Exception as e:
        print(f"An error occurred while retrieving reminders: {e}")
        return []
    
def set_user_pref(discord_id, notification_time = None, notification_method = None):
    try: 
        user_preferences = session.query(UserPreferences).filter_by(discord_id=discord_id).first()

        if not user_preferences:
            new_setting = UserPreferences(
                notification_method = notification_method,
                notification_time = notification_time,
                discord_id = discord_id,
            )
            
            session.add(new_setting)        
        else:
            if notification_time:
                user_preferences.notification_time = notification_time
            if notification_method:
                user_preferences.notification_method = notification_method
   
        session.commit()
        print(f"Setting  updated successfully.")
        return 1
        
    except Exception as e:
        print(f"An error occurred while setting user preferences: {e}")
        return []

set_user_pref("826334880455589918", notification_time="17:09")