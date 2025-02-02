from spend_tracker.models import Currency

from celery import shared_task


@shared_task
def count_currencies() -> int:
    return Currency.objects.count()
