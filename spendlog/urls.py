from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("users.urls", namespace="user")),
    path("api/spend-tracker/", include("spend_tracker.urls", namespace="money")),
]
