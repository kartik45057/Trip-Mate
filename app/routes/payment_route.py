from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from sqlmodel import Session
from app.database.db_main import get_session
from app.database.payment_crud import get_payment_by_id_from_db, update_payment_details_in_db
from app.enums import CurrencyCode, PaymentMode
from app.models import Payment_Read, User_Read
from util.auth import get_current_user

admin_user_email = "adminUser@gmail.com"

router = APIRouter()
    
@router.get("/payment/{payment_id}", status_code=status.HTTP_200_OK, response_model=Payment_Read)
def get_payment_by_id(payment_id: int, current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = get_payment_by_id_from_db(payment_id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item not Found")
    return result

@router.put("/payment", status_code=status.HTTP_200_OK)
def update_payment_details(payment_id: int, currency: Optional[CurrencyCode] = Query(None), amount: Optional[float] = Query(None), payment_mode: Optional[PaymentMode] = Query(None), user_id: Optional[int] = Query(None), current_user: User_Read = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        result = update_payment_details_in_db(payment_id, currency, amount, payment_mode, user_id, session)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
