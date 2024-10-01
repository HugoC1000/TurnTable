from datetime import datetime, timedelta
import numpy as np
from database import modify_or_create_new_date
from config import SCHEDULE_PATTERN


def get_block_order_for_date(date_obj):
    # Define your schedule pattern, example provided    
    # Assuming the start date is September 4, 2024 (adjust as needed)
    start_date = datetime(2024, 10, 1).date()
    delta_week_days = np.busday_count(start_date, date_obj)
    day_index = delta_week_days % len(SCHEDULE_PATTERN)
    
    # Return block order based on the schedule pattern
    return SCHEDULE_PATTERN[day_index]

def create_schedules_for_dates(start_date, end_date):
    current_date = start_date
    uniform = "Regular uniform"
    is_school = True
    block_times_list = ["08:20-09:30", "09:35-10:45","-", "11:05-12:15", "-", "13:05-14:15", "14:20-15:30"]
    
    while current_date <= end_date:
        block_order_list = get_block_order_for_date(current_date)
        
        # Call the function to modify or create a new date entry
        result = modify_or_create_new_date(
            current_date, 
            uniform, 
            is_school, 
            block_order_list, 
            block_times_list
        )
        
        if result == 1:
            print(f"Successfully processed schedule for {current_date}.")
        else:
            print(f"Failed to process schedule for {current_date}.")
        
        # Move to the next date
        current_date += timedelta(days=1)

# Define the start and end dates
start_date = datetime(2024, 10, 1).date()
end_date = datetime(2024, 10, 4).date()

# Call the function to create schedules for the defined date range
create_schedules_for_dates(start_date, end_date)
