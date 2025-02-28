from typing import List
from sqlmodel import Session, select, update
from app.database.db_models import Payment
from app.models import Payment_Create
from sqlalchemy.orm import selectinload

def create_payment_in_db(payment: Payment_Create, session: Session):
    try:
        new_payment = Payment(currency=payment.currency, amount=payment.amount, payment_mode=payment.payment_mode, payment_date=payment.payment_date, notes=payment.notes, user_id=payment.user_id, expense_id=payment.expense_id)
        session.add(new_payment)
        session.commit()
        session.refresh(new_payment)
        return new_payment
    except Exception as e:
        session.rollback()
        raise e

def get_payment_by_id_from_db(payment_id: int, session: Session):
    try:
        statement = select(Payment).where(Payment.id == payment_id).options(selectinload(Payment.expense))
        result = session.exec(statement).first()
        if result:
            payment_part_of_expense = result.expense
            return result
    except Exception as e:
        raise e

def get_payment_by_ids_from_db(payment_ids: List[int], session: Session):
    try:
        statement = select(Payment).where(Payment.id.in_(payment_ids)).options(selectinload(Payment.user))
        result = session.exec(statement).all()
        return result
    except Exception as e:
        raise e

def update_payment_details_in_db(payment_id, currency, amount, payment_mode, user_id, session: Session):
    try:
        query = update(Payment).where(Payment.id == payment_id)
        if currency and amount and payment_mode and user_id:
            statement = query.values(currency=currency, amount=amount, payment_mode=payment_mode, user_id=user_id)
        elif currency and amount and payment_mode:
            statement = query.values(currency=currency, amount=amount, payment_mode=payment_mode)
        elif currency and amount and user_id:
            statement = query.values(currency=currency, amount=amount, user_id=user_id)
        elif amount and payment_mode and user_id:
            statement = query.values(amount=amount, payment_mode=payment_mode, user_id=user_id)
        elif currency and amount:
            statement = query.values(currency=currency, amount=amount)
        elif currency and payment_mode:
            statement = query.values(currency=currency, payment_mode=payment_mode)
        elif currency and user_id:
            statement = query.values(currency=currency, user_id=user_id)
        elif amount and payment_mode:
            statement = query.values(amount=amount, payment_mode=payment_mode)
        elif amount and user_id:
            statement = query.values(amount=amount, user_id=user_id)
        elif payment_mode and user_id:
            statement = query.values(payment_mode=payment_mode, user_id=user_id)
        elif currency:
            statement = query.values(currency=currency)
        elif amount:
            statement = query.values(amount=amount)
        elif payment_mode:
            statement = query.values(payment_mode=payment_mode)
        elif user_id:
            statement = query.values(user_id=user_id)

        session.exec(statement)
        session.commit()
        return {"message": "details updated successfully"}
    except Exception as e:
        session.rollback()
        raise e

def delete_payment_from_db(payment_id: int, session: Session):
    try:
        statement = select(Payment).where(Payment.id == payment_id)
        result = session.exec(statement).first()
        if result:
            session.delete(result)
            session.commit()
            return {"message": "Payment deleted successfully"}

        return None
    except Exception as e:
        session.rollback()
        raise e