from rest_framework.routers import DefaultRouter
from mesa_partes.viewsets import *

router = DefaultRouter()

router.register("tramite", TramiteViewSet)
