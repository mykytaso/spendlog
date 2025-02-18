from spend_tracker.helpers.currencies import update_or_create_currencies_in_db

from celery import shared_task

from spend_tracker.helpers.monthly_reset import reset_income_expense_to_zero


@shared_task
def update_create_currencies() -> None:
    update_or_create_currencies_in_db()


@shared_task
def reset_units_to_zero() -> None:
    reset_income_expense_to_zero()
