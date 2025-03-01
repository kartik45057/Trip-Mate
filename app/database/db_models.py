from datetime import date, datetime, timezone
import re
from pydantic import EmailStr, field_validator, validator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from app.enums import CurrencyCode, PaymentMode

class UserTripLink(SQLModel, table=True):
    trip_id: int | None = Field(default=None, foreign_key="trip.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)

class UserExpenseLink(SQLModel, table=True):
    expense_id: int | None = Field(default=None, foreign_key="expense.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(sa_column_kwargs={"unique": True})
    password: str
    username: str = Field(min_length=3, max_length=15, sa_column_kwargs={"unique": True}, index=True)
    full_name: str = Field(min_length=2, max_length=50)
    date_of_birth: date
    currency: CurrencyCode = Field(default="INR")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) if datetime.now(timezone.utc) else None, description="Account creation timestamp")

    user_created_trips: List["Trip"] = Relationship(back_populates="created_by", sa_relationship_kwargs={"lazy": "selectin"},)
    trips: List["Trip"] = Relationship(back_populates="users", link_model=UserTripLink)
    expenses: List["Expense"] = Relationship(back_populates="users", link_model=UserExpenseLink)
    payments: List["Payment"] = Relationship(back_populates="user")

class Trip(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=3, max_length=50)
    start_date: date
    end_date: Optional[date] = Field(default=None)
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) if datetime.now(timezone.utc) else None, description="Trip creation timestamp")

    created_by: Optional[User] = Relationship(back_populates="user_created_trips", sa_relationship_kwargs={"lazy": "selectin"},)
    users: Optional[List[User]] = Relationship(back_populates="trips", link_model=UserTripLink)
    expenses: Optional[List["Expense"]] = Relationship(back_populates="trip")

    __table_args__ = (UniqueConstraint("title", "start_date", "end_date", "created_by_id", name="unique_trip_constraint"),)

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None, min_length=10, max_length=100)
    trip_id: int | None = Field(default=None, foreign_key="trip.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) if datetime.now(timezone.utc) else None, description="Expense creation timestamp")

    users: List[User] = Relationship(back_populates="expenses", link_model=UserExpenseLink)
    trip: Trip | None = Relationship(back_populates="expenses")
    payments: List["Payment"] = Relationship(back_populates="expense")

class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    currency: CurrencyCode
    amount: float
    payment_mode: PaymentMode
    payment_date: datetime = Field(default=None, description="Date and time of the payment") # Date and time of payment 
    notes: Optional[str] = Field(default=None, description="Any notes related to the payment")  # Optional notes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) if datetime.now(timezone.utc) else None, description="Payment creation timestamp")
    user_id: int | None = Field(default=None, foreign_key="user.id")
    expense_id: int | None = Field(default=None, foreign_key="expense.id")

    user: User | None = Relationship(back_populates="payments")
    expense: Expense | None = Relationship(back_populates="payments")

    __table_args__ = (UniqueConstraint("currency", "amount", "payment_mode", "user_id", "expense_id", "payment_date", name="unique_payment_constraint"),)
