from sqlmodel import SQLModel,create_engine
import os

connection_str=os.getenv('DB_URL')
print(connection_str)
engine=create_engine(connection_str)

def create_tables():
    SQLModel.metadata.create_all(engine)
