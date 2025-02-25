from sqlmodel import SQLModel, Session, create_engine
from app.models import *
from app.database.db_models import *

DATABASE_FILE_NAME = "Trip Planner.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def close_db_connections():
    engine.dispose()
