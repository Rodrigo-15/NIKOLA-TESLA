from django.urls import include, path

from desk.router import router
from desk.views import *

app_name = "desk"

urlpatterns = [
    path("", include(router.urls)),
    path("login/", login, name="login"),
]
