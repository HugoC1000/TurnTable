import discord
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord.ext import commands
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import UserSchedule, Base 
from table2ascii import table2ascii as t2a, PresetStyle
import psycopg2
import numpy as np

from config import CUSTOM_BLOCK_TIMES, CUSTOM_BLOCK_ORDERS, SPECIAL_UNIFORM_DATES, SCHEDULE_PATTERN, DAYS_OFF, CUSTOM_DAYS_OFF, TIME_SLOTS, SCHEDULE_START, ROOMS_FOR_COURSES
from config import BLOCK_1A_COURSES,BLOCK_1B_COURSES,BLOCK_1C_COURSES,BLOCK_1D_COURSES, BLOCK_1E_COURSES, BLOCK_2A_COURSES, BLOCK_2B_COURSES, BLOCK_2C_COURSES, BLOCK_2D_COURSES, BLOCK_2E_COURSES
from database import get_or_create_user_schedule, save_user_schedule, get_same_class, compare_schedule
from schedule import is_day_off, get_blocks_for_date, get_block_times_for_date

# Load environment variables from .env file
load_dotenv()

#DATABASE_URL = os.getenv("DATABASE_URL")

# # Create the engine
# engine = create_engine("postgresql+psycopg2://u5hsl3t8vpl42s:pe6a13af81a75d26bf7ec16ed5614d296602e45c12f84e7dc965e840334951295@cd1goc44htrmfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d66o2tq3s18vlt")

# # Create a configured session class
# Session = sessionmaker(bind=engine)

# session = Session()

# # Create tables based on the model definitions if they don't exist
# Base.metadata.create_all(engine)

intents = discord.Intents.all()
bot = discord.Bot(intents = intents)



async def get_courses_from_block(ctx: discord.AutocompleteContext):
    selectedBlock = ctx.options['block']
    if selectedBlock == '1A':
        return BLOCK_1A_COURSES
    elif selectedBlock == '1B':
        return BLOCK_1B_COURSES
    elif selectedBlock == '1C':
        return BLOCK_1C_COURSES
    elif selectedBlock == '1D':
        return BLOCK_1D_COURSES
    elif selectedBlock == '1E':
        return BLOCK_1E_COURSES
    elif selectedBlock == '2A':
        return BLOCK_2A_COURSES
    elif selectedBlock == '2B':
        return BLOCK_2B_COURSES
    elif selectedBlock == '2C':
        return BLOCK_2C_COURSES
    elif selectedBlock == '2D':
        return BLOCK_2D_COURSES
    elif selectedBlock == '2E':
        return BLOCK_2E_COURSES



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


schedule_input_cmds = bot.create_group("input", "input the courses you have for each block")

@schedule_input_cmds.command(name="change", description="Change one of your blocks")
async def change(ctx: discord.ApplicationContext, block: discord.Option(str, choices=["1A", "1B", "1C", "1D", "1E", "2A", "2B", "2C", "2D", "2E"]), course_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_courses_from_block))):
    user_id = str(ctx.author.id)

    # Fetch or create the user's schedule
    user_schedule = get_or_create_user_schedule(user_id, username=str(ctx.author))

    # Map the block to the correct attribute (e.g., "1A" -> "A1")
    block_attr = block[1] + block[0]

    # Update the corresponding block with the new course name
    setattr(user_schedule, block_attr, course_name)
    session.commit()

    await ctx.respond(f"{course_name} saved to {block}")

@schedule_input_cmds.command(name = "setup", description = "Set up your schedule here!")
async def setup_schedule(ctx: discord.ApplicationContext, block1a : discord.Option(str, choices = BLOCK_1A_COURSES), block1b : discord.Option(str, choices = BLOCK_1B_COURSES), block1c :  discord.Option(str, choices = BLOCK_1C_COURSES), block1d :  discord.Option(str, choices = BLOCK_1D_COURSES), block1e :  discord.Option(str, choices = BLOCK_1E_COURSES), 
                         block2a : discord.Option(str, choices = BLOCK_2A_COURSES), block2b : discord.Option(str, choices = BLOCK_2B_COURSES), block2c : discord.Option(str, choices = BLOCK_2C_COURSES), block2d : discord.Option(str, choices = BLOCK_2D_COURSES), block2e : discord.Option(str, choices = BLOCK_2E_COURSES)):
   
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

@getCmds.command(name = "people_in_class", description = "Gives a list of people who are in the class specified")
async def people_in_my_class(ctx, block: discord.Option(str, choices = ["1A","1B","1C","1D","1E","2A","2B","2C","2D","2E"]), course_name : discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_courses_from_block))):

    # Call your function to get users in the same class
    output = get_same_class(block, course_name) 

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
    
    # Fetch or create the user's schedule
    user_schedule = get_or_create_user_schedule(user_id, username=str(ctx.author))
    
    today_schedule = get_blocks_for_date(datetime.now().date())
    today_block_times = get_block_times_for_date(datetime.now().date())

    if not any([user_schedule.A1, user_schedule.B1, user_schedule.C1, user_schedule.D1, user_schedule.E1,
                user_schedule.A2, user_schedule.B2, user_schedule.C2, user_schedule.D2, user_schedule.E2]):
        await ctx.respond("You haven't set any courses yet.")
        return
    
    if today_schedule == "No school":
        await ctx.respond("No school today.")
        return 

    courses = []
    i = 0
    
    print(today_schedule)
    
    max_whitespace_after_courses = 0
    
    course_for_this_slot = ""
    
    for slot in today_schedule:
        if slot in ['1C(PA)', '1C(P)', '1C(A)']:
            course_for_this_slot = "School Event" if slot == '1C(PA)' else "PEAKS" if slot == '1C(P)' else "Academics"

        elif slot == 'school_event':
            course_for_this_slot = "School Event"
        else:
            course_for_this_slot = getattr(user_schedule, slot[1] + slot[0], 'None')
            
        max_whitespace_after_courses =  max(max_whitespace_after_courses,len(course_for_this_slot))

    max_whitespace_after_courses += 3
    
    for slot in today_schedule:
        if today_block_times[i] == "-":
            courses.append("-" * 20)
            i += 1

        if slot in ['1C(PA)', '1C(P)', '1C(A)']:
            print("Entered advisory")
            course_for_this_slot = getattr(user_schedule, "C1", 'None')
            room = ROOMS_FOR_COURSES.get("1C", {}).get(course_for_this_slot, 'Unknown Room')
            advisory_type = "School Event" if slot == '1C(PA)' else "PEAKS" if slot == '1C(P)' else "Academics"
            courses.append(f"{today_block_times[i]}  {advisory_type}"
                           f"{' ' * (max_whitespace_after_courses - len(advisory_type))}{room}")
        elif slot == 'school_event':
            courses.append(f"{today_block_times[i]}  School Event")
        else:
            course_for_this_slot = getattr(user_schedule, slot[1] + slot[0], 'None')
            room = ROOMS_FOR_COURSES.get(slot, {}).get(course_for_this_slot, 'Unknown Room')
            
            courses.append(f"{today_block_times[i]}  {course_for_this_slot}"
                           f"{' ' * (max_whitespace_after_courses - len(course_for_this_slot))}{room}")
        i += 1

    await ctx.respond(f"**## Today's schedule for {ctx.author.name}:**```\n" + "\n".join(courses) + "```")
    return

@getCmds.command(name="tomorrow_schedule", description="Get your schedule for tomorrow.")
async def get_tomorrow_schedule(ctx):
    user_id = str(ctx.author.id)
    
    # Fetch or create the user's schedule
    user_schedule = get_or_create_user_schedule(user_id, username=str(ctx.author))
    
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.date()
    
    tomorrow_schedule = get_blocks_for_date(tomorrow)
    tomorrow_block_times = get_block_times_for_date(tomorrow)

    if not any([user_schedule.A1, user_schedule.B1, user_schedule.C1, user_schedule.D1, user_schedule.E1,
                user_schedule.A2, user_schedule.B2, user_schedule.C2, user_schedule.D2, user_schedule.E2]):
        await ctx.respond("You haven't set any courses yet.")
        return
    
    if tomorrow_schedule == "No school":
        await ctx.respond("No school tomorrow.")
        return 

    courses = []
    
    course_for_first_for_loop_slot = ""
    
    max_whitespace_after_courses = 0
    
    for slot in tomorrow_schedule:
        print("Slot " + slot)
        if slot in ['1C(PA)', '1C(P)', '1C(A)']:
            course_for_first_for_loop_slot = "School Event" if slot == '1C(PA)' else "PEAKS" if slot == '1C(P)' else "Academics"

        elif slot == 'school_event':
            course_for_first_for_loop_slot = "School Event"
        else:
            course_for_first_for_loop_slot = getattr(user_schedule, slot[1] + slot[0], 'None')
            
        max_whitespace_after_courses = max(max_whitespace_after_courses,len(course_for_first_for_loop_slot))

    max_whitespace_after_courses += 3
        
    i = 0
    
    
    
    for slot in tomorrow_schedule:
        if tomorrow_block_times[i] == "-":
            courses.append("-" * 20)
            i += 1

        if slot in ['1C(PA)', '1C(P)', '1C(A)']:
            course_for_this_slot = getattr(user_schedule, "C1", 'None')
            room = ROOMS_FOR_COURSES.get("1C", {}).get(course_for_this_slot, 'Unknown Room')
            
            advisory_type = "School Event" if slot == '1C(PA)' else "PEAKS" if slot == '1C(P)' else "Academics"
            courses.append(f"{tomorrow_block_times[i]}  {advisory_type}"
                           f"{' ' * (max_whitespace_after_courses - len(advisory_type))}{room}")
        elif slot == 'school_event':
            courses.append(f"{tomorrow_block_times[i]}  School Event")
        else:
            course_for_this_slot = getattr(user_schedule, slot[1] + slot[0], 'None')
            
            room = ROOMS_FOR_COURSES.get(slot, {}).get(course_for_this_slot, 'Unknown Room')
            whitespace = ' ' * (max_whitespace_after_courses - len(course_for_this_slot))
            courses.append(f"{tomorrow_block_times[i]}  {course_for_this_slot}"
                           f"{whitespace}{room}")
        i += 1

    await ctx.respond(f"**## Tomorrow's schedule for {ctx.author.name}:**```\n" + "\n".join(courses) + "```")
    return


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

@uniform_cmds.command(name="today", description="Get uniform for today")
async def get_uniform_for_today(ctx: discord.ApplicationContext):
    today = datetime.today()
    weekno = today.weekday()
    today_date = today.date()

    # Initialize response
    response = ""

    # Check for no school days
    if weekno >= 5 or today_date in CUSTOM_DAYS_OFF:
        response = "No school today"
        await ctx.respond(response)
        return

    # Determine uniform based on special dates
    if today_date in SPECIAL_UNIFORM_DATES:
        special_uniform = SPECIAL_UNIFORM_DATES[today_date]
        response += f"{special_uniform}\n" if special_uniform != "Ceremonial" else "Ceremonial Uniform\n"
    else:
        response += "Regular Uniform\n"

    # Add hoodie allowance based on day of the week
    if weekno == 4:
        response += "Hoodie allowed (Exceptions apply)\n"

    # Get user schedule
    user_id = str(ctx.author.id)
    user_schedule = get_or_create_user_schedule(user_id)

    # Check for no school scenario
    today_schedule = get_blocks_for_date(datetime.now().date())
    if today_schedule == "No school":
        await ctx.respond("No school today.")
        return

    # Handle cases where the user schedule is missing
    if not user_schedule:
        response += "(Unable to predict if you have PE today. Please input schedule to gain access to this feature)\n"
        await ctx.respond(response)
        return

    # Check for PE classes in the user's schedule
    pe_courses = {"PE 10", "PE 11", "PE 10 Brenko", "PE 10 Kimura", "PE Aquatics"}
    for slot in today_schedule:
        course_name = getattr(user_schedule, slot[1] + slot[0], 'Free period')
        if course_name in pe_courses:
            response += "PE Strip may be needed as you have PE today. (Exceptions apply)\n"
            break  # PE detected, no need to check further slots

    await ctx.respond(response)


@uniform_cmds.command(name="tomorrow", description="Get uniform for tomorrow")
async def get_uniform_for_tomorrow(ctx: discord.ApplicationContext):
    # Calculate tomorrow's date and weekday
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    tomorrow_date = tomorrow.date()
    weekno = tomorrow.weekday()

    # Initialize response
    response = ""

    # Check for no school days
    if weekno >= 5 or tomorrow_date in CUSTOM_DAYS_OFF:
        response = "No school tomorrow."
        await ctx.respond(response)
        return

    # Determine uniform based on special dates
    if tomorrow_date in SPECIAL_UNIFORM_DATES:
        special_uniform = SPECIAL_UNIFORM_DATES[tomorrow_date]
        response += f"{special_uniform}\n" if special_uniform != "Ceremonial" else "Ceremonial Uniform\n"
    else:
        response += "Regular Uniform\n"

    # Add hoodie allowance based on day of the week
    if weekno == 4:
        response += "Hoodie allowed (Exceptions apply)\n"

    # Get user schedule
    user_id = str(ctx.author.id)
    user_schedule = get_or_create_user_schedule(user_id)

    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.date()
    
    # Check for no school scenario
    tomorrow_schedule = get_blocks_for_date(tomorrow)
    if tomorrow_schedule == "No school":
        await ctx.respond("No school tomorrow.")
        return

    # Handle cases where the user schedule is missing
    if not user_schedule:
        response += "(Unable to predict if you have PE tomorrow. Please input schedule to gain access to this feature)\n"
        await ctx.respond(response)
        return

    # Check for PE classes in the user's schedule
    pe_courses = {"PE 10", "PE 11", "PE 10 Brenko", "PE 10 Kimura", "PE Aquatics"}
    for slot in tomorrow_schedule:
        course_name = getattr(user_schedule, slot[1] + slot[0], 'Free period')
        if course_name in pe_courses:
            response += "PE Strip may be needed as you have PE tomorrow. (Exceptions apply)\n"
            break  # PE detected, no need to check further slots

    await ctx.respond(response)




@bot.slash_command(name="help", description="List all available commands.")
async def help_command(ctx):
    help_message = """
    # **Calendar Bot Help**

    ## **To get started:** Use `/input setup` and input your schedules.

    **Available Commands:**

    All commands have autocomplete inside their options. 

    `/input setup` - Set up your schedule with initial data.

    `/input change [block]` - Update the course name for a specific block (e.g., `/input change 1A`).

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

