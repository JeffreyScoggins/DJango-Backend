from django.urls import include, path
from .views import me, change_password

urlpatterns = [
    path("me/", me),
    path("change-password/", change_password),
    path("api/", include("cart.urls")),
]
