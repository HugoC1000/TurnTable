import discord
import os # default module
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
user_schedules = {}

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



intents=discord.Intents.all()
client=discord.Bot(intents=intents)

async def get_animal_types(ctx: discord.AutocompleteContext):
  """
  Here we will check if 'ctx.options['animal_type']' is a marine or land animal and return respective option choices
  """
  animal_type = ctx.options['animal_type']
  if animal_type == 'Marine':
    return ['Whale', 'Shark', 'Fish', 'Octopus', 'Turtle']
  else: # is land animal
    return ['Snake', 'Wolf', 'Lizard', 'Lion', 'Bird']
  

load_dotenv() # load all the variables from the env file
bot = discord.Bot(intents = intents)


testGroup = bot.create_group("testgroup", "math related commands")

schedule_input_cmds = bot.create_group("input", "input the courses you have for each block")

@schedule_input_cmds.command(name = "1a", description = "Change your 1c block")
async def test_text(ctx: discord.ApplicationContext, course_name : str):
   
   await ctx.respond(f"{course_name} saved to 1a")

@schedule_input_cmds.command(name = "1b", description = "Change your 1c block")
async def another_test(ctx: discord.ApplicationContext, course_name : str):
   await ctx.respond(f"{course_name} saved to 1b")

@schedule_input_cmds.command(name = "1c", description = "Change your 1c block")
async def another_test(ctx: discord.ApplicationContext, course_name : str):
   await ctx.respond(f"{course_name} saved to 1c")


@schedule_input_cmds.command(name = "setup", description = "Set up your schedule here!")
async def another_test(ctx: discord.ApplicationContext, block1a : str, block1b : str, block1c : str, block1d : str, block1e : str, block2a : str, block2b : str, block2c : str, block2d : str, block2e : str):
   
    user_id = str(ctx.author.id)
    if user_id not in user_schedules:
        user_schedules[user_id] = {}
    
    user_schedules[user_id]["1A"] = block1a
    user_schedules[user_id]["1B"] = block1b
    user_schedules[user_id]["1C"] = block1c
    user_schedules[user_id]["1D"] = block1d
    user_schedules[user_id]["1E"] = block1e
    user_schedules[user_id]["2A"] = block2a
    user_schedules[user_id]["2B"] = block2b
    user_schedules[user_id]["2C"] = block2c
    user_schedules[user_id]["2D"] = block2d
    user_schedules[user_id]["2E"] = block2e
    
    
    print(user_schedules[user_id])
    await ctx.respond(f"Saved")


# Function to print today's schedule with course names for a specific user
def print_today_schedule(username, today):
    if username not in user_schedules:
        print(f"No schedule found for {username}.")
        return
    
    if is_day_off(today):
        print(f"{today.strftime('%Y-%m-%d')}: No school today for {username}.")
    else:
        schedule = get_today_schedule(today)
        print(f"{today.strftime('%Y-%m-%d')}: {username}'s schedule is:")
        for block in schedule:
            course = user_schedules[username].get(block, "Free period")
            print(f"{block}: {course}")



@bot.slash_command(name="get_schedule", description="Get your schedule for today.")
async def get_schedule(ctx):
    user_id = str(ctx.author.id) 
    today_schedule = get_today_schedule(today = datetime.now()) #datetime(2024,9,4)
    
    if user_id not in user_schedules:
        await ctx.respond("You haven't set any courses yet.")
        return
    
    print("Today Schedule")
    print(today_schedule)
    courses = []    
    for slot in today_schedule:
        if slot == '1C(P)':
            courses.append(f"{slot}: Advisory: PEAKS")
        elif slot == '1C(A)':
            courses.append(f"{slot}: Advisory: Academics")
        else:
            courses.append(f"{slot}: {user_schedules[user_id].get(slot,'Free period')}")
    await ctx.respond(f"Today's schedule:\n" + "\n".join(courses))


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# @bot.slash_command(name="hello", description="Say hello to the bot")
# async def hello(ctx: discord.ApplicationContext):
#     await ctx.respond("Hey!")

# @bot.slash_command(name="animal")
# async def animal_command(ctx: discord.ApplicationContext, animal_type: discord.Option(str, choices=['Marine', 'Land']), animal: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_animal_types))
# ):
#   await ctx.respond(f'You picked an animal type of `{animal_type}` that led you to pick `{animal}`!')

# @testGroup.command(name = "sayhi")
# async def test_text(ctx: discord.ApplicationContext):
#    await ctx.respond("hi")

# @testGroup.command(name = "sayhello")
# async def another_test(ctx: discord.ApplicationContext):
#    await ctx.respond("hello")

bot.run(os.getenv('TOKEN')) # run the bot with the token