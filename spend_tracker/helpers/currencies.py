import os

import requests

from spend_tracker.models import Currency


url = os.environ.get("EXCHANGE_RATES_API_URL")
access_key = os.environ.get("EXCHANGE_RATES_API_ACCESS_KEY")


def get_currencies_from_api() -> dict | None:
    response = requests.get(url, params={"access_key": access_key})
    currencies_from_api = response.json().get("rates", None)
    return currencies_from_api


def update_or_create_currencies_in_db() -> None:
    currencies_from_api = get_currencies_from_api()
    if currencies_from_api:
        for currency_name, currency_rate in currencies_from_api.items():
            Currency.objects.update_or_create(
                name=currency_name, defaults={"rate": currency_rate}
            )


def convert_currencies(from_currency, to_currency, amount):

    if not (len(from_currency) == len(to_currency) == 3):
        return 0

    from_currency_upper = from_currency.upper()
    to_currency_upper = to_currency.upper()

    rates = get_currencies_from_api()

    if not rates or from_currency_upper not in rates or to_currency_upper not in rates:
        return 0

    rate = rates[to_currency_upper] / rates[from_currency_upper]
    return round(amount * rate, 3)
