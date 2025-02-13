import decimal
import os
from datetime import datetime

import requests
from rest_framework.exceptions import ValidationError

from spend_tracker.helpers.telegram import send_telegram_message
from spend_tracker.models import Currency
from dotenv import load_dotenv


load_dotenv()


url = os.getenv("EXCHANGE_RATES_API_URL")
access_key = os.getenv("EXCHANGE_RATES_API_ACCESS_KEY")


def get_currencies_from_api() -> dict | None:
    response = requests.get(url, params={"access_key": access_key})
    if response.status_code != 200:
        return None
    return response.json().get("rates", None)


def update_or_create_currencies_in_db() -> None:
    currencies_from_api = get_currencies_from_api()
    if currencies_from_api:
        for currency_name, currency_rate in currencies_from_api.items():
            Currency.objects.update_or_create(
                name=currency_name, defaults={"rate": currency_rate}
            )
        send_telegram_message(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nCurrencies Updated"
        )
    else:
        send_telegram_message(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nCurrencies NOT Updated"
        )


def convert_currencies(
    from_currency: str, to_currency: str, amount: decimal.Decimal
) -> decimal.Decimal:
    rates = get_currencies_from_api()
    if not rates or from_currency not in rates or to_currency not in rates:
        raise ValidationError(f"Currency convertion failed")
    target_rate = decimal.Decimal(rates[to_currency] / rates[from_currency])
    return amount * target_rate
