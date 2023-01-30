from django.urls import include, path

from desk.router import router
from desk.views import get_procedures, create_procedure, login

app_name = "desk"

urlpatterns = [
    path("", include(router.urls)),
    path("get_procedures", get_procedures, name="get_procedures"),
    path("create_procedure/", create_procedure, name="create_procedure"),
    path("login/", login, name="login"),
]
