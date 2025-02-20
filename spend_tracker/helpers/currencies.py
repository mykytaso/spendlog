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
    """Fetches currency exchange rates from an external API."""
    response = requests.get(url, params={"access_key": access_key})
    if response.status_code != 200:
        return None
    return response.json().get("rates", None)


def update_or_create_currencies_in_db() -> None:
    """Fetches currency rates from an external API and updates or creates currency records in the database."""
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
    amount: decimal.Decimal, from_currency: Currency, to_currency: Currency
) -> decimal.Decimal:
    """Converts a monetary amount from one currency to another.
    If the source and target currencies are the same, the original amount is returned.
    """
    if from_currency == to_currency:
        return amount
    return amount * (to_currency.rate / from_currency.rate)
