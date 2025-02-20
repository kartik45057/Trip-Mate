from datetime import timedelta
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.database.db_main import get_session
from app.database.user_crud import *
from app.models import User_Create, User_Read, Token
from typing import List
from app.util.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_hashed_password, get_current_user
from sqlalchemy.exc import IntegrityError


admin_user_email = "adminUser@gmail.com"

router = APIRouter()

@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=User_Read)
def register_user(user: User_Create, session: Session = Depends(get_session)):
    try:
        password = user.password
        hashed_password = get_hashed_password(password)
        result = create_user(user, hashed_password, session)
        return result
    except IntegrityError as e:
        if "UNIQUE constraint failed: user.email" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        elif "UNIQUE constraint failed: user.username" in str(e):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        else: # Some other IntegrityError
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An error occurred during user creation. Please check the provided information.") from e # Log the full error for debugging and return a generic message to the user
    except Exception as e: # Catch any other exceptions
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/user/all", status_code=status.HTTP_200_OK, response_model=List[User_Read])
def get_all_users(offset: int = Query(ge=0), limit: int = Query(ge=0), current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = get_all_users_from_db(offset, limit, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return result

@router.get("/user/me", status_code=status.HTTP_200_OK, response_model=User_Read)
def get_current_user(current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        current_user_email = current_user.email
        result = get_user_by_email(current_user_email, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return result

@router.get("/user/me/trips/created", status_code=status.HTTP_200_OK, response_model=List[Trip_Read_basic])
def get_trips_created_by_user(offset: int = Query(ge=0), limit: int = Query(ge=0), current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try: 
        current_user_email = current_user.email
        result = get_trips_created_by_user_from_db(offset, limit, current_user_email, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return result

@router.get("/user/me/trips/participated", status_code=status.HTTP_200_OK, response_model=List[Trip_Read_basic])
def get_trips_participated_by_user(offset: int = Query(ge=0), limit: int = Query(ge=0), current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try: 
        current_user_email = current_user.email
        result = get_trips_participated_by_user_from_db(offset, limit, current_user_email, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return result

@router.get("/users/me/payments", status_code=status.HTTP_200_OK, response_model=List[Payment_Read_without_user])
def get_payments_done_by_user(offset: int = Query(ge=0), limit: int = Query(ge=0), current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try: 
        current_user_email = current_user.email
        result = get_payments_done_by_user_from_db(offset, limit, current_user_email, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    return result

@router.get("/user/{id}", status_code=status.HTTP_200_OK, response_model=User_Read)
def get_user_by_id(id: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = get_user_by_id_from_db(id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return result

@router.put("/user/me/full_name", status_code=status.HTTP_200_OK)
def update_user_full_name(full_name: str, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        current_user_email = current_user.email
        result = update_user_full_name_in_db(full_name, current_user_email, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
@router.put("/user/me/dob", status_code=status.HTTP_200_OK)
def update_user_date_of_birth(date_of_birth: date, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        current_user_email = current_user.email
        result = update_user_date_of_birth_in_db(date_of_birth, current_user_email, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.put("/user/me/password", status_code=status.HTTP_200_OK)
def update_user_password(password: str,  current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        current_user_email = current_user.email
        hashed_password = get_hashed_password(password)
        result = update_user_password_in_db(hashed_password, current_user_email, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
