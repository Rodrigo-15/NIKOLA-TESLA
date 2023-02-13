from django.urls import include, path

from desk.router import router
from desk.views import (get_procedures, login, get_dashboard_procedures, get_tracings_procedures)

app_name = "desk"

urlpatterns = [
    path("", include(router.urls)),
    path("get_procedures", get_procedures, name="get_procedures"),
    path("get_tracings_procedures/<int:status>", get_tracings_procedures, name="get_tracings_procedures"),
    path("get_dashboard_procedures", get_dashboard_procedures, name="get_dashboard_procedures"),
    path("login/", login, name="login"),
]
