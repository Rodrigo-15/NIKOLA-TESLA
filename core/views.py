from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
from core.models import *
from core.serializers import *

def DefaultTemplate(request):
    return render(request, 'index.html')


@api_view(['GET'])
def get_periodo_active(request):
    periodo = Periodo.get_periodo_activo()
    serializer = PeriodoSerializer(periodo)
    return Response(serializer.data)

@api_view(['GET'])
def get_periodos(request):
    periodos = Periodo.get_periodos()
    serializer = PeriodoSerializer(periodos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_etapa_active(request):
    programa_id = request.GET.get('programa_id')
    periodo_id = request.GET.get('periodo_id')
    promocion = request.GET.get('promocion')
    etapa = Etapa.get_etapa_activo(programa_id,periodo_id,promocion)
    serializer = EtapaSerializer(etapa)
    return Response(serializer.data)