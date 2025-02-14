from sqlmodel import SQLModel, create_engine
from app.models import *
from app.database.db_models import *

sqlite_file_name = "Trip Planner.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def close_db_connections():
    engine.dispose()

if __name__ == "__main__":
    create_db_and_tables() 
