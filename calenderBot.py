import discord
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord.ext import commands
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from user_schedule_model import UserSchedule, Base 
from table2ascii import table2ascii as t2a, PresetStyle
import psycopg2

# Load environment variables from .env file
load_dotenv()

#DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine
engine = create_engine("postgresql+psycopg2://u5hsl3t8vpl42s:pe6a13af81a75d26bf7ec16ed5614d296602e45c12f84e7dc965e840334951295@cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d66o2tq3s18vlt")

# Create a configured session class
Session = sessionmaker(bind=engine)

session = Session()

# Create tables based on the model definitions if they don't exist
Base.metadata.create_all(engine)

intents = discord.Intents.all()
bot = discord.Bot(intents = intents)

time_slots = [
    "08:20 - 09:30",
    "09:35 - 10:45",
    "-",
    "11:05 - 12:15",
    "-",
    "13:05 - 14:15",
    "14:20 - 15:30"
]

custom_block_times = {
    datetime(2024,8,30).date() : ["09:35 - 10:40", 
                                  "-",
                                "10:55 - 11:35", 
                                "11:40 - 12:20",
                                "-",
                                "13:20 - 14:00", 
                                "14:05 - 14:45", 
                                "14:50 - 15:30"],
    datetime(2024,9,3).date() : ["09:35 - 10:40", 
                                 "-",
                          "10:55 - 11:35", 
                          "11:40 - 12:20",
                          "-",
                        "13:20 - 14:00", 
                          "14:05 - 14:45", 
                          "14:50 - 15:30"],
    datetime(2024,9,5).date() : ["08:20 - 09:20", 
                          "09:25 - 10:25", 
                          "-",
                          "10:45 - 11:45",
                        "11:50 - 12:30", 
                        "-",
                          "13:25 - 14:25", 
                          "14:30 - 15:30"],
    datetime(2024,9,6).date() : ["08:20 - 09:20", 
                          "09:25 - 10:25", 
                          "-",
                          "10:45 - 12:10",
                        "-",
                          "13:05 - 14:25", 
                          "14:30 - 15:30"],

}


schedule_pattern = [
    ["1A","1B","1C(P)","1D","1E"],
    ["2A","2B","2C","2D","2E"],
    ["1A","1B","1E","1C(A)","1D"],
    ["2A","2B","2E","2C","2D"],
    ["1A","1B","1D","1E","1C(P)"],
    ["2A","2B","2D","2E","2C"],
    ["1A","1B","1C(A)","1D","1E"],
    ["2A","2B","2C","2D","2E"],
    ["1A","1B","1E","1C(P)","1D"],
    ["2A","2B","2E","2C","2D"],
    ["1A","1B","1D","1E","1C(A)"],
    ["2A","2B","2D","2E","2C"],
]


schedule_start = datetime(2024, 9, 4).date()


# Days off (no school)
days_off = {5, 6}  # Saturday and Sunday
custom_days_off = [datetime(2024, 9, 2).date()]  # Example: Thanksgiving Day


custom_block_orders = {
    datetime(2024,8,30).date(): ["2A","2B","2C","school_event", "2D","2E"],
    datetime(2024,9,3).date(): ["1C(PA)","2A","2B","2C","2D","2E"],
    datetime(2024,9,5).date():["2A","2B","2C","school_event", "2D","2E"],
    datetime(2024,9,6).date():["1A","1B","1C(PA)","1D","1E"],   
    datetime(2024, 12, 20).date(): ["2A", "1A", "2B", "1B", "2C", "1C(P)", "2D", "1D", "2E", "1E"],
      # Example: Last day before winter break
}

special_uniform_dates = {
    datetime(2024,9,3).date() : "Ceremonial",
    datetime(2024,9,6).date() : "Ceremonial",
    datetime(2024,9,27).date() : "Orange Shirt Day"
}


block_1a_courses = ["AP Chinese", "AP Statistics", "AP World History: Modern", "CLE", "Concert Band 10", "Entrepreneurship 12",  "Pre-Calculus 12", "Social Studies 10","Theatre Company 10", "Web Development 10"]
block_1b_courses = ["AP Calculus BC", "CLE", "EFP 10", "French 10 Enriched", "French 11", "Literary Studies 11", "Pre-AP English 11", "Science 10", "Social Studies 10", "Study Block"]
block_1c_courses = ["Advisory"]
block_1d_courses = ["AP CSP", "Art Studio 10", "EFP 10", "French 10", "Literary Studies 11", "Pre-AP English 11",  "Pre-Calculus 11","Pre-Calculus 12", "Spanish 10", "Study Block", "WP"]
block_1e_courses = ["CLE", "CLE(WP)", "Drafting 11", "EFP 10", "French 11 Enriched", "Mandarin 10 Accel", "Media Design 10", "PE 11", "Pre-Calculus 12", "Study Block" ]
block_2a_courses = ["Active Living 11",  "AP Economics", "Chemistry 11", "English Studies 12", "French 10", "PE 10", "PE Aquatics", "Pre-Calculus 11",  "Science 10", "Social Studies 10", "Study Block"]
block_2b_courses = ["AP Economics", "AP French", "AP Music Theory", "Chemistry 12", "Life Sciences 11", "PE 10 Brenko", "PE 10 Kimura", "Pre-Calculus 11", "Science 10", "Study Block"]
block_2c_courses = ["AP Human Geography","AP Statistics",  "Film /TV 11",  "French 10 Enriched", "French 11 Enriched", "French 12",  "Jazz Performence 11", "Math 10",  "Mandarin 10", "Mandarin 11 Accel", "Physics 11", "Pre-AP English 10", "Science 10H", "Social Studies 10", "Study Block"]
block_2d_courses = ["Art Studio 10", "CLE", "Film and TV 11", "Life Sciences 11", "Pre-AP English 10", "Pre-Calculus 12", "Study Block", "Web Development 10"]
block_2e_courses = ["20th Century World History", "BC FP 12",  "Chemistry 11", "French 10", "Math 10", "Physics 11", "Physics 12", "Pre-Calculus 11", "Study Block", "Woodwork 10"]

rooms_for_courses = {
    "1A" : {"AP Chinese" : "021W","AP World History: Modern" : "S 215" , "CLE" : "S 101", "Concert Band 10" : "J 009/Band Room" , "Entrepreneurship 12" : "S 114","Pre-Calculus 12" : "S 013" , "Social Studies 10" : "S 112" , "Theatre Company 10" : "J 013/Drama Room", "Web Development 10": "S 206/Holowka Room"},
    "1B" : {"AP Calculus BC" : "032E", "CLE" : "034E", "EFP 10" : "S 110" , "French 10 Enriched" : "023W" , "French 11" : "021W" , "Literary Studies 11" : "S 112", "Pre-AP English 11" : "S 114", "Science 10" : "S 200", "Social Studies 10" : "S 122", "Study Block" : "Location varies"},
    "1C" : {"Advisory" : "Different advisories coming soon"},
    "1D" : {"AP CSP" : "S 203/ Mr. Lu Room", "Art Studio 10" : "J 010/Art Room", "EFP 10" : "033E", "French 10" : "S 216", "Literary Studies 11" : "S 112", "Pre-AP English 11" : "S 114", "Pre-Calculus 11" : "032E" , "Pre-Calculus 12" : "031E", "Spanish 10" : "024E", "Study Block" : "Location varies","WP" : "S 013"},
    "1E" : {"CLE" : "034E" , "CLE(WP)" : "S 013" , "Drafting 11" : "J 010/Art Room", "EFP 10" : "032E" , "French 11 Enriched" : "S 013", "Mandarin 10 Accel" : "021W" , "Media Design 10" : "S 216", "PE 11" : "Location varies" , "Pre-Calculus 12" : "031E" , "Study Block" : "Location varies"},
    "2A" : {"Active Living 11" : "Location varies" ,"AP Economics" : "S 203/ Mr. Lu room" , "Chemistry 11" : "S 200" , "English Studies 12" : "S 108" , "French 10" : "S 013" , "PE 10" : "Location varies" , "PE Aquatics" : "A body of water" ,"Pre-Calculus 11" : "032E" , "Science 10" : "S 208" , "Social Studies 10" : "S 114" , "Study Block" : "Location varies"},
    "2B" : {"AP Economics" : "S 203/Mr. Lu room", "AP French" : "022W", "AP Music Theory" : "J 009/Band Room", "Chemistry 12" : "S 200", "Life Sciences 11" : "S 204", "PE 10 Brenko" : "Location varies", "PE 10 Kimura" : "Location varies", "Pre-Calculus 11" : "034E", "Science 10" : "S 208", "Study Block" : "Location varies"},
    "2C" : {"AP Human Geography" : "S 216","AP Statistics" : "032E",  "Film /TV 11" : "S 211",  "French 10 Enriched" : "023W", "French 11 Enriched" : "S 013", "French 12" : "022W",  "Jazz Performence 11" : "J 009/Band Room", "Math 10" : "033E",  "Mandarin 10" : "021W", "Mandarin 11 Accel" : "021W", "Physics 11" : "S 208", "Pre-AP English 10" : "S 112", "Science 10" : "S 200", "Social Studies 10" : "S 114", "Study Block" : "Location varies"},
    "2D" : {"Art Studio 10" : "J 010/Art Room", "CLE" : "032E", "Film and TV 11" : "S 221", "Life Sciences 11" : "S 200", "Pre-AP English 10" : "S 122", "Pre-Calculus 12" : "031E", "Study Block" : "Location varies", "Web Development 10" : "S 20/Holowka Room"},
    "2E" : {"20th Century World History" : "S 114", "BC FP 12" : "S 216",  "Chemistry 11" : "S 200", "French 10" : "S 013", "Math 10" : "031E", "Physics 11" : "S 208", "Physics 12" : "S 206/Holowka Room", "Pre-Calculus 11" : "034E", "Study Block" : "Location varies", "Woodwork 10" : "J 012/Woodshop"}
}


# Helper function to determine if a day is a day off
def is_day_off(date):
    return date.weekday() in days_off or date in custom_days_off

# Helper function to get today's schedule
def get_today_blocks():
    today = datetime.now().date()
    print(today)
    # Check for custom block order
    if today in custom_block_orders:
        return custom_block_orders[today]
    
    # Calculate the index in the repeating schedule pattern
    delta_days = (today - schedule_start).days
    day_index = delta_days % len(schedule_pattern)

    if is_day_off(today) or today in custom_days_off:
        return "No school"
    
    return schedule_pattern[day_index]

def get_today_block_times():
    today = datetime.now().date()
    # Check for custom block order
    if today in custom_block_times:
        print("entered")
        return custom_block_times[today]
    else:
        return time_slots


def get_tomorrow_blocks():
    # Check for custom block order
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.date()
    if tomorrow in custom_block_orders:
        return custom_block_orders[tomorrow]
    
    # Calculate the index in the repeating schedule pattern
    delta_days = (tomorrow - schedule_start).days
    day_index = delta_days % len(schedule_pattern)
    print("Day index: ", day_index)

    

    # Adjust index if today is a day off
    if is_day_off(tomorrow) or tomorrow in custom_days_off:
        return "No school"
    
    return schedule_pattern[day_index]

def get_tomorrow_block_times():
    tomorrow =  datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.date()
    # Check for custom block order
    if tomorrow in custom_block_times:
        return custom_block_times[tomorrow]
    else:
        return time_slots

def compare_schedule(discord_id1, discord_id2): 
    """
    Compare the course schedules of two users and return their schedules in two separate dictionaries.

    Args:
        discord_id1 (str): The Discord ID of the first user.
        discord_id2 (str): The Discord ID of the second user.

    Returns:
        tuple: A tuple containing two dictionaries. 
                The first dictionary has the course schedule for the first user,
                and the second dictionary has the course schedule for the second user.
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

def get_user_schedule(discord_id):
    user = session.query(UserSchedule).filter_by(discord_id=discord_id).first()
    if user:
        return {
            '1A': user.A1,
            '1B': user.B1,
            '1C': user.C1,
            '1D': user.D1,
            '1E': user.E1,
            '2A': user.A2,
            '2B': user.B2,
            '2C': user.C2,
            '2D': user.D2,
            '2E': user.E2
        }
    return {}

def save_user_schedule(discord_id, schedule_data):
    user = session.query(UserSchedule).filter_by(discord_id=discord_id).first()
    if not user:
        user = UserSchedule(discord_id=discord_id, username="Placeholder")  # Username can be updated later
        session.add(user)
    
    for block, course in schedule_data.items():
        setattr(user, block, course)
    
    session.commit()

def get_same_class(block, course_name):

    block = '"' + block[1] + block[0] + '"'
    print("Reversed block" + block)

    try:
        conn = psycopg2.connect(
            dbname= "d66o2tq3s18vlt",
            user="u5hsl3t8vpl42s",
            password="pe6a13af81a75d26bf7ec16ed5614d296602e45c12f84e7dc965e840334951295",
            host="cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
            port="5432"
        )

        cursor = conn.cursor()
        query = f"SELECT discord_id FROM user_schedules WHERE {block} = %s;"
        cursor.execute(query, (course_name,))
        results = cursor.fetchall()
        
        for row in results:
            print(row[0])
        
        return results

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        cursor.close()
        conn.close()

def getUserById(user_id):
    try:
        # Fetch the user by their ID
        user = bot.fetch_user(user_id)    
        return user
    except discord.NotFound:
        return "User Not Found"
    except discord.HTTPException as e:
        print(f'Failed to fetch user. Error: {str(e)}')
        return "Error"

testGroup = bot.create_group("testgroup", "math related commands")

schedule_input_cmds = bot.create_group("input", "input the courses you have for each block")

@schedule_input_cmds.command(name = "1a", description = "Change your 1a block")
async def change1a(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_1a_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 1C block with the new course name
    user_schedule.A1 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 1A")

@schedule_input_cmds.command(name = "1b", description = "Change your 1b block")
async def change1b(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_1b_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 1C block with the new course name
    user_schedule.B1 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 1B")

@schedule_input_cmds.command(name = "1c", description = "Change your 1c block")
async def change1c(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_1c_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 1C block with the new course name
    user_schedule.C1 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 1C")

@schedule_input_cmds.command(name = "1d", description = "Change your 1d block")
async def change1d(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_1d_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 1D block with the new course name
    user_schedule.D1 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 1D")

@schedule_input_cmds.command(name = "1e", description = "Change your 1e block")
async def change1e(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_1e_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 1E block with the new course name
    user_schedule.E1 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 1E")

@schedule_input_cmds.command(name = "2a", description = "Change your 2a block")
async def change2a(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_2a_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 2A block with the new course name
    user_schedule.A2 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 2A")

@schedule_input_cmds.command(name = "2b", description = "Change your 2b block")
async def change2b(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_2b_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 2B block with the new course name
    user_schedule.B2 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 2B")

@schedule_input_cmds.command(name = "2c", description = "Change your 2c block")
async def change2c(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_2c_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 2C block with the new course name
    user_schedule.C2 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 2C")

@schedule_input_cmds.command(name = "2d", description = "Change your 2d block")
async def change2d(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_2d_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 2D block with the new course name
    user_schedule.D2 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 2D")

@schedule_input_cmds.command(name = "2e", description = "Change your 2e block")
async def change2e(ctx: discord.ApplicationContext, course_name : discord.Option(str, choices = block_2e_courses)):
    user_id = str(ctx.author.id)

    # Retrieve the user’s current schedule from the database
    user_schedule = session.query(UserSchedule).filter_by(discord_id=user_id).first()

    # Check if the user exists in the database
    if not user_schedule:
        # If the user does not exist, create a new record
        user_schedule = UserSchedule(discord_id=user_id, username=str(ctx.author))
        session.add(user_schedule)

    # Update the 2E block with the new course name
    user_schedule.E2 = course_name
    session.commit()

    await ctx.respond(f"{course_name} saved to 2E")

@schedule_input_cmds.command(name = "setup", description = "Set up your schedule here!")
async def setup_schedule(ctx: discord.ApplicationContext, block1a : discord.Option(str, choices = block_1a_courses), block1b : discord.Option(str, choices = block_1b_courses), block1c :  discord.Option(str, choices = block_1c_courses), block1d :  discord.Option(str, choices = block_1d_courses), block1e :  discord.Option(str, choices = block_1e_courses), 
                         block2a : discord.Option(str, choices = block_2a_courses), block2b : discord.Option(str, choices = block_2b_courses), block2c : discord.Option(str, choices = block_2c_courses), block2d : discord.Option(str, choices = block_2d_courses), block2e : discord.Option(str, choices = block_2e_courses)):
   
    user_id = str(ctx.author.id)
    username = ctx.author.name

    schedule_data = {
        'Username' : username,
        'A1': block1a,
        'B1': block1b,
        'C1': block1c,
        'D1': block1d,
        'E1': block1e,
        'A2': block2a,
        'B2': block2b,
        'C2': block2c,
        'D2': block2d,
        'E2': block2e
    }
    print("About to print schedule data")
    print(schedule_data)
    save_user_schedule(user_id, schedule_data)
    await ctx.respond("Schedule saved!")





getCmds = bot.create_group("get", "Get information about schedules and courses")

async def get_courses_from_block(ctx: discord.AutocompleteContext):

    selectedBlock = ctx.options['block']
    if selectedBlock == '1A':
        return block_1a_courses
    elif selectedBlock == '1B':
        return block_1b_courses
    elif selectedBlock == '1C':
        return block_1c_courses
    elif selectedBlock == '1D':
        return block_1d_courses
    elif selectedBlock == '1E':
        return block_1e_courses
    elif selectedBlock == '2A':
        return block_2a_courses
    elif selectedBlock == '2B':
        return block_2b_courses
    elif selectedBlock == '2C':
        return block_2c_courses
    elif selectedBlock == '2D':
        return block_2d_courses
    elif selectedBlock == '2E':
        return block_2e_courses

@getCmds.command(name = "people_in_class", description = "Gives a list of people who are in the class specified")
async def people_in_my_class(ctx, block: discord.Option(str, choices = ["1A","1B","1C","1D","1E","2A","2B","2C","2D","2E"]), course_name : discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_courses_from_block))):

    # Call your function to get users in the same class
    output = get_same_class(block, course_name)  # Implement this function to query the database\

    if not output:
        await ctx.respond(f"No users found in {course_name} {block}.")
        return

    # Prepare the response message
    response = f"Those in {course_name} {block} are:\n"
    
    for theid in output:
        # print(type(theid[0]))
        # print(ctx.author.guild)
        # print(ctx.author.guild.get_member(int(theid[0])))
        try:
            name = ctx.author.guild.get_member(int(theid[0])).name
            # print(type(name))
            response += f"- {name}\n"
        except:
            response += f"- {theid[0]} (Not in this server) \n"

    # Send the response
    await ctx.respond(response)


@getCmds.command(name="today_schedule", description="Get your schedule for today.")
async def get_today_schedule(ctx):
    user_id = str(ctx.author.id)
    user_schedule = get_user_schedule(user_id)
    print("User Schedule: " )
    print(user_schedule)
    today_schedule = get_today_blocks()
    print("Today Schedule: ")
    print(today_schedule)
    today_block_times = get_today_block_times()
    if not user_schedule:
        await ctx.respond("You haven't set any courses yet.")
        return
    
        
    if today_schedule == "No school":
        await ctx.respond ("No school today.")
        return 
    
    courses = []
    i = 0
    for slot in today_schedule:
        if(today_block_times[i] == "-"):
            courses.append("-" * 20)
            i+=1
        if slot == '1C(PA)':
            courses.append(f"{today_block_times[i]}   {slot}: Advisory: School Event")
        elif slot == '1C(P)':
            courses.append(f"{today_block_times[i]}   {slot}: Advisory: PEAKS")
        elif slot == '1C(A)':
            courses.append(f"{today_block_times[i]}   {slot}: Advisory: Academics")
        elif slot == 'school_event':
            courses.append(f"{today_block_times[i]}   School Event")
        else:
            course_for_this_slot = user_schedule.get(slot, 'None')
            courses.append(f"{today_block_times[i]}   {slot}: {course_for_this_slot}"
                            f"{' ' * (24 - len(course_for_this_slot))}{rooms_for_courses.get(slot).get(course_for_this_slot)}")
        i+= 1
    
    await ctx.respond(f"**## Today's schedule for {ctx.author.name}:**```\n" +  "\n".join(courses) + "```")

@getCmds.command(name="tomorrow_schedule", description="Get your schedule for tomorrow.")
async def get_tomorrow_schedule(ctx):
    user_id = str(ctx.author.id)
    user_schedule = get_user_schedule(user_id)
    tomorrow_schedule = get_tomorrow_blocks()
    tomorrow_block_times = get_tomorrow_block_times()
    if not user_schedule:
        await ctx.respond("You haven't set any courses yet.")
        return
    
    if tomorrow_schedule == "No school":
        await ctx.respond ("No school tomorrow.")
        return 
    
    courses = []
    i = 0
    for slot in tomorrow_schedule:
        if(tomorrow_block_times[i] == "-"):
            courses.append("-" * 20)
            i+=1
        if slot == '1C(PA)':
            courses.append(f"{tomorrow_block_times[i]}   {slot}: Advisory: School Event")
        elif slot == '1C(P)':
            courses.append(f"{tomorrow_block_times[i]}   {slot}: Advisory: PEAKS")
        elif slot == '1C(A)':
            courses.append(f"{tomorrow_block_times[i]}   {slot}: Advisory: Academics")
        elif slot == 'school_event':
            courses.append(f"{tomorrow_block_times[i]}   School Event")
        else:
            course_for_this_slot = user_schedule.get(slot, 'None')
            courses.append(f"{tomorrow_block_times[i]}   {slot}: {course_for_this_slot}"
                            f"{' ' * (24 - len(course_for_this_slot))}{rooms_for_courses.get(slot).get(course_for_this_slot)}")
        i+= 1
    
    await ctx.respond(f"**## Tomorrow's schedule for {ctx.author.name}:**```\n" +  "\n".join(courses) + "```")

@getCmds.command(name = "compare_schedules", description = "Compare schedules for two people")
async def compare_schedules(ctx, person1: discord.Option(discord.Member,description = "Person 1"), person2: discord.Option(discord.Member,description = "Person 2")):
    schedule1, schedule2 = compare_schedule(person1.id, person2.id)
    # await ctx.send(f"User 1 Schedule: {schedule1}")
    # await ctx.send(f"User 2 Schedule: {schedule2}")
    
    output = t2a(
        header=["Block", f"{person1.name}", f"{person2.name}"],
        body=[["1A", schedule1.get('1A'), schedule2.get('1A')],["1B", schedule1.get('1B'), schedule2.get('1B')],["1C", schedule1.get('1C'), schedule2.get('1C')],
            ["1D", schedule1.get('1D'), schedule2.get('1D')],["1E", schedule1.get('1E'), schedule2.get('1E')],
            ["2A", schedule1.get('2A'), schedule2.get('2A')],["2B", schedule1.get('2B'), schedule2.get('2B')],["2C", schedule1.get('2C'), schedule2.get('2C')],
            ["2D", schedule1.get('2D'), schedule2.get('2D')],["2E", schedule1.get('2E'), schedule2.get('2E')]
        ],
        style=PresetStyle.thin
    )
    await ctx.respond(f"```\n{output}\n```")




@bot.slash_command(name = "ping_class", description = "Pings everyone in this server whose in the class specifed")
async def ping_class(ctx,block: discord.Option(str, choices = ["1A","1B","1C","1D","1E","2A","2B","2C","2D","2E"]), course_name : discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_courses_from_block))):
     # Call your function to get users in the same class
    output = get_same_class(block, course_name)  # Implement this function to query the database\

    if not output:
        await ctx.respond(f"No users found in {course_name} {block}.")
        return
    
    response = ""
    
    for theid in output:
        try:
            # print(type(name))
            response += f"<@{int(theid[0])}>"
        except:
            response += f"{theid[0]} (Not in this server) \n"

    await ctx.respond(response)


uniform_cmds = bot.create_group("uniform", "Get information about uniform")

@uniform_cmds.command(name = "today", description = "Get uniform for today")
async def get_uniform_for_today(ctx):

    today = datetime.today()

    weekno = today.weekday()
    today_date = today.date()

    if weekno >= 5 or today_date in custom_days_off:
        response = "No school today"
        await ctx.respond(response)
        return

 
    response = ""
    if today_date in special_uniform_dates:
        if(special_uniform_dates[today_date] == "Ceremonial"):
            response += "Ceremonial Uniform\n"
        else:
            response += special_uniform_dates[today_date] + "\n"
    else:
        response += "Regular Uniform\n"

    if weekno < 4:
        pass
    elif weekno == 4:
        response += "Hoodie allowed (Exceptions apply)" 


    user_id = str(ctx.author.id)
    user_schedule = get_user_schedule(user_id)
    today_schedule = get_today_blocks()

    if today_schedule == "No school":
        await ctx.respond ("No school today.")
        return 
    if not user_schedule:
        responses += "(Unable to predict if you have PE today. Please input schedule to gain access to this feature)"
        await ctx.respond(response)
    
    for slot in today_schedule:
        course_name = user_schedule.get(slot, 'Free period')
        if course_name == "PE 10" or course_name == "PE 11" or course_name == "PE 10 Brenko" or course_name == "PE 10 Kimura" or course_name == "PE Aquatics":
            print("Detected PE")
            response += "PE Strip may be needed as you have PE today. (Exceptions apply) \n"

    await ctx.respond(response)

@uniform_cmds.command(name = "tomorrow", description = "Get uniform for tomorrow")
async def get_uniform_for_tomorrow(ctx):

    today = datetime.today()
    
    tomorrow = today + timedelta(days=1)
    tomorrow_date = tomorrow.date()

    weekno = tomorrow.weekday()

    if weekno  >= 5 or tomorrow_date in custom_days_off:
        response = "No school today"
        await ctx.respond(response)
        return

 
    response = ""
    if tomorrow_date in special_uniform_dates:
        if(special_uniform_dates[tomorrow_date] == "Ceremonial"):
            response += "Ceremonial Uniform\n"
        else:
            response += special_uniform_dates[tomorrow_date] + "\n"
    else:
        response += "Regular Uniform\n"

    if weekno < 4:
        pass
    elif weekno == 4:
        response += "Hoodie allowed (Exceptions apply)\n" 

    user_id = str(ctx.author.id)
    user_schedule = get_user_schedule(user_id)
    tomorrow_schedule = get_tomorrow_blocks()

    if tomorrow_schedule == "No school":
        await ctx.respond ("No school tomorrow.")
        return 

    if not user_schedule:
        responses += "(Unable to predict if you have PE tomorrow. Please input schedule to gain access to this feature)"
        await ctx.respond(response)
    
    for slot in tomorrow_schedule:
        course_name = user_schedule.get(slot, 'Free period')
        if course_name == "PE 10" or course_name == "PE 11" or course_name == "PE 10 Brenko" or course_name == "PE 10 Kimura" or course_name == "PE Aquatics":
            print("Detected PE")
            response += "PE Strip may be needed as you have PE tomorrow. (Exceptions apply) \n"

    await ctx.respond(response)



@bot.slash_command(name="help", description="List all available commands.")
async def help_command(ctx):
    help_message = """
    # **Calendar Bot Help**

    ## **To get started:** Use `/input setup` and input your schedules.

    **Available Commands:**

    All commands have autocomplete inside their options. 

    `/input setup` - Set up your schedule with initial data.

    `/input [block]` - Update the course name for a specific block (e.g., `/input 1A`).

    `/get schedule_today` - Displays your schedule for today.

    `/get schedule_tomorrow` - Shows your schedule for tomorrow.

    `/get compare_schedules <user1> <user2>` - Compares the schedules of two users.

    `/get people_in_class <block> <class>` - Lists all people in a specified class block.

    `/ping_class <block> <class>` - Pings everyone in a specified class block.

    `/uniform today` - Check uniform needed today.

    `/uniform tomorrow` - Check uniform needed tomorrow.
    """
    await ctx.respond(help_message)


dev_cmds = bot.create_group("zdeveloper", "Developer commands")

@dev_cmds.command(name = "say", description = "Says something")
async def say(ctx, message : str):
    developer_id = 826334880455589918
    if ctx.author.id == developer_id:
        await ctx.respond(message)
    else:
        await ctx.respond('This command is for developer only')



print("runs?")

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run('MTI3NjAxNDYwNzAyNjIyNTE4Mw.GlNuGp.Z1I4EHYaD3K8D9sJ3qratBCbs3onkzrAQuRPFY') # run the bot with the token

print("should connect")