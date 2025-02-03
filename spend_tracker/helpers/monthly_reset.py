from spend_tracker.models import Unit


def reset_income_expense_to_zero():
    units = Unit.objects.filter(unit_type__in=("INCOME", "EXPENSE"))
    units.update(amount=0)
