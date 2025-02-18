from sqlmodel import SQLModel, Session, create_engine
from app.models import *
from app.database.db_models import *

DATABASE_FILE_NAME = "Trip Planner.db"
TEST_DATABASE_FILE_NAME = "Test.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_FILE_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
test_engine = create_engine(TEST_DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def create_test_db_and_tables():
    SQLModel.metadata.create_all(test_engine)

def drop_test_db_and_tables():
    SQLModel.metadata.drop_all(test_engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_test_session():
    with Session(test_engine) as session:
        yield session

def close_db_connections():
    engine.dispose()
