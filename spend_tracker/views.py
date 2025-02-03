from django.db import transaction
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from spend_tracker.models import Currency, Unit, Transaction, DefaultCurrency
from spend_tracker.serializers import (
    CurrencySerializer,
    TransactionSerializer,
    UnitListSerializer,
    UnitSerializer,
    TransactionListSerializer,
    DefaultCurrencySerializer,
    DefaultCurrencyListSerializer,
)


class CurrencyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class DefaultCurrencyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = DefaultCurrency.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        return (
            DefaultCurrencyListSerializer
            if self.action == "list"
            else DefaultCurrencySerializer
        )

    def perform_create(self, serializer):
        instance, created = DefaultCurrency.objects.update_or_create(
            user=self.request.user,
            defaults=serializer.validated_data,
        )
        serializer.instance = instance


class UnitViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Unit.objects.all()
        unit_type = self.request.query_params.get("unit_type")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if unit_type:
            queryset = queryset.filter(type=unit_type.upper())

        return queryset.order_by("unit_type")

    def get_serializer_class(self):
        return UnitListSerializer if self.action == "list" else UnitSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Transaction.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset.order_by("date_time")

    def get_serializer_class(self):
        return (
            TransactionListSerializer
            if self.action == "list"
            else TransactionSerializer
        )

    @transaction.atomic
    def perform_create(self, serializer):

        data = serializer.validated_data

        source_unit = Unit.objects.get(pk=data["source_unit"].id)
        destination_unit = Unit.objects.get(pk=data["destination_unit"].id)

        # Operation for INCOME -> ACCOUNT
        if (
            source_unit.unit_type == "INCOME"
            and destination_unit.unit_type == "ACCOUNT"
        ):
            source_unit.amount += data["source_amount"]
            destination_unit.amount += data["destination_amount"]

        # Operation for ACCOUNT -> ACCOUNT/EXPENSE
        elif source_unit.unit_type == "ACCOUNT" and destination_unit.unit_type in (
            "ACCOUNT",
            "EXPENSE",
        ):
            source_unit.amount -= data["source_amount"]
            destination_unit.amount += data["destination_amount"]

        else:
            raise ValidationError("Invalid transaction type combination.")

        source_unit.save()
        destination_unit.save()

        serializer.save(user=self.request.user)

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.source_unit.unit_type == "INCOME":
            instance.source_unit.amount -= instance.source_amount
            instance.destination_unit.amount -= instance.destination_amount
        else:
            instance.source_unit.amount += instance.source_amount
            instance.destination_unit.amount -= instance.destination_amount

        instance.source_unit.save()
        instance.destination_unit.save()
        instance.delete()
