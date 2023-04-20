from django.urls import path
from .views import *

urlpatterns = [
    path("reporte-economico-alumno-api/", reporte_economico_alumno_api,
         name="reporte-economico-alumno-api"),
    path("get_reporte_matricula_pdf/", get_reporte_matricula_pdf,
         name="get_reporte_matricula_pdf"),
    path("get-reporte-ingresos-api/", get_reporte_ingresos_api,
         name="get-reporte-ingresos-api"),
    path("get-reporte-programas-api/", get_reporte_programas_api,
         name="get-reporte-programas-api"),
    path('get_reporte_programas_excel/', get_reporte_programas_excel,
         name='get_reporte_programas_excel'),
    path("reporte_programa_function/", reporte_programa_function,
         name="reporte_programa_function"),
    path("get_reporte_actanotas_pdf/", get_reporte_actanotas_pdf,
         name="get_reporte_actanotas_pdf"),
    path("get_reporte_economico_alumno_pdf/", get_reporte_economico_alumno_pdf,
         name="get_reporte_economico_alumno_pdf"),
    path("get_reporte_academico_alumno_pdf/", get_reporte_academico_alumno_pdf,
         name="get_reporte_academico_alumno_pdf"),
    path("get_process_tracking_sheet_pdf/", get_process_tracking_sheet_pdf,
         name="get_process_tracking_sheet_pdf"),
]
