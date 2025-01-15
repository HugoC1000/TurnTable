import re
from datetime import datetime
from database import modify_or_create_new_date
import json

# Original schedule data
schedule_data = """
Mon, Jan 13	1A	1B	1D	1E	1Ca
Tue, Jan 14	2A	2B	2D	2E	2C
Wed, Jan 15	1A	1B	1E	1Cp	1D
Thu, Jan 16	2A	2B	2E	2C	2D
Fri, Jan 17	1A	1B	1Ca	1D	1E
Mon, Jan 20	2A	2B	2C	2D	2E
Tue, Jan 21	1A	1B	1D	1E	
Wed, Jan 22	2A	2B	2D	2E	2C
Thu, Jan 23	1A	1B	1E	1Cp	1D
Fri, Jan 24	2A	2B	2E	2C	2D
Mon, Jan 27	1A	1B	1Ca	1D	1E
Tue, Jan 28	2A	2B	2C	2D	2E
Wed, Jan 29	1A	1B	1D	1E	
Thu, Jan 30	2A	2B	2D	2E	2C
Fri, Jan 31	1A	1B	1E	1Cp	1D
Mon, Feb 3	2A	2B	2E	2C	2D
Tue, Feb 4	1Ca	1A	1B	1D	1E
Wed, Feb 5	2A	2B	2C	2D	2E
Thu, Feb 6	1Cp	1A	1B	1D	1E
Fri, Feb 7	2A	2B	2D	2E	2C
Mon, Feb 10	1A	1B	1E	1Ca	1D
Tue, Feb 11	2A	2B	2E	2C	2D
Wed, Feb 12	1A	1B	2E	1D	1E
Thu, Feb 13	2A	2B	2C	2D				
Tue, Feb 18	1A	1B	1D	1E	1Cp
Wed, Feb 19	2A	2B	2D	2E	2C
Thu, Feb 20	1A	1B	1E	1Ca	1D
Fri, Feb 21	2A	2B	2E	2C	2D
Mon, Feb 24	1A	1B	1Cp	1D	1E
Tue, Feb 25	2A	2B	2C	2D	2E
Wed, Feb 26	1A	1B	1D	1E	1Ca
Thu, Feb 27	2A	2B	2D	2E	2C
Fri, Feb 28	1A	1B	1E	1Cp	1D
Mon, Mar 3	2A	2B	2E	2C	2D
Tue, Mar 4	1A	1B	1Ca	1D	1E
Wed, Mar 5	2A	2B	2C	2D	2E
Thu, Mar 6	1A	1B	1D	1E	1Cp
Fri, Mar 7	2A	2B	2D	2E	2C
Mon, Mar 10	1A	1B	1E	1Ca	1D
Tue, Mar 11	2A	2B	2E	2C	2D
Wed, Mar 12	1A	1B	2E	1D	1E
Thu, Mar 13	2A	2B	2C	2D	Assm							
"""

term3 = """
Mon, Mar 31	1A	1B	1D	1E	1Cp
Tue, Apr 1	2A	2B	2D	2E	2C
Wed, Apr 2	1A	1B	1E	1Ca	1D
Thu, Apr 3	2A	2B	2E	2C	2D
Fri, Apr 4	1A	1B	1Cp	1D	1E
Mon, Apr 7	2A	2B	2C	2D	
Tue, Apr 8	1A	1B	1D	1E	2E
Wed, Apr 9	2A	2B	2D	2E	2C
Thu, Apr 10	1A	1B	1E	1Ca	1D
Fri, Apr 11	2A	2B	2E	2C	2D
Mon, Apr 14	1A	1B	1Cp	1D	1E
Tue, Apr 15	2A	2B	2C	2D	2E
Wed, Apr 16	1A	1B	1D	1E	1Ca
Thu, Apr 17	2A	2B	2D	2E	2C
Tue, Apr 22	1A	1B	1E	1Cp	1D
Wed, Apr 23	2A	2B	2E	2C	2D
Thu, Apr 24	1A	1B	1Ca	1D	1E
Fri, Apr 25	2A	2B	2C	2D	2E
Mon, Apr 28	1A	1B	1D	1E	1Cp
Tue, Apr 29	2A	2B	2D	2E	2C
Wed, Apr 30		1A	1B	1E	1D
Thu, May 1	2A	2B	2E	2C	2D
Fri, May 2	1A	1B	1Ca	1D	1E
Mon, May 5	2A	2B	2C	2D	2E
Tue, May 6	1A	1B	1D	1E	1Cp
Wed, May 7	2A	2B	2D	2E	2C
Thu, May 8	1A	1B	1E	1Ca	1D
Fri, May 9	2A	2B	2E	2C	2D
Mon, May 12	1A	1B	1Cp	1D	1E
Tue, May 13	2A	2B	2C	2D	2E
Wed, May 14	1A	1B	1D	1E	1Ca
Thu, May 15	2A	2B	2D	2E	2C
Fri, May 16	1A	1B	1E	1D	
Tue, May 20	2A	2B	2E	2C	2D
Wed, May 21	1A	1B	1D	1E	Assm
Thu, May 22	2A	2B	2C	2D	2E
Fri, May 23	1A	1B	1D	1E	1Cp
Mon, May 26	2A	2B	2D	2E	2C
Tue, May 27		1A	1B	1E	1D
Wed, May 28	2A	2B	2E	2C	2D
Thu, May 29	1A	1B	1Ca	1D	1E
Fri, May 30	2A	2B	2C	2D	2E
Mon, Jun 2	1A	1B	1D	1E	1Cp
Tue, Jun 3	2A	2B	2D	2E	2C
Wed, Jun 4	1A	1E	1D		
Thu, Jun 5	2A	2B	2C		
Fri, Jun 6	1B	2E	2D		
Mon, Jun 9	Math Exams and Make-up day				
Tue, Jun 10	2A	2B	2C	2D	2E
Wed, Jun 11	1A	1B	1D	1E	Final Assembly
Thu, Jun 12	SS Sports Day				
Fri, Jun 13	Half Day for faculty (report cards due)	
"""

data = [
    {"date": "03-09-2024", "block1": "G8 Assm", "block2": "SS Assm", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "04-09-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "05-09-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "06-09-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "09-09-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "10-09-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "2E", "block5": "1D"},
    {"date": "11-09-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "12-09-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "13-09-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "school_event"},
    {"date": "16-09-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "1C(P)"},
    {"date": "17-09-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "18-09-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "2D", "block5": "1D"},
    {"date": "19-09-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "school_event"},
    {"date": "20-09-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "23-09-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "24-09-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "1C(P)"},
    {"date": "25-09-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "26-09-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "2E", "block5": "1D"},
    {"date": "27-09-2024", "block1": "2A", "block2": "2B", "block3": "school_event", "block4": "2C", "block5": "2D"},
    {"date": "30-09-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "01-10-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "02-10-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "03-10-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "1C(P)"},
    {"date": "04-10-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "07-10-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1C(A)", "block5": "1D"},
    {"date": "08-10-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "09-10-2024", "block1": "1A", "block2": "1B", "block3": "1C(P)", "block4": "1D", "block5": "1E"},
    {"date": "10-10-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "11-10-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "school_event"},
    {"date": "14-10-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "15-10-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "16-10-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1C(A)", "block5": "1D"},
    {"date": "17-10-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "18-10-2024", "block1": "1A", "block2": "1B", "block3": "1C(P)", "block4": "1D", "block5": "1E"},
    {"date": "21-10-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "22-10-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "1C(A)"},
    {"date": "23-10-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "24-10-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1C(P)", "block5": "1D"},
    {"date": "25-10-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "28-10-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "29-10-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "30-10-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "31-10-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "2C"},
    {"date": "01-11-2024", "block1": "school_event", "block2": "2A", "block3": "2B", "block4": "2D", "block5": "2E"},
    {"date": "04-11-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1C(P)", "block5": "1D"},
    {"date": "05-11-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "06-11-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "07-11-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "08-11-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "school_event", "block5": "1E"},
    {"date": "11-11-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "12-11-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "13-11-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "14-11-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "15-11-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "18-11-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "19-11-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "2D", "block5": "1D"},
    {"date": "20-11-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "school_event"},
    {"date": "21-11-2024", "block1": "school_event", "block2": "school_event", "block3": "school_event", "block4": "school_event", "block5": "school_event"},
    {"date": "22-11-2024", "block1": "1A", "block2": "1B", "block3": "1C(P)", "block4": "1D", "block5": "1E"},
    {"date": "25-11-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "26-11-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "1C(A)"},
    {"date": "27-11-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "28-11-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1C(P)", "block5": "1D"},
    {"date": "29-11-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "02-12-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "03-12-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "04-12-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "1C(P)"},
    {"date": "05-12-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "06-12-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1D", "block5": "school_event"},
    {"date": "09-12-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "10-12-2024", "block1": "1A", "block2": "1B", "block3": "1C(A)", "block4": "1D", "block5": "1E"},
    {"date": "11-12-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "2E"},
    {"date": "12-12-2024", "block1": "1A", "block2": "1B", "block3": "1D", "block4": "1E", "block5": "school_event"},
    {"date": "13-12-2024", "block1": "2A", "block2": "2B", "block3": "2D", "block4": "2E", "block5": "2C"},
    {"date": "16-12-2024", "block1": "1A", "block2": "1B", "block3": "1E", "block4": "1C(P)", "block5": "1D"},
    {"date": "17-12-2024", "block1": "2A", "block2": "2B", "block3": "2E", "block4": "2C", "block5": "2D"},
    {"date": "18-12-2024", "block1": "1A", "block2": "1B", "block3": "2E", "block4": "1D", "block5": "1E"},
    {"date": "19-12-2024", "block1": "2A", "block2": "2B", "block3": "2C", "block4": "2D", "block5": "school_event"}
]

def format_date(date_str):
    import datetime
    date_obj = datetime.datetime.strptime(date_str, "%b %d %Y")
    return date_obj.strftime("%m-%d-%Y")

def parse_schedule_to_json(raw_data):
    result = []
    for line in raw_data.strip().split("\n"):
        # Split by whitespace and tabs, then remove empty entries
        parts = [part.strip() for part in line.split() if part.strip()]
        if not parts:
            continue

        # Parse date and blocks
        print(parts[1], parts[2])
        date_str = parts[1] + " " + parts[2] + " 2025"
        blocks = parts[3:]

        entry = {"date": format_date(date_str)}
        for i, block in enumerate(blocks):
            if block.strip():
                if block == "Assm":
                    entry[f"block{i + 1}"] = "1C(PA)"
                elif block == "1Cp":
                    entry[f"block{i + 1}"] = "1C(P)"
                elif block == "1Ca":
                    entry[f"block{i + 1}"] = "1C(A)"
                else:
                    entry[f"block{i + 1}"] = block.strip()

        result.append(entry)

    return result

term2data = parse_schedule_to_json(schedule_data)
# print(term2data)

def upload_schedule_to_db(schedule_data):
    for entry in schedule_data:
        print(entry)
        date_str = entry['date']
        try:
            blocks = [entry['block1'], entry['block2'], entry['block3'], entry['block4'], entry['block5']]
        except:
            blocks = [entry['block1'], entry['block2'], entry['block3'], entry['block4']]
        
        # Convert date to a datetime object
        date_obj = datetime.strptime(date_str, "%m-%d-%Y").date()
        
        # Define block times for this day
        if(len(blocks) == 4):
            if(date_str == "04-30-2025" or date_str == "05-27-2025"):
                block_times_list = ["09:35-10:45", "-", "11:05-12:15", "-", "13:05-14:15", "14:20-15:30"]
            else:
                block_times_list = ["08:20-09:30", "09:35-10:45", "-", "11:05-12:15", "-", "13:05-14:15"]
        else:
            block_times_list = ["08:20-09:30", "09:35-10:45", "-", "11:05-12:15", "-", "13:05-14:15", "14:20-15:30"]

        ceremonialDates = ["01-13-2025", "01-27-2025", "02-04-2025", "02-05-2025", "02-06-2025", "02-18-2025", "03-13-2025"]
        if(date_str in ceremonialDates):
            uniform = "Ceremonial"
        else:
            uniform = "Regular uniform"
        
        # Modify or create new date entry in the database
        result = modify_or_create_new_date(
            date_obj, 
            uniform,
            True,  # Assuming it's a school day
            blocks,  # The list of blocks for the day
            block_times_list  # The block times for the day
        )
        
        if result == 1:
            print(f"Successfully processed schedule for {date_obj}.")
        else:
            print(f"Failed to process schedule for {date_obj}.")

# Call the function to upload the schedule
upload_schedule_to_db(term2data)

