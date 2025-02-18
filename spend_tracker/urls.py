from django.urls import path, include
from rest_framework import routers

from spend_tracker.views import (
    CurrencyViewSet,
    UnitViewSet,
    TransactionViewSet,
    DefaultCurrencyViewSet,
)

app_name = "spend_tracker"

router = routers.DefaultRouter()
router.register("currency", CurrencyViewSet, basename="currency")
router.register("unit", UnitViewSet, basename="unit")
router.register("transaction", TransactionViewSet, basename="transaction")
router.register("default-currency", DefaultCurrencyViewSet, basename="default-currency")

urlpatterns = [
    path("", include(router.urls)),
]
