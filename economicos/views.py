import datetime
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Sum


@api_view(["POST"])
def pago_generate(request, id_pago):
    if id_pago == None:
        data_pago = request.data
        numero_documento = data_pago["numero_documento"]
        nombre_cliente = data_pago["nombre_cliente"]
        numero_operacion = data_pago["numero_operacion"]
        fecha_operacion = data_pago["fecha_operacion"]
        concepto = data_pago["concepto"]
        monto = data_pago["monto"]
        concepto = Concepto.get_concepto_by_id(concepto)
        new_pago = Pago(
            numero_documento=numero_documento,
            nombre_cliente=nombre_cliente,
            numero_operacion=numero_operacion,
            fecha_operacion=fecha_operacion,
            concepto=concepto,
            is_active=True,
            monto=monto,
        )

        expediente = Expediente.get_expediente_by_numero_documento(numero_documento)

        if len(expediente) == 1:
            expediente = expediente.first()
            new_pago.expendiente = expediente
    else:
        data_pago = request.data
        new_pago = Pago.objects.get(pk=id_pago)
        new_pago.numero_documento = data_pago["numero_documento"]
        new_pago.nombre_cliente = data_pago["nombre_cliente"]
        new_pago.numero_operacion = data_pago["numero_operacion"]
        new_pago.fecha_operacion = data_pago["fecha_operacion"]
        concepto = data_pago["concepto"]
        concepto_INSTANCE = Concepto.get_concepto_by_id(concepto)
        new_pago.concepto = concepto_INSTANCE
        new_pago.monto = data_pago["monto"]

        expediente = Expediente.get_expediente_by_numero_documento(
            data_pago["numero_documento"]
        )

        if len(expediente) == 1:
            expediente = expediente.first()
            new_pago.expendiente = expediente

    new_pago.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def import_pagos(request):
    if request.method == "POST":
        data_nueva = []
        data_existente = []
        data = request.data
        for pago in data:
            try:
                pago_existente = Pago.objects.filter(
                    numero_operacion=pago["numero_operacion"],
                    numero_documento=pago["numero_documento"],
                )

                if len(pago_existente) > 0:
                    data_existente.append(pago)
                else:
                    data_nueva.append(pago)
            except:
                data_nueva.append(pago)

        for pago in data_nueva:
            numero_documento = pago["numero_documento"]
            nombre_cliente = pago["nombre_cliente"]
            numero_operacion = pago["numero_operacion"]
            fecha_operacion = pago["fecha_operacion"]
            concepto = pago["concepto"]
            monto = pago["monto"]
            concepto = Concepto.get_concepto_by_id(concepto)
            new_pago = Pago(
                numero_documento=numero_documento,
                nombre_cliente=nombre_cliente,
                numero_operacion=numero_operacion,
                fecha_operacion=fecha_operacion,
                concepto=concepto,
                is_active=True,
                monto=monto,
            )

            expediente = Expediente.get_expediente_by_numero_documento(numero_documento)

            if len(expediente) == 1:
                expediente = expediente.first()
                new_pago.expendiente = expediente

            new_pago.save()

        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def conciliar_pagos(request):
    if request.method == "POST":
        data = request.data

        for pago in data:
            numero_operacion = pago["numero_operacion"]
            numero_conciliacion = pago["numero_conciliacion"]

            pago_obj = Pago.objects.filter(numero_operacion=numero_operacion).first()
            if pago_obj:
                pago_obj.is_conciliado = True
                pago_obj.numero_conciliacion = numero_conciliacion
                pago_obj.save()

        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def filter_pago(request):
    if request.method == "GET":
        search = request.GET.get("search", "")
        if search == "":
            pagos = Pago.objects.filter(
                Q(nombre_cliente__icontains=search)
                | Q(numero_operacion__icontains=search)
                | Q(numero_documento__icontains=search)
                | Q(concepto__nombre__icontains=search)
            )[:25]
        else:
            pagos = Pago.objects.filter(
                Q(nombre_cliente__icontains=search)
                | Q(numero_operacion__icontains=search)
                | Q(numero_documento__icontains=search)
                | Q(concepto__nombre__icontains=search)
            )
        pagos_serializer = PagoSerializerFilter(pagos, many=True)
        return Response(pagos_serializer.data)


@api_view(["GET"])
def filter_pago_sin_conciliar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            search = request.GET.get("search", "")
            pagos = Pago.objects.filter(
                Q(nombre_cliente__icontains=search)
                | Q(numero_operacion__icontains=search)
                | Q(numero_documento__icontains=search)
                | Q(concepto__nombre__icontains=search)
            ).filter(is_conciliado=False)[:25]
            pagos_serializer = PagoSerializerFilter(pagos, many=True)
            return Response(pagos_serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def get_dashboard(request):
    if request.method == "GET":
        fecha_actual = datetime.datetime.now()
        total_pagos_anio = Pago.get_pagos_by_anio(fecha_actual.year).aggregate(
            Sum("monto")
        )["monto__sum"]
        total_pagos_mes = Pago.get_pagos_by_anio_and_mes(
            fecha_actual.year, fecha_actual.month
        ).aggregate(Sum("monto"))["monto__sum"]
        cantidad_pagos_por_conciliar = Pago.get_pagos_sin_conciliar().count()
        pagos_del_dia_list = Pago.get_pagos_del_dia(fecha_actual.day - 1)
        pagos_serializer = PagoSerializerFilter(pagos_del_dia_list[:50], many=True)

        return Response(
            {
                "total_pagos_anio": total_pagos_anio,
                "total_pagos_mes": total_pagos_mes,
                "cantidad_pagos_por_conciliar": cantidad_pagos_por_conciliar,
                "pagos_del_dia_list": pagos_serializer.data,
            }
        )
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
def save_pago(request):
    if request.method == "PUT":
        data = request.data
        pago_obj = Pago.objects.filter(
            numero_operacion=data["numero_operacion"],
            numero_documento=data["numero_documento"],
            fecha_operacion=data["fecha_operacion"],
        ).first()

        if pago_obj:
            pago_obj.nombre_cliente = data["nombre_cliente"]
            pago_obj.concepto_id = data["concepto_id"]
            pago_obj.expendiente_id = data["expediente_id"]
            pago_obj.is_validado = True
            pago_obj.adjunto = data["adjunto"]
            pago_obj.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
