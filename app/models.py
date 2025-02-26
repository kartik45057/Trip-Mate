from datetime import date, datetime
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.enums import CurrencyCode, PaymentMode

class User_Create(BaseModel):
    full_name: str = Field(min_length=2, max_length=50, description="User's full name")
    username: str = Field(min_length=3, max_length=15, description="Unique name for user")
    email: EmailStr = Field(description="User's Email id")
    password: str
    date_of_birth: date = Field(description="User's date of birth")

    @field_validator("password")
    def validate_password(cls, password):
        try:
            if len(password) < 8:
                 raise ValueError("Password length must atleast be 8")
            # 1. Check against common passwords (optional but recommended)
            # You can use a list of common passwords or an API for this.
            # Example (using a simple list - in real app, use a proper list):
            common_passwords = ["password123", "123456", "qwerty"]
            if password in common_passwords:
                raise ValueError("Password is too common. Choose a stronger password.")

            # 2. Meet complexity requirements (customize these rules):
            if not re.search(r"[a-z]", password):  # At least one lowercase
                raise ValueError("Password must contain at least one lowercase letter")
            if not re.search(r"[A-Z]", password):  # At least one uppercase
                raise ValueError("Password must contain at least one uppercase letter")
            if not re.search(r"[0-9]", password):  # At least one digit
                raise ValueError("Password must contain at least one digit")
            if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]", password): # At least one special character
                raise ValueError("Password must contain at least one special character")

            return password  # Validation successful
        except ValueError as e:
            raise ValueError(str(e))  # Re-raise the exception with the original message

class User_Read(BaseModel):
    id: int = Field(description="Unique identifier for the user")
    full_name: str = Field(min_length=2, max_length=50, description="User's full name")
    username: str = Field(min_length=2, max_length=50, description="Unique name for user")
    email: EmailStr = Field(description="User's Email id")
    date_of_birth: date = Field(description="User's date of birth")

class User_Read_id_username(BaseModel):
    id: int = Field(description="Unique identifier for the user")
    username: str = Field(min_length=2, max_length=50, description="Unique name for user")

class Payment_Create(BaseModel):
    currency: CurrencyCode = Field(description="The currency of the payment (allowed values: INR, USD, EUR)")
    amount: float = Field(description="The amount of the payment in the specified currency")
    payment_mode: PaymentMode = Field(description="The mode of the payment (allowed values: Cash, Credit Card, Debit Card, UPI etc)")
    payment_date: datetime = Field(default=None, description="Date and time of the payment")
    notes: Optional[str] = Field(default=None, max_length=100 ,description="Any notes related to the payment")
    user_id: int = Field(description="user id of user who has done the payment")
    expense_id: int

class Payment_Read(BaseModel):
    id: int = Field(description="Unique identifier for the payment")
    currency: CurrencyCode = Field(description="The currency of the payment (allowed values: INR, USD, EUR)")
    amount: float = Field(description="The amount of the payment in the specified currency")
    payment_mode: PaymentMode = Field(description="The mode of the payment (allowed values: Cash, Credit Card, Debit Card, UPI etc)")
    user: User_Read_id_username = Field(description="user who has done the payment")
    payment_date: datetime = Field(default=None, description="Date and time of the payment")
    notes: Optional[str] = Field(default=None, max_length=100 ,description="Any notes related to the payment")

class Payment_Read2(BaseModel):
    id: int = Field(description="Unique identifier for the payment")
    currency: CurrencyCode = Field(description="The currency of the payment (allowed values: INR, USD, EUR)")
    amount: float = Field(description="The amount of the payment in the specified currency")
    payment_mode: PaymentMode = Field(description="The mode of the payment (allowed values: Cash, Credit Card, Debit Card, UPI etc)")
    user: User_Read_id_username = Field(description="user who has done the payment")

class Payment_Read_basic(BaseModel):
    id: int = Field(description="Unique identifier for the payment")
    currency: CurrencyCode = Field(description="The currency of the payment (allowed values: INR, USD, EUR)")
    amount: float = Field(description="The amount of the payment in the specified currency")
    payment_mode: PaymentMode = Field(description="The mode of the payment (allowed values: Cash, Credit Card, Debit Card, UPI etc)")

class Payment_Read_without_user(BaseModel):
    id: int = Field(description="Unique identifier for the payment")
    currency: CurrencyCode = Field(description="The currency of the payment (allowed values: INR, USD, EUR)")
    amount: float = Field(description="The amount of the payment in the specified currency")
    payment_mode: PaymentMode = Field(description="The mode of the payment (allowed values: Cash, Credit Card, Debit Card, UPI etc)")
    payment_date: datetime = Field(default=None, description="Date and time of the payment")
    notes: Optional[str] = Field(default=None, max_length=100 ,description="Any notes related to the payment")

class Payment_Split_Exp(BaseModel):
    id: int = Field(description="Unique identifier for the payment")
    currency: CurrencyCode = Field(description="The currency of the payment (allowed values: INR, USD, EUR)")
    amount: float = Field(description="The amount of the payment in the specified currency")
    user: User_Read = Field(description="user who has done the payment")

class Expense_Create(BaseModel):
    description: Optional[str] = Field(default=None, min_length=10, max_length=100, description="Details of expense, eg: 2000 rupees spend for dinner at cafe")
    trip_id: int = Field(description="id of the trip this expense is part of")
    payments: List[Payment_Create] = Field(description="Stores the payments done as part of this expense which tells who has contributed how much in the total amount paid as part of this expense")
    users: List[int] = Field(description="List of ids of users between whom amount needs to be splitted")

class Expense_Read(BaseModel):
    id: int = Field(description="Unique identifier for the expense")
    description: Optional[str] = Field(default=None, min_length=10, max_length=100, description="Details of expense, eg: 2000 rupees spend for dinner at cafe")
    trip_id: int = Field(description="id of the trip this expense is part of")
    users: List[User_Read_id_username] = Field(description="List of users between whom amount needs to be splitted")
    payments: List[Payment_Read2] = Field(description="Payments done as a part of this expense")

class Expense_Read2(BaseModel):
    id: int = Field(description="Unique identifier for the expense")
    description: Optional[str] = Field(default=None, min_length=10, max_length=100, description="Details of expense, eg: 2000 rupees spend for dinner at cafe")
    trip_id: int = Field(description="id of the trip this expense is part of")
    payments: List[Payment_Read_basic] = Field(description="Payments done as a part of this expense")

class Expense_Split_Exp(BaseModel):
    id: int = Field(description="Unique identifier for the expense")
    trip_id: int = Field(description="id of the trip this expense is part of")
    description: Optional[str] = Field(default=None, min_length=10, max_length=100, description="Details of expense, eg: 2000 rupees spend for dinner at cafe")
    users: List[User_Read_id_username] = Field(description="List of users between whom amount needs to be splitted")
    payments: List[Payment_Split_Exp] = Field(description="Payments done as a part of this expense")

class Trip_Create(BaseModel):
    title: str = Field(min_length=3, max_length=50, description="Title of the trip")
    start_date: date = Field(description="Start date of the trip")
    end_date: Optional[date] = Field(default=None, description="End date of the trip")
    users: Optional[List[int]] = Field(default=[], description="ids of users who are part of the trip")

class Trip_Read(BaseModel):
    id: int = Field(description="Unique identifier for the trip")
    title: str = Field(min_length=3, max_length=50, description="Title of the trip")
    start_date: date = Field(description="Start date of the trip")
    end_date: Optional[date] = Field(default=None, description="End date of the trip")
    created_by: User_Read_id_username
    users: Optional[List[User_Read_id_username]] = Field(default=[], description="List of users who are part of the trip")

class Trip_Read2(BaseModel):
    id: int = Field(description="Unique identifier for the trip")
    title: str = Field(min_length=3, max_length=50, description="Title of the trip")
    start_date: date = Field(description="Start date of the trip")
    end_date: Optional[date] = Field(default=None, description="End date of the trip")
    created_by: User_Read
    users: Optional[List[User_Read]] = Field(default=[], description="List of users who are part of the trip")
    expenses: Optional[List[Expense_Read]] = Field(default=[], description="List of expenses that incurred during the trip")

class Trip_Read_basic(BaseModel):
    id: int = Field(description="Unique identifier for the trip")
    title: str = Field(min_length=3, max_length=50, description="Title of the trip")
    start_date: date = Field(description="Start date of the trip")
    end_date: Optional[date] = Field(default=None, description="End date of the trip")

class Token(BaseModel):
    access_token: str
    token_type: str
