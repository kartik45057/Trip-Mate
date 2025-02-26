from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from app.database.db_models import Expense, Payment, Trip, User, UserExpenseLink
from app.enums import PaymentMode
from app.main import app
from app.database.db_main import get_session
from app.util.auth import get_current_user

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
      "full_name": "kartik",
      "username": "kartik",
      "email": "kartiksingh@gmail.com",
      "password": "Shiva10#bhole",
      "date_of_birth": "2001-04-06"
    }
    result_user1 = {
      "id": 1,
      "full_name": "kartik",
      "username": "kartik",
      "email": "kartiksingh@gmail.com",
      "date_of_birth": "2001-04-06"
    }

    response = client_unauthorized.post("/user", json=user1)  # Send the POST request
    assert response.status_code == 201  # Check the status code
    assert response.json() == result_user1  # Check the response body

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.id == 1
    assert result.full_name == "kartik"
    assert result.email == "kartiksingh@gmail.com"
    assert result.date_of_birth == datetime(2001, 4, 6, 0, 0).date()

def test_register_user_with_duplicate_username(client_unauthorized: TestClient, test_session: Session):
    user = {
      "full_name": "kartik",
      "username": "kartik",
      "email": "kartiksingh123@gmail.com",
      "password": "11Shiva10#bhole11",
      "date_of_birth": "2002-05-07"
    }

    response = client_unauthorized.post("/user", json=user)  # Send the POST request
    assert response.status_code == 400  # Check the status code
    assert response.json() == {'detail': 'Username already exists'}

def test_register_user_with_duplicate_email(client_unauthorized: TestClient, test_session: Session):
    user = {
      "full_name": "kartik",
      "username": "kartik123",
      "email": "kartiksingh@gmail.com",
      "password": "11Shiva10#bhole11",
      "date_of_birth": "2002-05-07"
    }

    response = client_unauthorized.post("/user", json=user)  # Send the POST request
    assert response.status_code == 400  # Check the status code
    assert response.json() == {'detail': 'Email already exists'}

def test_register_users(client_unauthorized: TestClient, test_session: Session):
    user2 = {
      "full_name": "admin",
      "username": "admin",
      "email": "adminUser@gmail.com",
      "password": "11#Admin#11",
      "date_of_birth": "1997-07-07"
    }
    user3 = {
      "full_name": "suman",
      "username": "suman",
      "email": "sumansingh137@gmail.com",
      "password": "Bam10#bhole",
      "date_of_birth": "1975-06-11"
    }
    user4 = {
      "full_name": "arvind",
      "username": "A.k Singh",
      "email": "arvindsingh45057@gmail.com",
      "password": "10#Bhole#10",
      "date_of_birth": "1976-07-10"
    }
    result_user2 = {
      "id": 2,
      "full_name": "admin",
      "username": "admin",
      "email": "adminUser@gmail.com",
      "date_of_birth": "1997-07-07"
    }
    result_user3 = {
      "id": 3,
      "full_name": "suman",
      "username": "suman",
      "email": "sumansingh137@gmail.com",
      "date_of_birth": "1975-06-11"
    }
    result_user4 = {
      "id": 4,
      "full_name": "arvind",
      "username": "A.k Singh",
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
    response = client_unauthorized.get("/user/me")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}


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

@pytest.fixture
def client_user3(test_session: Session):
    def override_get_current_user():  # Override for tests
        statement = select(User).where(User.id == 3)
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
      "full_name": "kartik",
      "username": "kartik",
      "email": "kartiksingh@gmail.com",
      "date_of_birth": "2001-04-06"
    }

    response = client.get("/user/me")  # Send the get request
    assert response.status_code == 200  # Check the status code
    assert response.json() == result # Check the response body

def test_get_all_users(client: TestClient, test_session: Session):
    response = client.get("/user/all/?offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 4, 'full_name': 'arvind', 'username': 'A.k Singh', 'email': 'arvindsingh45057@gmail.com', 'date_of_birth': '1976-07-10'}, {'id': 2, 'full_name': 'admin', 'username': 'admin', 'email': 'adminUser@gmail.com', 'date_of_birth': '1997-07-07'}, {'id': 1, 'full_name': 'kartik', 'username': 'kartik', 'email': 'kartiksingh@gmail.com', 'date_of_birth': '2001-04-06'}, {'id': 3, 'full_name': 'suman', 'username': 'suman', 'email': 'sumansingh137@gmail.com', 'date_of_birth': '1975-06-11'}]

def test_get_all_users_with_offset_limit(client: TestClient, test_session: Session):
    response = client.get("/user/all/?offset=1&limit=2")
    assert response.status_code == 200
    assert response.json() == [{'id': 2, 'full_name': 'admin', 'username': 'admin', 'email': 'adminUser@gmail.com', 'date_of_birth': '1997-07-07'}, {'id': 1, 'full_name': 'kartik', 'username': 'kartik', 'email': 'kartiksingh@gmail.com', 'date_of_birth': '2001-04-06'}]

def test_get_user_by_id_for_non_existing_user(client: TestClient, test_session: Session):
    response = client.get("/user/50")
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

def test_update_user_full_name(client: TestClient, test_session: Session):
    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.full_name == "kartik"

    response = client.put("/user/me/full_name/?full_name=kartik singh")
    assert response.status_code == 200
    assert response.json() == {'message': "User's full name updated successfully"}

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.full_name == "kartik singh"

def test_update_username(client: TestClient, test_session: Session):
    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.username == "kartik"

    response = client.put("/user/me/username/?username=kartik._.singh")
    assert response.status_code == 200
    assert response.json() == {'message': "username updated successfully"}

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.username == "kartik._.singh"

    #reverse update
    response = client.put("/user/me/username/?username=kartik")
    assert response.status_code == 200
    assert response.json() == {'message': "username updated successfully"}

def test_update_user_date_of_birth(client: TestClient, test_session: Session):
    response = client.put("/user/me/dob/?date_of_birth=2001-04-07")
    assert response.status_code == 200
    assert response.json() == {'message': 'date of birth updated successfully'}

    statement = select(User).where(User.id == 1)
    result = test_session.exec(statement).first()
    assert result.date_of_birth == datetime(2001, 4, 7, 0, 0).date()

def test_create_trip_with_user1_as_current_user(client: TestClient, test_session: Session):
    trip1 = {
        "title": "Kedarnath, Haridwar, Nainital",
        "start_date": "2025-03-20",
        "users": [1, 3, 4]
    }

    trip2 = {  
        "title": "Rajasthan trip",
        "start_date": "2025-05-05",
        "users": [1, 3]
    }

    response = client.post("/trip", json=trip1)
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'title': 'Kedarnath, Haridwar, Nainital', 'start_date': '2025-03-20', 'end_date': None, 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}

    statement = select(Trip).where(Trip.title == "Kedarnath, Haridwar, Nainital")
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 3, 20, 0, 0).date()
    assert result.created_by_id == 1

    response = client.post("/trip", json=trip2)
    assert response.status_code == 201
    assert response.json() == {'id': 2, 'title': 'Rajasthan trip', 'start_date': '2025-05-05', 'end_date': None, 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}]}

    statement = select(Trip).where(Trip.title == "Rajasthan trip")
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 5, 5, 0, 0).date()
    assert result.created_by_id == 1

def test_create_trip_with_user3_as_current_user(client_user3: TestClient, test_session: Session):
    trip3 = {
        "title": "Pondicherry trip",
        "start_date": "2025-03-15",
        "users": [1]
    }

    trip4 = {  
        "title": "Ooty, Nandi hills trip",
        "start_date": "2025-04-05",
        "users": [3, 4]
    }

    response = client_user3.post("/trip", json=trip3)
    assert response.status_code == 201
    assert response.json() == {'id': 3, 'title': 'Pondicherry trip', 'start_date': '2025-03-15', 'end_date': None, 'created_by': {'id': 3, 'username': 'suman'}, 'users': [{'id': 1, 'username': 'kartik'}]}

    statement = select(Trip).where(Trip.title == "Pondicherry trip")
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 3, 15, 0, 0).date()
    assert result.created_by_id == 3

    response = client_user3.post("/trip", json=trip4)
    assert response.status_code == 201
    assert response.json() == {'id': 4, 'title': 'Ooty, Nandi hills trip', 'start_date': '2025-04-05', 'end_date': None, 'created_by': {'id': 3, 'username': 'suman'}, 'users': [{'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}

    statement = select(Trip).where(Trip.title == "Ooty, Nandi hills trip")
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 4, 5, 0, 0).date()
    assert result.created_by_id == 3

def test_get_trips_created_by_user1(client: TestClient):
    response = client.get("/user/me/trips/created/?offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Haridwar, Nainital', 'start_date': '2025-03-20', 'end_date': None}, {'id': 2, 'title': 'Rajasthan trip', 'start_date': '2025-05-05', 'end_date': None}]

def test_get_trips_participated_by_user1(client: TestClient):
    response = client.get("/user/me/trips/participated/?offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Haridwar, Nainital', 'start_date': '2025-03-20', 'end_date': None}, {'id': 2, 'title': 'Rajasthan trip', 'start_date': '2025-05-05', 'end_date': None}, {'id': 3, 'title': 'Pondicherry trip', 'start_date': '2025-03-15', 'end_date': None}]

def test_get_trips_created_by_user3(client_user3: TestClient):
    response = client_user3.get("/user/me/trips/created/?offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 3, 'title': 'Pondicherry trip', 'start_date': '2025-03-15', 'end_date': None}, {'id': 4, 'title': 'Ooty, Nandi hills trip', 'start_date': '2025-04-05', 'end_date': None}]

def test_get_trips_participated_by_user3(client_user3: TestClient):
    response = client_user3.get("/user/me/trips/participated/?offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Haridwar, Nainital', 'start_date': '2025-03-20', 'end_date': None}, {'id': 2, 'title': 'Rajasthan trip', 'start_date': '2025-05-05', 'end_date': None}, {'id': 4, 'title': 'Ooty, Nandi hills trip', 'start_date': '2025-04-05', 'end_date': None}]

def test_add_traveller_to_a_trip_by_authorized_user(client_user3: TestClient, test_session: Session):
    response = client_user3.put("/trip/traveller/add/?trip_id=3&user_id=4")
    assert response.status_code == 200
    assert response.json() == {'message': 'User added to the trip successfully'}

    statement = select(Trip).where(Trip.id == 3)
    result = test_session.exec(statement).first()
    assert any(user.id == 4 for user in result.users)

def test_add_traveller_to_a_trip_by_unauthorized_user(client: TestClient, test_session: Session):
    response = client.put("/trip/traveller/add/?trip_id=3&user_id=3")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Insufficient privileges'}

    statement = select(Trip).where(Trip.id == 3)
    result = test_session.exec(statement).first()
    assert not any(user.id == 3 for user in result.users)

def test_add_traveller_to_a_trip_which_do_not_exists(client_user3: TestClient, test_session: Session):
    response = client_user3.put("/trip/traveller/add/?trip_id=7&user_id=4")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Trip not found'}

def test_add_traveller_which_do_not_exists_to_a_trip(client_user3: TestClient, test_session: Session):
    response = client_user3.put("/trip/traveller/add/?trip_id=3&user_id=5")
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

def test_add_traveller_to_a_trip_where_traveller_and_trip_both_do_not_exist(client_user3: TestClient, test_session: Session):
    response = client_user3.put("/trip/traveller/add/?trip_id=7&user_id=5")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Trip and User both not found'}

def test_remove_traveller_from_the_trip_authorized(client_user3: TestClient, test_session: Session):
    response = client_user3.delete("/trip/traveller/remove/?trip_id=3&user_id=4")
    assert response.status_code == 200
    assert response.json() == {'message': 'User removed from the trip successfully'}

    statement = select(Trip).where(Trip.id == 3)
    result = test_session.exec(statement).first()
    assert not any(user.id == 4 for user in result.users)

def test_remove_traveller_from_the_trip_unauthorized(client: TestClient, test_session: Session):
    response = client.delete("/trip/traveller/remove/?trip_id=3&user_id=1")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Insufficient privileges'}

    statement = select(Trip).where(Trip.id == 3)
    result = test_session.exec(statement).first()
    assert any(user.id == 1 for user in result.users)

def test_remove_traveller_from_the_trip_which_do_not_exists(client_user3: TestClient, test_session: Session):
    response = client_user3.delete("/trip/traveller/remove/?trip_id=7&user_id=4")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Trip not found'}

def test_remove_traveller_which_do_not_exits_from_the_trip(client_user3: TestClient, test_session: Session):
    response = client_user3.delete("/trip/traveller/remove/?trip_id=3&user_id=8")
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred: 404: User not found'}

def test_update_trip_title_authorized(client: TestClient, test_session: Session):
    response = client.put("/trip/update/title/?trip_id=1&title=Kedarnath, Tungnath, Deoriatal")
    assert response.status_code == 200
    assert response.json() == {'message': 'Title updated successfully'}

    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.title == "Kedarnath, Tungnath, Deoriatal"

def test_update_trip_title_unauthorized(client_user3: TestClient, test_session: Session):
    response = client_user3.put("/trip/update/title/?trip_id=1&title=Kedarnath, Tungnath, Deoriatal, Guptkashi")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Insufficient privileges'}

    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.title == "Kedarnath, Tungnath, Deoriatal"

def test_update_title_of_trip_which_do_not_exists(client: TestClient, test_session: Session):
    response = client.put("/trip/update/title/?trip_id=7&title=Ayodhya Ram Mandir")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Trip not found'}

def test_update_trip_dates_authorized(client: TestClient, test_session: Session):
    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 3, 20, 0, 0).date()
    assert result.end_date == None

    response = client.put("/trip/update/dates/?trip_id=1&start_date=2025-03-21&end_date=2025-03-23")
    assert response.status_code == 200
    assert response.json() == {'message': 'Date updated successfully'}

    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 3, 21, 0, 0).date()
    assert result.end_date == datetime(2025, 3, 23, 0, 0).date()

def test_update_trip_dates_unauthorized(client: TestClient, test_session: Session):
    response = client.put("/trip/update/dates/?trip_id=3&start_date=2025-03-21&end_date=2025-03-23")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Insufficient privileges'}

def test_update_trip_start_date_only(client: TestClient, test_session: Session):
    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 3, 21, 0, 0).date()

    response = client.put("/trip/update/dates/?trip_id=1&start_date=2025-03-20")
    assert response.status_code == 200
    assert response.json() == {'message': 'Date updated successfully'}

    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.start_date == datetime(2025, 3, 20, 0, 0).date()

def test_update_trip_end_date_only(client: TestClient, test_session: Session):
    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.end_date == datetime(2025, 3, 23, 0, 0).date()

    response = client.put("/trip/update/dates/?trip_id=1&end_date=2025-03-25")
    assert response.status_code == 200
    assert response.json() == {'message': 'Date updated successfully'}

    statement = select(Trip).where(Trip.id == 1)
    result = test_session.exec(statement).first()
    assert result.end_date == datetime(2025, 3, 25, 0, 0).date()

def test_create_trips(client: TestClient):
    trip5 = {
        "title": "Mahakal Ujjain",
        "start_date": "2024-11-17",
        "end_date": "2024-11-18",
        "users": [1, 3, 4]
    }

    trip6 = {  
        "title": "Somnath/Dwarka",
        "start_date": "2024-12-25",
        "end_date": "2024-12-27",
        "users": [1, 3]
    }

    response = client.post("/trip", json=trip5)
    assert response.status_code == 201

    response = client.post("/trip", json=trip6)
    assert response.status_code == 201

def test_get_trips_starting_after_date(client: TestClient):
    response = client.get("/trip/?start_after=2025-01-01")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Tungnath, Deoriatal', 'start_date': '2025-03-20', 'end_date': '2025-03-25', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}, {'id': 2, 'title': 'Rajasthan trip', 'start_date': '2025-05-05', 'end_date': None, 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}]}]

def test_get_trips_starting_after_date_with_title(client: TestClient):
    response = client.get("/trip/?start_after=2024-01-01&title=Somnath/Dwark")
    assert response.status_code == 200
    assert response.json() == [{'id': 6, 'title': 'Somnath/Dwarka', 'start_date': '2024-12-25', 'end_date': '2024-12-27', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}]}]

def test_get_trips_starting_before_date(client: TestClient):
    response = client.get("/trip/?start_before=2025-01-01")
    assert response.status_code == 200
    assert response.json() == [{'id': 5, 'title': 'Mahakal Ujjain', 'start_date': '2024-11-17', 'end_date': '2024-11-18', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}, {'id': 6, 'title': 'Somnath/Dwarka', 'start_date': '2024-12-25', 'end_date': '2024-12-27', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}]}]

def test_get_trips_ending_after_date(client: TestClient):
    response = client.get("/trip/?end_after=2025-04-01")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item not Found'}

def test_get_trips_ending_before_date(client: TestClient):
    response = client.get("/trip/?end_before=2024-12-27")
    assert response.status_code == 200
    assert response.json() == [{'id': 5, 'title': 'Mahakal Ujjain', 'start_date': '2024-11-17', 'end_date': '2024-11-18', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_get_trips_starting_between_dates(client: TestClient):
    response = client.get("/trip/?start_after=2025-01-01&start_before=2025-04-01")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Tungnath, Deoriatal', 'start_date': '2025-03-20', 'end_date': '2025-03-25', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_get_trips_ending_between_dates_but_start_date_beyond_end_date(client: TestClient):
    response = client.get("/trip/?end_after=2025-12-27&end_before=2025-04-01")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item not Found'}

def test_get_trips_ending_between_dates(client: TestClient):
    response = client.get("/trip/?end_after=2024-12-27&end_before=2025-04-01")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Tungnath, Deoriatal', 'start_date': '2025-03-20', 'end_date': '2025-03-25', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_get_user_trips_starting_within_daterange_and_ending_after_specified_date(client: TestClient):
    response = client.get("/trip/?start_after=2024-01-01&start_before=2025-04-01&end_after=2024-12-27")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'title': 'Kedarnath, Tungnath, Deoriatal', 'start_date': '2025-03-20', 'end_date': '2025-03-25', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_get_user_trips_starting_within_daterange_and_ending_before_specified_date(client: TestClient):
    response = client.get("/trip/?start_after=2024-01-01&start_before=2025-04-01&end_before=2024-12-27")
    assert response.status_code == 200
    assert response.json() == [{'id': 5, 'title': 'Mahakal Ujjain', 'start_date': '2024-11-17', 'end_date': '2024-11-18', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_get_user_trips_ending_within_daterange_and_starting_after_specified_date(client: TestClient):
    response = client.get("/trip/?start_after=2024-01-01&end_after=2024-04-01&end_before=2024-12-27")
    assert response.status_code == 200
    assert response.json() == [{'id': 5, 'title': 'Mahakal Ujjain', 'start_date': '2024-11-17', 'end_date': '2024-11-18', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_get_user_trips_ending_within_daterange_and_starting_before_specified_date(client: TestClient):
    response = client.get("/trip/?start_before=2025-01-01&end_after=2024-12-01&end_before=2025-12-27")
    assert response.status_code == 200
    assert response.json() == [{'id': 6, 'title': 'Somnath/Dwarka', 'start_date': '2024-12-25', 'end_date': '2024-12-27', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}]}]

def test_get_user_trips_starting_within_daterange_and_ending_within_daterange(client: TestClient):
    response = client.get("/trip/?start_after=2024-01-01&start_before=2025-04-01&end_after=2024-12-01&end_before=2024-03-23")
    assert response.status_code == 200
    assert response.json() == [{'id': 5, 'title': 'Mahakal Ujjain', 'start_date': '2024-11-17', 'end_date': '2024-11-18', 'created_by': {'id': 1, 'username': 'kartik'}, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}]}]

def test_delete_trip(client: TestClient, test_session: Session):
    statement = select(Trip).where(Trip.id == 6)
    result= test_session.exec(statement).first()
    assert result.title == 'Somnath/Dwarka'

    response = client.delete("/trip/remove/?trip_id=6")
    assert response.status_code == 200
    assert response.json() == {'message': 'Trip deleted successfully'}

    statement = select(Trip).where(Trip.id == 6)
    result= test_session.exec(statement).first()
    assert result == None

def test_create_expense(client: TestClient, test_session: Session):
    payment1 = {
        "currency": "INR",
        "amount": 500,
        "payment_mode": "Cash",
        "payment_date": "2025-03-21T10:00:00Z",
        "user_id": 1,
        "expense_id": 1
    }
    payment2 = {
        "currency": "INR",
        "amount": 350,
        "payment_mode": "Cash",
        "payment_date": "2025-03-21T20:00:00Z",
        "user_id": 1,
        "expense_id": 1
    }
    payment3 = {
        "currency": "INR",
        "amount": 200,
        "payment_mode": "UPI",
        "payment_date": "2025-03-21T20:00:00Z",
        "user_id": 3,
        "expense_id": 1
    }
    expense1 = {
        "description": "Breakfast day 1",
        "trip_id": 1,
        "payments": [payment1],
        "users": [1, 3, 4]
    }
    expense2 = {
        "description": "Dinner day 1",
        "trip_id": 1,
        "payments": [payment2, payment3],
        "users": [1, 3, 4]
    }

    response = client.post("/expense", json=expense1)
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'description': 'Breakfast day 1', 'trip_id': 1, 'payments': [{'id': 1, 'currency': 'INR', 'amount': 500.0, 'payment_mode': 'Cash'}]}

    response = client.post("/expense", json=expense2)
    print(response.json())
    assert response.status_code == 201
    assert response.json() == {'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'Cash'}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI'}]}

def test_get_expense_by_id(client: TestClient):
    response = client.get("/expense/1")
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'description': 'Breakfast day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 1, 'currency': 'INR', 'amount': 500.0, 'payment_mode': 'Cash', 'user': {'id': 1, 'username': 'kartik'}}]}

    response = client.get("/expense/2")
    assert response.status_code == 200
    assert response.json() == {'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'Cash', 'user': {'id': 1, 'username': 'kartik'}}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI', 'user': {'id': 3, 'username': 'suman'}}]}

    response = client.get("/expense/3")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item not Found'}

def test_get_all_expenses_for_the_trip(client: TestClient):
    response = client.get("/expense/trip/all/?trip_id=1&offset=0&limit=1")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'description': 'Breakfast day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 1, 'currency': 'INR', 'amount': 500.0, 'payment_mode': 'Cash', 'user': {'id': 1, 'username': 'kartik'}}]}]
    
    response = client.get("/expense/trip/all/?trip_id=1&offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 1, 'description': 'Breakfast day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 1, 'currency': 'INR', 'amount': 500.0, 'payment_mode': 'Cash', 'user': {'id': 1, 'username': 'kartik'}}]}, {'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'Cash', 'user': {'id': 1, 'username': 'kartik'}}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI', 'user': {'id': 3, 'username': 'suman'}}]}]

def test_update_expense_description(client: TestClient, test_session: Session):
    statement = select(Expense).where(Expense.id == 1)
    result = test_session.exec(statement).first()
    assert result.description == "Breakfast day 1"

    response = client.put("/expense/update/description/?expense_id=1&description=Breakfast day 1 (croissant and pasta)")
    assert response.status_code == 200
    assert response.json() == {'message': 'Description updated successfully'}

    statement = select(Expense).where(Expense.id == 1)
    result = test_session.exec(statement).first()
    assert result.description == "Breakfast day 1 (croissant and pasta)"

def test_delete_expense(client: TestClient, test_session: Session):
    statement = select(Expense).where(Expense.id == 1)
    result = test_session.exec(statement).first()
    users = [user.id for user in result.users] if result.users else []
    payments = [payment.id for payment in result.payments] if result.payments else []
    assert result.description == "Breakfast day 1 (croissant and pasta)"
    assert users == [1, 3, 4]
    assert payments ==  [1]

    statement = select(UserExpenseLink).where(UserExpenseLink.expense_id == 1)
    result = test_session.exec(statement).all()
    assert len(result) == 3

    response = client.delete("/expense/?expense_id=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Expense deleted successfully"}

    statement = select(Expense).where(Expense.id == 1)
    result = test_session.exec(statement).first()
    assert result == None

    statement = select(Payment).where(Payment.id == 1)
    result = test_session.exec(statement).first()
    assert result == None

    statement = select(UserExpenseLink).where(UserExpenseLink.expense_id == 1)
    result = test_session.exec(statement).all()
    assert len(result) == 0

def test_get_payment_details_by_id(client: TestClient):
    response = client.get("/payment/2")
    assert response.status_code == 200
    assert response.json() == {'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'Cash', 'user': {'id': 1, 'username': 'kartik'}, 'payment_date': '2025-03-21T20:00:00', 'notes': None}

    response = client.get("/payment/1")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item not Found'}

def test_update_payment_details(client: TestClient, test_session: Session):
    statement = select(Payment).where(Payment.id == 2)
    result = test_session.exec(statement).first()
    assert result.amount == 350.0

    response = client.put("/payment/?payment_id=2&amount=351")
    assert response.status_code == 200
    assert response.json() == {'message': 'details updated successfully'}

    statement = select(Payment).where(Payment.id == 2)
    result = test_session.exec(statement).first()
    assert result.amount == 351.0

    statement = select(Payment).where(Payment.id == 2)
    result = test_session.exec(statement).first()
    assert result.payment_mode == PaymentMode.CASH

    response = client.put("/payment/?payment_id=2&amount=350&payment_mode=UPI")
    assert response.status_code == 200
    assert response.json() == {'message': 'details updated successfully'}

    statement = select(Payment).where(Payment.id == 2)
    result = test_session.exec(statement).first()
    assert result.amount == 350.0

    statement = select(Payment).where(Payment.id == 2)
    result = test_session.exec(statement).first()
    assert result.payment_mode == PaymentMode.UPI

def test_create_payment(client: TestClient, test_session: Session):
    payment = {
        'id': 2,
        'currency': 'INR',
        'amount': 150.0, 
        'payment_mode': 'Cash',
        'payment_date': '2025-03-21T20:01:00Z',
        'user_id': 4,
        'expense_id': 2
        }
    
    response = client.get("/expense/2")
    assert response.status_code == 200
    assert response.json() == {'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'UPI', 'user': {'id': 1, 'username': 'kartik'}}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI', 'user': {'id': 3, 'username': 'suman'}}]}

    response = client.post("/payment", json=payment)
    assert response.status_code == 201
    assert response.json() == {'id': 4, 'currency': 'INR', 'amount': 150.0, 'payment_mode': 'Cash', 'user': {'id': 4, 'username': 'A.k Singh'}, 'payment_date': '2025-03-21T20:01:00', 'notes': None}

    response = client.get("/payment/4")
    assert response.status_code == 200
    assert response.json() == {'id': 4, 'currency': 'INR', 'amount': 150.0, 'payment_mode': 'Cash', 'user': {'id': 4, 'username': 'A.k Singh'}, 'payment_date': '2025-03-21T20:01:00', 'notes': None}

    response = client.get("/expense/2")
    assert response.status_code == 200
    assert response.json() == {'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'UPI', 'user': {'id': 1, 'username': 'kartik'}}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI', 'user': {'id': 3, 'username': 'suman'}}, {'id': 4, 'currency': 'INR', 'amount': 150.0, 'payment_mode': 'Cash', 'user': {'id': 4, 'username': 'A.k Singh'}}]}

def test_delete_payment(client: TestClient, test_session: Session):
    response = client.delete("/payment/?payment_id=4")
    assert response.status_code == 200
    assert response.json() == {'message': 'Payment deleted successfully'}

    response = client.get("/payment/4")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Item not Found'}

    response = client.get("/expense/2")
    assert response.status_code == 200
    assert response.json() == {'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'UPI', 'user': {'id': 1, 'username': 'kartik'}}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI', 'user': {'id': 3, 'username': 'suman'}}]}

def test_get_equal_share_distribution(client: TestClient, test_session: Session):
    expenses = []
    response = client.get("/expense/trip/all/?trip_id=1&offset=0&limit=10")
    assert response.status_code == 200
    assert response.json() == [{'id': 2, 'description': 'Dinner day 1', 'trip_id': 1, 'users': [{'id': 1, 'username': 'kartik'}, {'id': 3, 'username': 'suman'}, {'id': 4, 'username': 'A.k Singh'}], 'payments': [{'id': 2, 'currency': 'INR', 'amount': 350.0, 'payment_mode': 'UPI', 'user': {'id': 1, 'username': 'kartik'}}, {'id': 3, 'currency': 'INR', 'amount': 200.0, 'payment_mode': 'UPI', 'user': {'id': 3, 'username': 'suman'}}]}]
    expenses = response.json()

    response = client.post("/payment/distribute", json=[2])
    assert response.status_code == 200
    assert response.json() == ['4 needs to give INR 166.67 to 1', '4 needs to give INR 16.67 to 3']
