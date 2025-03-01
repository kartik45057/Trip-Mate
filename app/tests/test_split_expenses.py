from app.enums import CurrencyCode
from app.models import Expense_Split_Exp, Payment_Split_Exp, User_Read_id_username
from app.thirdPartyApi.exchange_rates import get_exchange_rates
from app.util.split_expenses import Get_Display_Messages, Get_Equal_Share_Distribution

user1 = User_Read_id_username(**{
      "id": 1,
      "username": "kartik"
    }
)

user2 = User_Read_id_username(**{
      "id": 2,
      "username": "vatsal"
    }
)

user3 = User_Read_id_username(**{
      "id": 3,
      "username": "rajat"
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

payment3 = Payment_Split_Exp(**
    {
      "id": 3,
      "currency": "INR",
      "amount": 800,
      "user": user3
    },
)

payment4 = Payment_Split_Exp(**
    {
      "id": 4,
      "currency": "INR",
      "amount": 2400,
      "user": user1
    },
)

payment5 = Payment_Split_Exp(**
    {
      "id": 5,
      "currency": "USD",
      "amount": 20,
      "user": user3
    },
) 

expense1 = Expense_Split_Exp(**{
  "id": 2,
  "description": "Lunch day 1",
  "trip_id": 1,
  "users": [user1, user2, user3],
  "payments": [payment1, payment2]
})

expense2 = Expense_Split_Exp(**{
  "id": 2,
  "description": "Coffee day 1",
  "trip_id": 1,
  "users": [user1, user2, user3],
  "payments": [payment3]
})

expense3 = Expense_Split_Exp(**{
  "id": 3,
  "description": "Jet skiing day 1",
  "trip_id": 1,
  "users": [user1, user3],
  "payments": [payment4]
})

expense4 = Expense_Split_Exp(**{
  "id": 4,
  "description": "Drinks day 1",
  "trip_id": 1,
  "users": [user1, user2, user3],
  "payments": [payment5]
})

exchanges_rates_INR = get_exchange_rates()

def test_1():
    expenses = [expense1]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR)
    assert result == ['vatsal needs to give INR 33.33 to kartik', 'rajat needs to give INR 333.33 to kartik']

def test_2():
    expenses = [expense2]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR)
    assert result == ['kartik needs to give INR 266.67 to rajat', 'vatsal needs to give INR 266.67 to rajat']

def test_3():
    expenses = [expense3]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR)
    assert result == ['rajat needs to give INR 1200.0 to kartik']

def test_4():
    expenses = [expense1, expense2, expense3]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR)
    assert result == ['vatsal needs to give INR 100.0 to kartik', 'rajat needs to give INR 1200.0 to kartik', 'vatsal needs to give INR 200.0 to rajat']

def test_5():
    expenses = [expense1, expense2, expense3]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR, CurrencyCode.USD)
    assert result == ['vatsal needs to give USD 1.14 to kartik', 'rajat needs to give USD 13.68 to kartik', 'vatsal needs to give USD 2.28 to rajat']

def test_6():
    expenses = [expense4]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR)
    assert result == ['kartik needs to give INR 584.8 to rajat', 'vatsal needs to give INR 584.8 to rajat']

def test_7():
    expenses = [expense1, expense2, expense3, expense4]
    amount_to_be_received_and_from_by_userid, username_by_user_id = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    result = Get_Display_Messages(amount_to_be_received_and_from_by_userid, username_by_user_id, exchanges_rates_INR)
    assert result == ['vatsal needs to give INR 884.8 to rajat', 'rajat needs to give INR 715.2 to kartik']
