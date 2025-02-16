from typing import List
from sqlmodel import Session, select, update
from app.database.db_models import Expense, Payment, Trip, User
from app.models import Expense_Create
from app.database.db_main import engine
from sqlalchemy.orm import selectinload
        
def get_payment_by_id_from_db(payment_id: int):
    with Session(engine) as session:
        try:
            statement = select(Payment).where(Payment.id == payment_id).options(selectinload(Payment.expense))
            result = session.exec(statement).first()
            payment_part_of_expense = result.expense
            return result
        except Exception as e:
            raise e

def get_payment_by_ids_from_db(payment_ids: List[int]):
    with Session(engine) as session:
        try:
            statement = select(Payment).where(Payment.id.in_(payment_ids)).options(selectinload(Payment.user))
            result = session.exec(statement).all()
            return result
        except Exception as e:
            raise e

def update_payment_details_in_db(payment_id, currency, amount, payment_mode, user_id):
    with Session(engine) as session:
        try:
            if amount:
                payment_detail = get_payment_by_id_from_db(payment_id)
                if payment_detail:
                    expense_id = payment_detail.expense_id
                    expense_amount = payment_detail.expense.amount
                    payment_amount = payment_detail.amount
                    if amount > payment_amount:
                        extra_amount = amount - payment_amount
                        statement_to_update_expense_amount = update(Expense).where(Expense.id == expense_id).values(amount = expense_amount + extra_amount)
                        session.exec(statement_to_update_expense_amount)
                    elif amount < payment_amount:
                        deducted_amount = payment_amount - amount
                        statement_to_update_expense_amount = update(Expense).where(Expense.id == expense_id).values(amount = expense_amount - deducted_amount)
                        session.exec(statement_to_update_expense_amount)
                else:
                    return {"message": "Item not found"}

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
