from sqlmodel import Session, select
from app.database.db_models import Expense, Payment, Trip, User
from app.models import Expense_Create
from app.database.db_main import engine
from sqlalchemy.orm import selectinload


def create_expense_in_db(expense: Expense_Create, current_user: User):
    try:
        with Session(engine) as session: 
            user_ids = expense.users
            statement = select(User).where(User.id.in_(user_ids))
            split_between_users = session.exec(statement).all()

            expense_payments = []
            payments = expense.payments
            if payments:
                for payment in payments:
                    new_payment = Payment(currency=payment.currency, amount=payment.amount, payment_mode=payment.payment_mode, user_id=payment.user_id)
                    expense_payments.append(new_payment)

            new_expense = Expense(description=expense.description, amount=expense.amount, trip_id=expense.trip_id, payments=expense_payments, users=split_between_users)
            session.add(new_expense)
            session.commit()
            session.refresh(new_expense)
            return new_expense
    except Exception as e:
        session.rollback()
        raise e
    
def get_all_expenses_for_the_trip_from_db(trip_id: int):
    with Session(engine) as session:
        try:
            statement = select(Expense).where(Expense.trip_id == trip_id).options(selectinload(Expense.users))
            result = session.exec(statement).all()
            for item in result:
                payments = item.payments
                trip = item.trip

            return result
        except Exception as e:
            raise e
    
def get_expense_details_from_db(expense_id: int):
    with Session(engine) as session:
        try:
            statement = select(Expense).where(Expense.id == expense_id).options(selectinload(Expense.users))
            result = session.exec(statement).first()
            payments = result.payments
            trip = result.trip
            return result
        except Exception as e:
            raise e
