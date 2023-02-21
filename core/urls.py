from django.urls import include, path
from core.router import router

from core.views import *

urlpatterns = [
    path("", include(router.urls)),
    path("get_periodo_active", get_periodo_active, name="get_periodo_active"),
    path("get_etapa_active", get_etapa_active, name="get_etapa_active"),
    path("get_periodos", get_periodos, name="get_periodos"),
    path("get_menu", get_menu, name="get_menu"),
    path("paths", paths, name="paths"),
    path("get_person_list", get_person_list, name="get_person_list"),

]
