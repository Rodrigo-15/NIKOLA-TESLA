from django.urls import include, path

from desk.router import router
from desk.views import get_finished_procedures, get_inprocess_procedures, get_procedures, get_started_procedures, login

app_name = "desk"

urlpatterns = [
    path("", include(router.urls)),
    path("get_procedures", get_procedures, name="get_procedures"),
    path("get_finished_procedures", get_finished_procedures, name="get_finished_procedures"),
    path("login/", login, name="login"),
]
