from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from models import UserSchedule, Base  # Adjust the import based on your setup
import os
from dotenv import load_dotenv

# Database setup
load_dotenv()

DB_URL = os.getenv("CORRECT_DATABASE_URL")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
session = Session()

# Update the grade based on discord_id
try:
    # Update for discord_id = 708147583864012860
    session.query(UserSchedule).filter(UserSchedule.discord_id == '708147583864012860').update({UserSchedule.grade: 11})
    
    # Update for all other discord_ids
    session.query(UserSchedule).filter(UserSchedule.discord_id != '708147583864012860').update({UserSchedule.grade: 10})

    # Commit the changes
    session.commit()
    print("Grades updated successfully.")
except Exception as e:
    session.rollback()
    print(f"An error occurred: {e}")
finally:
    session.close()
