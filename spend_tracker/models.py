from django.db import models

from spendlog import settings


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True)
    rate = models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        return self.name


class DefaultCurrency(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class Unit(models.Model):
    UNIT_TYPE_CHOICES = [
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
        ("ACCOUNT", "Account"),
    ]

    name = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    in_balance = models.BooleanField(default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="units"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"], name="unique_unit_name_per_user"
            )
        ]

    def __str__(self):
        return f"{self.unit_type}: {self.name}"


class Transaction(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    source_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="source_transactions"
    )
    destination_unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="destination_transactions"
    )
    source_amount = models.DecimalField(max_digits=16, decimal_places=2)
    destination_amount = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
