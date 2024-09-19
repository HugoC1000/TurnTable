from config import CUSTOM_BLOCK_TIMES, CUSTOM_BLOCK_ORDERS, SPECIAL_UNIFORM_DATES, SCHEDULE_PATTERN, DAYS_OFF, CUSTOM_DAYS_OFF, TIME_SLOTS, SCHEDULE_START, ROOMS_FOR_COURSES, AP_FLEX
from datetime import datetime, timedelta
from database import get_school_info_from_date
import numpy as np

# Helper function to determine if a day is a day off
def is_day_off(date):
    return date.weekday() in DAYS_OFF or date in CUSTOM_DAYS_OFF


def get_blocks_for_date(date):
    
    school_info = get_school_info_from_date(date)
    
    if not school_info:
        return None
    
    return school_info.block_order

def get_uniform_for_date(date):
    school_info = get_school_info_from_date(date)
    
    if not school_info:
        return None
    
    return school_info.uniform
    # """Retrieve the block schedule for a specific date."""
    # if date in CUSTOM_BLOCK_ORDERS:
    #     return CUSTOM_BLOCK_ORDERS[date]
    
    # delta_week_days = np.busday_count(datetime(2024, 9, 4).date(), date)
    # day_index = delta_week_days % len(SCHEDULE_PATTERN)
    
    # if is_day_off(date) or date in CUSTOM_DAYS_OFF:
    #     return "No school"
    
    # return SCHEDULE_PATTERN[day_index]

def get_alt_rooms_for_date(date):
    school_info = get_school_info_from_date(date)
    
    if not school_info:
        return {}
    
    return school_info.courses
def get_block_times_for_date(date):
    school_info = get_school_info_from_date(date)
    
    if not school_info:
        return None
    
    return school_info.block_times

def get_ap_flex_courses_for_date(date):
    
    # Check if the date exists in the AP Flex schedule
    if date in AP_FLEX:
        return AP_FLEX[date]
    
    # If no AP Flex is found for the date, return an empty dictionary
    return {}

def has_set_courses(user_schedule):
    """Check if the user has set any courses."""
    return any([user_schedule.A1, user_schedule.B1, user_schedule.C1, user_schedule.D1, user_schedule.E1,
                user_schedule.A2, user_schedule.B2, user_schedule.C2, user_schedule.D2, user_schedule.E2])


def get_user_courses(user_schedule):
    """Return a dictionary of user courses mapped by block."""
    return {
        '1A': user_schedule.A1, '1B': user_schedule.B1, '1C': user_schedule.C1, '1C(A)' : user_schedule.C1, '1C(P)' : user_schedule.C1, '1C(PA)' : user_schedule.C1, '1D': user_schedule.D1, '1E': user_schedule.E1,
        '2A': user_schedule.A2, '2B': user_schedule.B2, '2C': user_schedule.C2, '2D': user_schedule.D2, '2E': user_schedule.E2
    }


def generate_schedule(user_schedule, schedule, block_times, alt_rooms, ap_flex_courses, user_courses, user_grade, school_events):
    """Generate the final schedule output for the day."""
    courses = []
    max_whitespace = get_max_whitespace(schedule, user_courses, ap_flex_courses, user_grade, school_events)
    print("Whitespace: ")
    print(max_whitespace)
    i=0
    
    for slot in schedule:
        if block_times[i] == "-":
            courses.append("-" * 20)
            i+=1
        
        if is_advisory(slot):
            course_info = handle_advisory(slot, user_courses.get(slot), ap_flex_courses, user_courses, alt_rooms)
        else:
            course_info = handle_regular_block(slot, user_schedule, user_courses, alt_rooms)
        
        for event in school_events:
            if slot in event['block'] and user_grade in event['grades']:
                course_info = (event['name'],event['location'])
                if event['start_time'] and event['end_time']:
                    block_times[i] = f"{event['start_time']-event['end_time']}"

        courses.append(format_schedule_entry(block_times[i], course_info, max_whitespace))
        i += 1
        
        

    return courses


def get_max_whitespace(schedule, user_courses, ap_flex_courses):
    """Calculate the max whitespace for alignment."""
    max_length = 0
    for slot in schedule:
        course = determine_course_name_for_slot(slot, user_courses, ap_flex_courses)
        #print("Course: " + course)
        max_length = max(max_length, len(course))
        #print(f"Max length: {max_length}")
    return max_length + 3


def determine_course_name_for_slot(slot, user_courses, ap_flex_courses,user_grade, school_events):
    #print("Slot")
    #print(slot) 
    """Determine the course for the current slot"""
    for event in school_events:
        if slot in event['block'] and user_grade in event['grades']:
            return event['name']
    
    if is_advisory(slot) and ap_flex_courses:
        matching_courses = [course for course in user_courses.values() if course in ap_flex_courses]
        if len(matching_courses) == 1:
            return "F: " + matching_courses[0]
        elif len(matching_courses) > 1:
            return "AP Flex conflict"
        advisory_type = "School Event" if slot == '1C(PA)' else "PEAKS" if slot == '1C(P)' else "Academics"
        return advisory_type
    return user_courses.get(slot, 'None')


def handle_advisory(slot, user_advisory, ap_flex_courses, user_courses, alt_rooms):
    """Handle the advisory block, including AP Flex check."""
    if ap_flex_courses:
        matching_courses = [course for course in user_courses.values() if course in ap_flex_courses]
        if len(matching_courses) == 1:
            return ("F: " + matching_courses[0], ap_flex_courses[matching_courses[0]])
        elif len(matching_courses) > 1:
            return ("AP Flex conflict", "")
        
        
    advisory_type = "School Event" if slot == '1C(PA)' else "PEAKS" if slot == '1C(P)' else "Academics"
    
    if advisory_type == "School Event":
        return (advisory_type, "")
    # Default to regular advisory if no AP Flex
    return (advisory_type, get_room_for_slot('1C', user_advisory, alt_rooms))


def handle_regular_block(slot, user_schedule, user_courses, alt_rooms):
    """Handle a regular block."""
    course = getattr(user_schedule, slot[1] + slot[0], 'None')
    
    room = get_room_for_slot(slot, course, alt_rooms)
    return (course, room)


def get_room_for_slot(slot, course, alt_rooms):
    """Get the room for a specific course and slot."""
    
    print(slot)
    print("-")
    print(course)
    if alt_rooms and alt_rooms.get(slot, {}).get(course, "Unknown Room") != "Unknown Room":
        return alt_rooms[slot][course]
    return ROOMS_FOR_COURSES.get(slot, {}).get(course, 'Unknown Room')


def format_schedule_entry(time, course_info, max_whitespace):
    """Format a schedule entry with aligned whitespace."""
    course, room = course_info
    print("Format schedule entry")
    print(course)
    print(room)
    print(max_whitespace)
    return f"{time}  {course}{' ' * (max_whitespace - len(course))}{room}"


def is_advisory(slot):
    """Check if the slot is an advisory block."""
    return slot in ['1C(PA)', '1C(P)', '1C(A)']

def get_next_course(user_schedule, schedule, block_times, alt_rooms, ap_flex_courses, user_courses):
    """Generate the final schedule output for the day."""
    current_time = datetime.now().time()
    courses = []

    max_whitespace = get_max_whitespace(schedule, user_courses, ap_flex_courses)
    i=0
    
    for slot in schedule:
        if block_times[i] == "-":
            i+=1
        print(slot)
        block_time_str = block_times[i]
        print(block_time_str)
        print(block_time_str.split('-')[0].strip())
        block_time = datetime.strptime(block_time_str.split('-')[0].strip(), "%H:%M").time()
        print(type(block_time))

            
        if current_time < block_time:
            next_course = getattr(user_schedule, slot[1] + slot[0], "None")

            # If no course set for this block, say no class
            if next_course == "None":
                return f"**Next:** {block_time_str} - No class for this block."
            else:
                if is_advisory(slot):
                    room = get_room_for_slot('1C', next_course, alt_rooms)
                else:
                    room = get_room_for_slot(slot, next_course, alt_rooms)
                return f"**Next:** {block_time_str} - {next_course} in {room}."
        i += 1

    return "School will be over after this class."