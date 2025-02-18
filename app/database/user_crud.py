from sqlite3 import IntegrityError
from app.database.db_main import engine
from sqlmodel import Session, select, update
from app.models import *
from app.database.db_models import *
from sqlalchemy.orm import selectinload

def create_user(user: User_Create, hashed_password: str, session: Session):
    try:
        new_user = User(name=user.name, email=user.email, password=hashed_password, date_of_birth=user.date_of_birth)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except IntegrityError as e:
        session.rollback()
        raise e
    
def get_user_by_email(email: EmailStr, session: Session):
    try:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user
    except Exception as e:
        raise e

def get_all_users_from_db(offset: int, limit: int, session: Session):
    try:
        statement = select(User).order_by(User.name).offset(offset).limit(limit)
        result = session.exec(statement).all()
        return result
    except Exception as e:
        raise e

def get_user_by_id_from_db(user_id: int, session: Session):
    try:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement).first()
        return result
    except Exception as e:
        raise e
        
def get_user_by_ids_from_db(user_ids: List[int], session: Session):
    try:
        statement = select(User).where(User.id.in_(user_ids))
        result = session.exec(statement).all()
        return result
    except Exception as e:
        raise e

def get_trips_created_by_user_from_db(offset: int, limit: int, email: EmailStr, session: Session):
    try:
        statement = select(User).where(User.email == email).options(selectinload(User.user_created_trips))
        result = session.exec(statement).first()
        user_created_trips = result.user_created_trips
        length_of_user_created_trips = len(user_created_trips)
        if offset < length_of_user_created_trips:
            if offset + limit < length_of_user_created_trips:
                user_created_trips = user_created_trips[offset:offset+limit]
            else:
                user_created_trips = user_created_trips[offset:]
        else:
            return []
        return user_created_trips
    except Exception as e:
        raise e

def get_trips_participated_by_user_from_db(offset: int, limit: int, email: EmailStr, session: Session):
    try:
        statement = select(User).where(User.email == email).options(selectinload(User.trips))
        result = session.exec(statement).first()
        trips_in_which_user_participated = result.trips
        length_of_trips_in_which_user_participated = len(trips_in_which_user_participated)
        if offset < length_of_trips_in_which_user_participated:
            if offset + limit < length_of_trips_in_which_user_participated:
                trips_in_which_user_participated = trips_in_which_user_participated[offset:offset+limit]
            else:
                trips_in_which_user_participated = trips_in_which_user_participated[offset:]
        else:
            return []

        return trips_in_which_user_participated
    except Exception as e:
        raise e

def get_payments_done_by_user_from_db(offset: int, limit: int, email: EmailStr, session: Session):
    try:
        statement = select(User).where(User.email == email).options(selectinload(User.payments))
        result = session.exec(statement).first()
        user_payments = result.payments
        length_of_user_payments = len(user_payments)
        if offset < length_of_user_payments:
            if offset + limit < length_of_user_payments:
                user_payments = user_payments[offset:offset+limit]
            else:
                user_payments = user_payments[offset:]
        else:
            return []

        return user_payments
    except Exception as e:
        raise e

def update_user_name_in_db(new_name: str, email:EmailStr, session: Session):
    try:
        statement = update(User).where(User.email == email).values(name = new_name)
        session.exec(statement)
        session.commit()
        return {"message": "name updated successfully"}
    except Exception as e:
        session.rollback()
        raise e
        
def update_user_date_of_birth_in_db(new_date_of_birth: str, email:EmailStr, session: Session):
    try:
        statement = update(User).where(User.email == email).values(date_of_birth = new_date_of_birth)
        session.exec(statement)
        session.commit()
        return {"message": "date of birth updated successfully"}
    except Exception as e:
        session.rollback()
        raise e
        
def update_user_password_in_db(new_password: str, email:EmailStr, session: Session):
    try:
        statement = update(User).where(User.email == email).values(password = new_password)
        session.exec(statement)
        session.commit()
        return {"message": "password updated successfully"}
    except Exception as e:
        session.rollback()
        raise e
