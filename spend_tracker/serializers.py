from django.db import models
from rest_framework import serializers

from spend_tracker.helpers.currencies import convert_currencies
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

    # Reorder currency choices so the default currency appears first
    def __init__(self, *args, **kwargs):
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

    # Shows only units which belong to user
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            user_units = Unit.objects.filter(user=request.user).order_by("unit_type")
            self.fields["source_unit"].queryset = user_units
            self.fields["destination_unit"].queryset = user_units

    def validate(self, data):
        """Validates and processes transaction data by ensuring either the source or
        destination amount is provided and calculates the missing value if necessary."""
        source_amount = data.get("source_amount")
        source_currency = data.get("source_unit").currency
        destination_amount = data.get("destination_amount")
        destination_currency = data.get("destination_unit").currency

        if data.get("destination_amount") is None and data.get("source_amount") is None:
            raise serializers.ValidationError(
                "You must specify a destination or source amount"
            )

        if source_amount and destination_amount is None:
            data["destination_amount"] = convert_currencies(
                amount=source_amount,
                from_currency=source_currency,
                to_currency=destination_currency,
            )
        elif destination_amount and source_amount is None:
            data["source_amount"] = convert_currencies(
                amount=destination_amount,
                from_currency=destination_currency,
                to_currency=source_currency,
            )
        return data


class TransactionListSerializer(TransactionSerializer):
    date_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    user = serializers.StringRelatedField()
    source_unit = serializers.StringRelatedField()
    destination_unit = serializers.StringRelatedField()
