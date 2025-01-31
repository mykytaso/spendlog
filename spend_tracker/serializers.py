from django.db import models
from rest_framework import serializers

from spend_tracker.models import Currency, Unit, Transaction, DefaultCurrency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ("id", "name", "rate")


class DefaultCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultCurrency
        fields = ("id", "default_currency", "user")
        read_only_fields = ("user",)


class DefaultCurrencyListSerializer(DefaultCurrencySerializer):
    default_currency = serializers.StringRelatedField()
    user = serializers.StringRelatedField()


class UnitSerializer(serializers.ModelSerializer):
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),  # This will be overridden in `__init__`
        required=False,
    )

    class Meta:
        model = Unit
        fields = ("id", "name", "amount", "unit_type", "currency", "in_balance", "user")
        read_only_fields = ("user",)

    def __init__(self, *args, **kwargs):
        """Reorder currency choices so the default currency appears first"""
        super().__init__(*args, **kwargs)

        user = self.context["request"].user
        default_currency = DefaultCurrency.objects.filter(user=user).first()

        if default_currency:
            self.fields["currency"].queryset = Currency.objects.order_by(
                models.Case(
                    models.When(id=default_currency.default_currency.id, then=0),
                    default=1,
                    output_field=models.IntegerField(),
                )
            )


class UnitListSerializer(UnitSerializer):
    currency = serializers.StringRelatedField()
    user = serializers.StringRelatedField()


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "date_time",
            "source_unit",
            "destination_unit",
            "source_amount",
            "destination_amount",
            "user",
        )
        read_only_fields = ("user",)

    # If destination_amount is not provided, set it equal to source_amount
    def validate(self, data):
        if "destination_amount" not in data or data["destination_amount"] is None:
            data["destination_amount"] = data.get("source_amount", 0)
        return data


class TransactionListSerializer(TransactionSerializer):
    user = serializers.StringRelatedField()
    source_unit = serializers.StringRelatedField()
    destination_unit = serializers.StringRelatedField()
