import decimal
import os
from datetime import datetime

import requests

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
    currencies_from_api = response.json().get("rates", None)
    return currencies_from_api


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

    if not (len(from_currency) == len(to_currency) == 3):
        return decimal.Decimal(0)

    from_currency_upper = from_currency.upper()
    to_currency_upper = to_currency.upper()

    rates = get_currencies_from_api()

    if not rates or from_currency_upper not in rates or to_currency_upper not in rates:
        return decimal.Decimal(0)

    rate = decimal.Decimal(rates[to_currency_upper] / rates[from_currency_upper])
    return round(amount * rate, 3)
