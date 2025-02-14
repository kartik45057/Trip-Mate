from fastapi import HTTPException
import requests

def get_exchange_rates():
    exchange_rates = {}
    base_currency = "INR"
    url = f'https://api.exchangerate-api.com/v4/latest/{base_currency}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "rates" in data:
            exchange_rates = data.get("rates")
        return exchange_rates
    else:
        raise HTTPException(status_code=500, detail="Something Went Wrong")
   
if __name__ == "__main__":  
    get_exchange_rates()