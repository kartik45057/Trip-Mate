

from app.models import Expense_Split_Exp, User_Read, Payment_Split_Exp
from app.thirdPartyApi.exchange_rates import get_exchange_rates
from app.util.split_expenses import Get_Display_Messages, Get_Equal_Share_Distribution

user1 = User_Read(**{
      "id": 1,
      "name": "kartik singh",
      "email": "kartiksingh@gmail.com",
      "date_of_birth": "2001-04-06"
    }
)

user2 = User_Read(**{
      "id": 2,
      "name": "vatsal mishra",
      "email": "vatsalmishra@gmail.com",
      "date_of_birth": "2000-07-12"
    }
)

user3 = User_Read(**{
      "id": 3,
      "name": "rajat nigam",
      "email": "rajat@gmail.com",
      "date_of_birth": "1997-07-12"
    }
)

payment1 = Payment_Split_Exp(**
    {
      "id": 1,
      "currency": "INR",
      "amount": 700,
      "user": user1
    },
)

payment2 = Payment_Split_Exp(**
    {
      "id": 2,
      "currency": "INR",
      "amount": 300,
      "user": user2
    },
)

expenses1 = [Expense_Split_Exp(**{
  "id": 2,
  "description": "Lunch day 1",
  "trip_id": 1,
  "users": [user1, user2],
  "payments": [payment1, payment2]
})]

exchanges_rates_INR = get_exchange_rates()

def test_1():
    amount_to_be_received_and_from_by_userid = Get_Equal_Share_Distribution(expenses1, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid)
    assert result == ['2 needs to give INR 200.0 to 1']
    