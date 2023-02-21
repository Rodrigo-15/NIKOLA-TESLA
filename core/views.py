from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core import urls_dict
from core.models import *
from core.serializers import *


def DefaultTemplate(request):
    return render(request, "index.html")


@api_view(["GET"])
def get_periodo_active(request):
    periodo = Periodo.get_periodo_activo()
    serializer = PeriodoSerializer(periodo)
    return Response(serializer.data)


@api_view(["GET"])
def get_periodos(request):
    periodos = Periodo.get_periodos()
    serializer = PeriodoSerializer(periodos, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_etapa_active(request):
    programa_id = request.GET.get("programa_id")
    periodo_id = request.GET.get("periodo_id")
    promocion = request.GET.get("promocion")
    etapa = Etapa.get_etapa_activo(programa_id, periodo_id, promocion)
    serializer = EtapaSerializer(etapa)
    return Response(serializer.data)

@api_view(['POST'])
def get_menu(request):
    if request.method == 'POST':
        data = request.data
        user = data.get('user')
        user_model = User.objects.get(id=user.get('id'))
        groups = user_model.groups.all()
        app = request.headers["app-name"]
        menu_obj = []
        for group in groups:
            menu = Menu.objects.filter(app__name=app, groups__id=group.id)
            serializer = MenuSerializer(menu, many=True)
            for menu in serializer.data:
                if menu not in menu_obj:
                    menu_obj.append(menu)
        return Response(menu_obj)

@api_view(["GET"])
def paths(request):
    return Response(urls_dict.urls_dict)