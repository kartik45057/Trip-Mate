from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from sqlmodel import Session
from app.database.db_main import get_session
from app.database.expense_crud import get_all_expenses_by_ids
from app.database.payment_crud import create_payment_in_db, delete_payment_from_db, get_payment_by_id_from_db, update_payment_details_in_db
from app.enums import CurrencyCode, PaymentMode
from app.models import Expense_Split_Exp, Payment_Create, Payment_Read, User_Read
from app.thirdPartyApi.exchange_rates import get_exchange_rates
from app.util.split_expenses import Get_Display_Messages, Get_Equal_Share_Distribution

admin_user_email = "adminUser@gmail.com"

router = APIRouter()

@router.post("/payment", status_code=status.HTTP_201_CREATED, response_model=Payment_Read)
def create_payment(payment: Payment_Create, session: Session = Depends(get_session)):
    try:
        result = create_payment_in_db(payment, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.post("/payment/distribute", status_code=status.HTTP_200_OK)
def get_equal_share_distribution(expense_ids: List[int],  session: Session = Depends(get_session)):
    try:
        expenses = get_all_expenses_by_ids(expense_ids, session)
        exchanges_rates_INR = get_exchange_rates()
        amount_to_be_received_and_from_by_userid = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
        result = Get_Display_Messages(amount_to_be_received_and_from_by_userid)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/payment/{payment_id}", status_code=status.HTTP_200_OK, response_model=Payment_Read)
def get_payment_details_by_id(payment_id: int, session: Session = Depends(get_session)):
    try:
        result = get_payment_by_id_from_db(payment_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.put("/payment", status_code=status.HTTP_200_OK)
def update_payment_details(payment_id: int, currency: Optional[CurrencyCode] = Query(None), amount: Optional[float] = Query(None), payment_mode: Optional[PaymentMode] = Query(None), user_id: Optional[int] = Query(None), session: Session = Depends(get_session)):
    try:
        result = update_payment_details_in_db(payment_id, currency, amount, payment_mode, user_id, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.delete("/payment", status_code=status.HTTP_200_OK)
def delete_payment(payment_id: int,  session: Session = Depends(get_session)):
    try:
        result = delete_payment_from_db(payment_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")

    return result

