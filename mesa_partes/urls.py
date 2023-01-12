from django.urls import path, include
from .router import router
from .views import *

app_name = "mesa_partes"


urlpatterns = [
    path("", include(router.urls)),
    path("get_tramites/", get_tramites, name="get_tramites"),
    path("generar_expediente/", generar_expediente, name="generar_expediente"),
    path("get_estudiante_by_dni/", get_estudiante_by_dni,
         name="get_estudiante_by_dni"),
    path("get_requisito_tramite_by_desc/", get_requisito_tramite_by_desc,
         name="get_requisito_tramite_by_desc"),
    path("get_tramite_by_asunto/", get_tramite_by_asunto,
         name="get_tramite_by_asunto"),
    path("derivar_tramite/", derivar_tramite, name="derivar_tramite"),
    path("concluir_tramite/", concluir_tramite, name="concluir_tramite")
]
