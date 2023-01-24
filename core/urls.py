from django.urls import path

from core.views import *

urlpatterns = [
    path('get_periodo_active', get_periodo_active, name='get_periodo_active'),
    path('get_etapa_active', get_etapa_active, name='get_etapa_active'),
    path('get_periodos', get_periodos, name='get_periodos'),
    path('get_menus', get_menus, name='get_menus'),
    path("paths", paths, name="paths"),
]
