from config import CUSTOM_BLOCK_TIMES, CUSTOM_BLOCK_ORDERS, SPECIAL_UNIFORM_DATES, SCHEDULE_PATTERN, DAYS_OFF, CUSTOM_DAYS_OFF, TIME_SLOTS, SCHEDULE_START, ROOMS_FOR_COURSES
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

def get_block_times_for_date(date):
    school_info = get_school_info_from_date(date)
    
    if not school_info:
        return None
    
    return school_info.block_times
