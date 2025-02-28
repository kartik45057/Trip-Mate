from typing import List
from sqlmodel import Session, select, update
from app.database.db_models import Expense, Payment, Trip, User, UserExpenseLink
from app.database.payment_crud import get_payment_by_ids_from_db
from app.models import Expense_Create
from app.database.db_main import engine
from sqlalchemy.orm import selectinload


def create_expense_in_db(expense: Expense_Create, current_user: User, session: Session):
    try: 
        user_ids = expense.users
        statement = select(User).where(User.id.in_(user_ids))
        split_between_users = session.exec(statement).all()

        expense_payments = []
        payments = expense.payments
        if payments:
            for payment in payments:
                new_payment = Payment(currency=payment.currency, amount=payment.amount, payment_mode=payment.payment_mode, payment_date=payment.payment_date, user_id=payment.user_id)
                expense_payments.append(new_payment)

        new_expense = Expense(description=expense.description, trip_id=expense.trip_id, payments=expense_payments, users=split_between_users)
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return new_expense
    except Exception as e:
        session.rollback()
        raise e

def get_expense_details_from_db(expense_id: int, session: Session):
    try:
        statement = select(Expense).where(Expense.id == expense_id).options(selectinload(Expense.users))
        result = session.exec(statement).first()
        if result:
            payments = result.payments
            for payment in payments:
                user = payment.user

        return result
    except Exception as e:
        raise e
    
def get_all_expenses_by_ids(expense_ids: List[int], session: Session):
    try:
        statement = select(Expense).where(Expense.id.in_(expense_ids)).options(selectinload(Expense.users))
        result = session.exec(statement).all()
        if result:
            for expense in result:
                payments = expense.payments
                if payments:
                    for payment in payments:
                        user = payment.user

        return result
    except Exception as e:
        raise e
    
def update_expense_description_in_db(expense_id: int, new_description: str, session: Session):
    try:
        statement = update(Expense).where(Expense.id == expense_id).values(description = new_description)
        session.exec(statement)
        session.commit()
        return {"message": "Description updated successfully"}
    except Exception as e:
        session.rollback()
        raise e
    
def delete_expense_in_db(expense_id: int, session: Session):
    try:
        statement = select(Expense).where(Expense.id == expense_id)
        expense = session.exec(statement).first()
        if expense:
            payment_ids = [payment.id for payment in expense.payments] if expense.payments else []
            statement = select(Payment).where(Payment.id.in_(payment_ids))
            payments = session.exec(statement).all()

            session.delete(expense)
            for payment in payments:
                session.delete(payment)

            session.commit()
            return {"message": "Expense deleted successfully"}
        else:
            return None
    except Exception as e:
        session.rollback()
        raise e
