from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlmodel import Session
from app.database.db_main import get_session
from app.database.expense_crud import create_expense_in_db, get_all_expenses_for_the_trip_from_db, get_expense_details_from_db
from app.database.trip_crud import get_trip_by_id_from_db
from app.models import Expense_Create, Expense_Read, User_Read
from app.util.auth import get_current_user


router = APIRouter()

@router.post("/expense", status_code=status.HTTP_201_CREATED)
def create_expense(expense: Expense_Create, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = create_expense_in_db(expense, current_user, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/expense/trip/all", status_code=status.HTTP_201_CREATED, response_model=List[Expense_Read])
def get_all_expenses_for_the_trip(trip_id: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        trip = get_trip_by_id_from_db(trip_id, session)
        if not trip.created_by_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Insufficient privileges")

        result = get_all_expenses_for_the_trip_from_db(trip_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.get("/expense/{id}", status_code=status.HTTP_201_CREATED, response_model=Expense_Read)
def get_expense_by_id(expense_id: int, session: Session = Depends(get_session)):
    try:
        result = get_expense_details_from_db(expense_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result
