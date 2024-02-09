from functools import reduce
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core import urls_dict
from core.models import *
from core.serializers import *
from django.db.models import Q


def DefaultTemplate(request):
    return render(request, "index.html")


@api_view(["GET"])
def get_periodo_active(request):
    periodo = Periodo.get_periodo_activo()
    serializer = PeriodoSerializer(periodo)
    return Response(serializer.data)


@api_view(["GET"])
def get_periodos(request):
    periodos = Periodo.get_periodos().order_by("nombre")
    serializer = PeriodoSerializer(periodos, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_etapa_active(request):
    programa_id = request.GET.get("programa_id")
    promocion = request.GET.get("promocion")
    etapa = Etapa.get_etapa_activo(programa_id, promocion)
    serializer = EtapaSerializer(etapa)
    return Response(serializer.data)


@api_view(["POST"])
def get_menu(request):
    if request.method == "POST":
        data = request.data
        user = data.get("user")
        user_model = User.objects.get(id=user.get("id"))
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


@api_view(["POST"])
def get_person_list(request):
    if request.method == "POST":
        query = request.data.get("query")
        persons = []
        legalperson = []

        if query.isdigit():
            persons = Persona.objects.filter(numero_documento=query)[:10]
            if not persons:
                legalperson = PersonaJuridica.objects.filter(ruc=query)[:10]
        else:
            query = query.upper()
            persons = Persona.objects.filter(full_name__contains=query)[:10]
            if not persons:
                legalperson = PersonaJuridica.objects.filter(razon_social__contains=query)[:10]

        if not persons and  not legalperson:
            return Response([])
        if persons:
            serializer = PersonListSerializer(persons, many=True)
            return Response(serializer.data)
        else:
            serializer = PersonaJuridicaSerializer(legalperson, many=True)
            return Response(serializer.data)


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_profile_image(request):
    if request.method == "POST":
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        person = Persona.objects.get(user=user)
        foto = request.FILES.get("foto")
        if not foto:
            return Response({"message": "No se ha enviado ninguna imagen"}, status=400)
        person.foto = foto
        person.save()
        return Response({"message": "Imagen de perfil actualizada"}, status=200)


@api_view(["GET"])
def get_periodo_etapa_active(request):
    from admision.models import Expediente

    expediente_id = request.GET.get("expediente_id")
    is_academico = request.GET.get("is_academico")
    if is_academico:
        is_academico = True
    else:
        is_academico = False

    programa = Expediente.objects.filter(id=expediente_id, is_active=True).values(
        "programa_id", "promocion"
    )
    periodo = Periodo.get_periodo_by_etapa_active(
        programa[0]["programa_id"], programa[0]["promocion"], is_academico
    )
    serializer = PeriodoSerializer(periodo)
    return Response(serializer.data)
