from typing import List
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from sqlmodel import Session
from app.database.db_main import get_session
from app.database.expense_crud import create_expense_in_db, delete_expense_in_db, get_all_expenses_for_the_trip_from_db, get_expense_details_from_db, update_expense_description_in_db
from app.database.trip_crud import get_trip_by_id_from_db
from app.models import Expense_Create, Expense_Read, Expense_Read2, User_Read
from app.util.auth import get_current_user


router = APIRouter()

@router.post("/expense", status_code=status.HTTP_201_CREATED, response_model=Expense_Read2)
def create_expense(expense: Expense_Create, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = create_expense_in_db(expense, current_user, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/expense/trip/all", status_code=status.HTTP_200_OK, response_model=List[Expense_Read])
def get_all_expenses_for_the_trip(trip_id: int, offset: int, limit: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = get_all_expenses_for_the_trip_from_db(trip_id, offset, limit, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.get("/expense/{expense_id}", status_code=status.HTTP_200_OK, response_model=Expense_Read)
def get_expense_by_id(expense_id: int, session: Session = Depends(get_session)):
    try:
        result = get_expense_details_from_db(expense_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.put("/expense/update/description", status_code=status.HTTP_200_OK)
def update_expense_description(expense_id: int, description: str = Query(min_length=10, max_length=100), session: Session = Depends(get_session)):
    try:
        result = update_expense_description_in_db(expense_id, description, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.delete("/expense", status_code=status.HTTP_200_OK)
def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    try:
        result = delete_expense_in_db(expense_id, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    