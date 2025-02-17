from app.enums import CurrencyCode
from app.models import Expense_Read
from app.thirdPartyApi.exchange_rates import get_exchange_rates


def Distribute_Amounts(expenses, split_between, exchanges_rates_INR):
    no_of_users = len(split_between)
    amount_paid_by_user_id = {}
    total_amount_paid_during_trip = 0

    # Calculate the amounts paid by each user in this group of expenses
    for expense in expenses:
        if expense.payments:
            payments = expense.payments
            for payment in payments:
                user_id = payment.user_id
                amount_paid_by_user = payment.amount
                currency = payment.currency
                if not currency == CurrencyCode.INR:
                    if currency in exchanges_rates_INR:
                      exchange_rate = exchanges_rates_INR[currency]
                      amount_paid_by_user = amount_paid_by_user / exchange_rate
                    else:
                        raise Exception(f"The {currency} to INR exchange rate is unavailable.")

                total_amount_paid_during_trip += amount_paid_by_user
                if user_id in amount_paid_by_user_id:
                    amount_paid_by_user_id[user_id] += amount_paid_by_user
                else:
                    amount_paid_by_user_id[user_id] = amount_paid_by_user

    # Calculate the fair share for each user
    equal_share = total_amount_paid_during_trip / no_of_users

    # Calculate how much each user needs to be paid or received based on how much more or less they have spend compared to equal share
    amount_to_be_given_or_received_by_user_id = {}
    for user_id in split_between:
        amount_paid = amount_paid_by_user_id[user_id] if user_id in amount_paid_by_user_id else 0
        diff = amount_paid - equal_share
        if diff >= 0:
            amount_to_be_given_or_received_by_user_id[user_id] = {"receive":diff, "give":0.0}
        else:
            amount_to_be_given_or_received_by_user_id[user_id] = {"receive":0.0, "give":-(diff)}

    # Identify the way by which amount can be distributed equally
    amount_to_be_received_and_from_by_userid = {}
    for user_id in amount_to_be_given_or_received_by_user_id:
        amount_needs_to_be_received = amount_to_be_given_or_received_by_user_id[user_id]["receive"] if user_id in amount_to_be_given_or_received_by_user_id and "receive" in amount_to_be_given_or_received_by_user_id[user_id] else 0
        for temp_user_id in amount_to_be_given_or_received_by_user_id:
            if amount_needs_to_be_received > 0:
                if temp_user_id != user_id:
                    amount_needs_to_be_given = amount_to_be_given_or_received_by_user_id[temp_user_id]["give"] if temp_user_id in amount_to_be_given_or_received_by_user_id and "give" in amount_to_be_given_or_received_by_user_id[temp_user_id] else 0
                    if amount_needs_to_be_given > 0:
                        transfer = min(amount_needs_to_be_received, amount_needs_to_be_given)
                        if transfer > 0:
                            amount_needs_to_be_received -= transfer
                            amount_to_be_given_or_received_by_user_id[user_id]["receive"] -= transfer
                            amount_to_be_given_or_received_by_user_id[temp_user_id]["give"] -= transfer
                            if user_id in amount_to_be_received_and_from_by_userid:
                                amount_to_be_received_and_from_by_userid[user_id][temp_user_id] = transfer
                            else:
                                amount_to_be_received_and_from_by_userid[user_id] = {temp_user_id: transfer}
            else:
                break

    return amount_to_be_received_and_from_by_userid

def Get_Display_Messages(amount_to_be_received_and_from_by_userid):
    display_messages = []
    for user_receiving_amount in amount_to_be_received_and_from_by_userid:
        for user_giving_amount in amount_to_be_received_and_from_by_userid[user_receiving_amount]:
            amount = round(amount_to_be_received_and_from_by_userid[user_receiving_amount][user_giving_amount], 2)
            currency = "INR"
            msg = f"{user_giving_amount} needs to give {currency} {amount} to {user_receiving_amount}"
            display_messages.append(msg)
    return display_messages

def Get_Equal_Share_Distribution(expenses, exchanges_rates_INR):
    split_between_by_expenses = {}
    for expense in expenses:
        split_between = expense.users
        if not split_between:
            continue

        split_between = list(map(lambda user: user.id, split_between))
        split_between.sort()
        split_between = tuple(split_between)
        if split_between in split_between_by_expenses:
            split_between_by_expenses[split_between].append(expense)
        else:
            split_between_by_expenses[split_between] = [expense]

    amount_to_be_received_from_by_userid_from_multiple_grp_of_expenses = []
    for split_between in split_between_by_expenses:
        expenses = split_between_by_expenses[split_between]
        amount_to_be_received_from_by_userid = Distribute_Amounts(expenses, split_between, exchanges_rates_INR)
        amount_to_be_received_from_by_userid_from_multiple_grp_of_expenses.append(amount_to_be_received_from_by_userid)

    #amount_to_be_received_from_by_userid_from_multiple_grp_of_expenses  = [{'user1': {'user3': 850.0}, 'user2': {'user3': 1000.0}}, {'user3': {'user1': 1000.0}, 'user2': {'user1': 1000.0}}, {'user1': {'user2': 2500.0}}]
    merged_dict = {}
    for amount_to_be_received_from_by_userid in amount_to_be_received_from_by_userid_from_multiple_grp_of_expenses:
        for user_id in amount_to_be_received_from_by_userid:
            if user_id in merged_dict:
                for temp_user_id in amount_to_be_received_from_by_userid[user_id]:
                    if temp_user_id in merged_dict[user_id]:
                        merged_dict[user_id][temp_user_id] += amount_to_be_received_from_by_userid[user_id][temp_user_id]
                    else:
                        merged_dict[user_id][temp_user_id] = amount_to_be_received_from_by_userid[user_id][temp_user_id] 
            else:
                merged_dict[user_id] = amount_to_be_received_from_by_userid[user_id]

    merged_dict_keys = list(merged_dict.keys())
    for user_to_be_paid in merged_dict_keys:
        users_to_pay_user_to_be_paid = list(merged_dict[user_to_be_paid].keys()) if user_to_be_paid in merged_dict else []
        for user_that_needs_to_pay in users_to_pay_user_to_be_paid:
            if user_that_needs_to_pay in merged_dict and merged_dict[user_that_needs_to_pay] and user_to_be_paid in merged_dict[user_that_needs_to_pay]:
                diff = merged_dict[user_to_be_paid][user_that_needs_to_pay] - merged_dict[user_that_needs_to_pay][user_to_be_paid]
                if diff > 0:
                    merged_dict[user_to_be_paid][user_that_needs_to_pay] = diff
                    merged_dict[user_that_needs_to_pay].pop(user_to_be_paid)
                    if len(merged_dict[user_that_needs_to_pay]) <= 0:
                        merged_dict.pop(user_that_needs_to_pay)
                elif diff < 0:
                    merged_dict[user_that_needs_to_pay][user_to_be_paid] = -(diff)
                    merged_dict[user_to_be_paid].pop(user_that_needs_to_pay)
                    if len(merged_dict[user_to_be_paid]) <= 0:
                        merged_dict.pop(user_to_be_paid)
                else:
                    merged_dict[user_that_needs_to_pay].pop(user_to_be_paid)
                    merged_dict[user_to_be_paid].pop(user_that_needs_to_pay)
                    if len(merged_dict[user_that_needs_to_pay]) <= 0:
                        merged_dict.pop(user_that_needs_to_pay)
                    if len(merged_dict[user_to_be_paid]) <= 0:
                        merged_dict.pop(user_to_be_paid)

    return merged_dict



expenses = [Expense_Read(**{
  "id": 2,
  "description": "dinner day 2",
  "amount": 1000,
  "trip_id": 1,
  "users": [
    {
      "id": 2,
      "name": "kartik singh",
      "email": "kartiksingh@gmail.com",
      "date_of_birth": "2001-04-07"
    },
    {
      "id": 3,
      "name": "vatsal mishra",
      "email": "vatsalmishra@gmail.com",
      "date_of_birth": "2000-07-12"
    }
  ],
  "payments": [
    {
      "id": 1,
      "currency": "INR",
      "amount": 700,
      "payment_mode": "Cash",
      "user_id": 2,
      "user": {
        "id": 2,
        "name": "kartik singh",
        "email": "kartiksingh@gmail.com",
        "date_of_birth": "2001-04-07"
      }
    },
    {
      "id": 2,
      "currency": "USD",
      "amount": 300,
      "payment_mode": "Cash",
      "user_id": 3,
      "user": {
        "id": 3,
        "name": "vatsal mishra",
        "email": "vatsalmishra@gmail.com",
        "date_of_birth": "2000-07-12"
      }
    }
  ]
})]

if __name__ == "__main__":
    exchanges_rates_INR = get_exchange_rates()
    result = Get_Equal_Share_Distribution(expenses, exchanges_rates_INR)
    print(Get_Display_Messages(result))
