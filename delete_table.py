import os
from sqlalchemy import create_engine, MetaData, Table

# Connect to the Heroku PostgreSQL database
DATABASE_URL = os.environ['DATABASE_URL']
engine = create_engine(DATABASE_URL)

# Metadata object to access database schema information
metadata = MetaData()

# Reflect the table to be dropped
table_name = 'user_schedules'  # Replace with your table name
table_to_drop = Table(table_name, metadata, autoload_with=engine)

# Drop the table
table_to_drop.drop(engine)
print(f"Table '{table_name}' has been dropped.")
