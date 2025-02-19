from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from app.database.db_models import User
from app.main import app
from app.database.db_main import get_session
from app.util.auth import get_current_user, get_hashed_password, verify_password

client = TestClient(app)

@pytest.fixture(scope="session")
def test_engine():
    #Creating Engine
    TEST_DATABASE_FILE_NAME = "Test.db"
    TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_FILE_NAME}"

    test_engine = create_engine(TEST_DATABASE_URL, echo=False)
    
    SQLModel.metadata.create_all(test_engine)

    yield test_engine

    # Drop tables only once
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture
def test_session(test_engine):
    #Creating Session
    with Session(test_engine) as session:
        yield session

@pytest.fixture
def client_unauthorized(test_session):  # Inject the test session
    def override_get_db():
        yield test_session

    app.dependency_overrides[get_session] = override_get_db  # Override the dependency
    with TestClient(app) as c:
        yield c

def test_register_user(client_unauthorized: TestClient, test_session: Session):
    user1 = {
      "name": "kartik",
      "email": "kartiksingh@gmail.com",
      "password": "Shiva10#bhole",
      "date_of_birth": "2001-04-06"
    }
    result_user = {
      "id": 1,
      "name": "kartik",
      "email": "kartiksingh@gmail.com",
      "date_of_birth": "2001-04-06"
    }

    response = client_unauthorized.post("/user", json=user1)  # Send the POST request
    assert response.status_code == 201  # Check the status code
    assert response.json() == result_user  # Check the response body

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.id == 1
    assert result.name == "kartik"
    assert result.email == "kartiksingh@gmail.com"
    assert result.date_of_birth == datetime(2001, 4, 6, 0, 0).date()

def test_register_users(client_unauthorized: TestClient, test_session: Session):
    user2 = {
      "name": "admin",
      "email": "adminUser@gmail.com",
      "password": "11#Admin#11",
      "date_of_birth": "1997-07-07"
    }
    user3 = {
      "name": "suman",
      "email": "sumansingh137@gmail.com",
      "password": "Bam10#bhole",
      "date_of_birth": "1975-06-11"
    }
    user4 = {
      "name": "arvind",
      "email": "arvindsingh45057@gmail.com",
      "password": "10#Bhole#10",
      "date_of_birth": "1976-07-10"
    }
    result_user2 = {
      "id": 2,
      "name": "admin",
      "email": "adminUser@gmail.com",
      "date_of_birth": "1997-07-07"
    }
    result_user3 = {
      "id": 3,
      "name": "suman",
      "email": "sumansingh137@gmail.com",
      "date_of_birth": "1975-06-11"
    }
    result_user4 = {
      "id": 4,
      "name": "arvind",
      "email": "arvindsingh45057@gmail.com",
      "date_of_birth": "1976-07-10"
    }

    response = client_unauthorized.post("/user", json=user2)
    assert response.status_code == 201
    assert response.json() == result_user2

    response = client_unauthorized.post("/user", json=user3)
    assert response.status_code == 201
    assert response.json() == result_user3

    response = client_unauthorized.post("/user", json=user4)
    assert response.status_code == 201
    assert response.json() == result_user4

def test_get_current_user_without_auth(client_unauthorized: TestClient, test_session: Session):
    response = client_unauthorized.get("/user/me")  # Send the get request
    assert response.status_code == 401  # Check the status code
    assert response.json() == {'detail': 'Not authenticated'} # Check the response body

@pytest.fixture
def client(test_session: Session):
    def override_get_current_user():  # Override for tests
        statement = select(User).where(User.id == 1)
        result = test_session.exec(statement).first()
        return result

    def override_get_db():
        yield test_session

    app.dependency_overrides[get_current_user] = override_get_current_user

    app.dependency_overrides[get_session] = override_get_db  # Override the dependency
    with TestClient(app) as c:
        yield c

@pytest.fixture
def client_admin(test_session: Session):
    def override_get_current_user():  # Override for tests
        statement = select(User).where(User.id == 2)
        result = test_session.exec(statement).first()
        return result

    def override_get_db():
        yield test_session

    app.dependency_overrides[get_current_user] = override_get_current_user

    app.dependency_overrides[get_session] = override_get_db  # Override the dependency
    with TestClient(app) as c:
        yield c

def test_get_current_user(client: TestClient, test_session: Session):
    result = {
      "id": 1,
      "name": "kartik",
      "email": "kartiksingh@gmail.com",
      "date_of_birth": "2001-04-06"
    }

    response = client.get("/user/me")  # Send the get request
    assert response.status_code == 200  # Check the status code
    assert response.json() == result # Check the response body

def test_get_all_users_unauthorized(client: TestClient, test_session: Session):
    response = client.get("/user/all/?offset=0&limit=10")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Insufficient privileges'}

def test_get_all_users_with_admin_authorization(client_admin: TestClient, test_session: Session):
    response = client_admin.get("/user/all/?offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 2, 'name': 'admin', 'email': 'adminUser@gmail.com', 'date_of_birth': '1997-07-07'}, {'id': 4, 'name': 'arvind', 'email': 'arvindsingh45057@gmail.com', 'date_of_birth': '1976-07-10'}, {'id': 1, 'name': 'kartik', 'email': 'kartiksingh@gmail.com', 'date_of_birth': '2001-04-06'}, {'id': 3, 'name': 'suman', 'email': 'sumansingh137@gmail.com', 'date_of_birth': '1975-06-11'}]

def test_get_all_users_with_admin_authorization_offset_limit(client_admin: TestClient, test_session: Session):
    response = client_admin.get("/user/all/?offset=1&limit=2")
    assert response.status_code == 200
    assert response.json() == [{'id': 4, 'name': 'arvind', 'email': 'arvindsingh45057@gmail.com', 'date_of_birth': '1976-07-10'}, {'id': 1, 'name': 'kartik', 'email': 'kartiksingh@gmail.com', 'date_of_birth': '2001-04-06'}]

def test_get_user_by_id_with_admin_authorization(client_admin: TestClient, test_session: Session):
    response = client_admin.get("/user/1")
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'name': 'kartik', 'email': 'kartiksingh@gmail.com', 'date_of_birth': '2001-04-06'}

def test_get_user_by_id_with_admin_authorization_non_existing_user(client_admin: TestClient, test_session: Session):
    response = client_admin.get("/user/50")
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

def test_update_user_name(client: TestClient, test_session: Session):
    response = client.put("/user/me/name/?name=kartik singh")
    assert response.status_code == 200
    assert response.json() == {'message': 'name updated successfully'}

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.name == "kartik singh"

def test_update_user_date_of_birth(client: TestClient, test_session: Session):
    response = client.put("/user/me/dob/?date_of_birth=2001-04-07")
    assert response.status_code == 200
    assert response.json() == {'message': 'date of birth updated successfully'}

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.date_of_birth == datetime(2001, 4, 7, 0, 0).date()
