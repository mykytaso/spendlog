from spend_tracker.helpers.currencies import update_or_create_currencies_in_db

from celery import shared_task


@shared_task
def update_create_currencies() -> None:
    update_or_create_currencies_in_db()
