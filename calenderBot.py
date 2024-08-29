import discord
import os # default module
from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord import Option
from discord.ext import commands
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from user_schedule_model import UserSchedule, Base 
from table2ascii import table2ascii as t2a, PresetStyle


DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


Base.metadata.create_all(engine)

intents=discord.Intents.all()
intents.members = True
client=discord.Bot(intents=intents)

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


schedule_start = datetime(2024, 9, 3)


# Days off (no school)
days_off = {5, 6}  # Saturday and Sunday
custom_days_off = [datetime(2024, 10, 14)]  # Example: Thanksgiving Day


custom_block_orders = {
    datetime(2024, 12, 20): ["2A", "1A", "2B", "1B", "2C", "1C(P)", "2D", "1D", "2E", "1E"]  # Example: Last day before winter break
}


# Dictionary to store multiple users' schedules
#user_schedules = {}

# Helper function to determine if a day is a day off
def is_day_off(date):
    return date.weekday() in days_off or date in custom_days_off

# Helper function to get today's schedule
def get_today_schedule(today):
    # Check for custom block order
    if today in custom_block_orders:
        return custom_block_orders[today]
    
    # Calculate the index in the repeating schedule pattern
    delta_days = (today - schedule_start).days
    day_index = delta_days % len(schedule_pattern)
    print("Day index: ", day_index)

    # Adjust index if today is a day off
    while is_day_off(today):
        today += timedelta(days=1)
        delta_days += 1
        day_index = delta_days % len(schedule_pattern)
    
    return schedule_pattern[day_index]

def get_tomorrow_schedule():
    # Check for custom block order
    tomorrow = datetime.now() + timedelta(days=1)
    if tomorrow in custom_block_orders:
        return custom_block_orders[tomorrow]
    
    # Calculate the index in the repeating schedule pattern
    delta_days = (tomorrow - schedule_start).days
    day_index = delta_days % len(schedule_pattern)
    print("Day index: ", day_index)

    

    # Adjust index if today is a day off
    while is_day_off(tomorrow):
        tomorrow += timedelta(days=1)
        delta_days += 1
        day_index = delta_days % len(schedule_pattern)
    
    return schedule_pattern[day_index]





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

  

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents = intents)


testGroup = bot.create_group("testgroup", "math related commands")

schedule_input_cmds = bot.create_group("input", "input the courses you have for each block")

@schedule_input_cmds.command(name = "1a", description = "Change your 1a block")
async def change1a(ctx: discord.ApplicationContext, course_name : str):
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
async def change1b(ctx: discord.ApplicationContext, course_name : str):
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
async def change1c(ctx: discord.ApplicationContext, course_name : str):
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


@schedule_input_cmds.command(name = "setup", description = "Set up your schedule here!")
async def setup_schedule(ctx: discord.ApplicationContext, block1a : str, block1b : str, block1c : str, block1d : str, block1e : str, block2a : str, block2b : str, block2c : str, block2d : str, block2e : str):
   
    user_id = str(ctx.author.id)
    username = ctx.message.author.name
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



@bot.slash_command(name="get_schedule", description="Get your schedule for today.")
async def display_schedule(ctx):
    user_id = str(ctx.author.id)
    user_schedule = get_user_schedule(user_id)
    today_schedule = get_today_schedule(today=datetime.now())
    
    if not user_schedule:
        await ctx.respond("You haven't set any courses yet.")
        return
    
    courses = []
    for slot in today_schedule:
        if slot == '1C(P)':
            courses.append(f"{slot}: Advisory: PEAKS")
        elif slot == '1C(A)':
            courses.append(f"{slot}: Advisory: Academics")
        else:
            courses.append(f"{slot}: {user_schedule.get(slot, 'Free period')}")
    
    await ctx.respond(f"Today's schedule:\n" + "\n".join(courses))

@bot.slash_command(name = "compare_schedules", description = "Compare schedules for two people")
async def compare_schedules(ctx, person1: Option(discord.Member,description = "Person 1"), person2: Option(discord.Member,description = "Person 2")):
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
        style=PresetStyle.thin_compact
    )

    await ctx.send(f"```\n{output}\n```")


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

bot.run(os.getenv('TOKEN')) # run the bot with the token