from core.models import Area, Persona
from .models import Expediente, Tramite, SeguimientoTramite, RequisitoTramite
from rest_framework.response import Response
from .serializers import RequisitoTramiteSerializer, TramiteSerializer, PersonaSerializer
from rest_framework.decorators import api_view
from rest_framework import status

# Create your views here.


@api_view(['GET'])
def get_tramites(request):
    """Devuelve los tramites de la base de datos."""

    tramites = Tramite.objects.all()
    serializer = TramiteSerializer(tramites, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def generar_expediente(request):
    """Genera un expediente enlazado a un tramite respectivo."""

    try:
        data = request.data

        expediente = Expediente(is_activo=True)
        expediente.save()

        expediente_id = Expediente.get_last_expediente_id()

        persona = data['persona']
        persona_nombre = data['persona_nombre']
        documento_identidad = data['documento_identidad']
        tipo_tramite = data['tipo_tramite']
        asunto = data['asunto']
        usuario = data['usuario']
        sede = data['sede']

        area_derivacion = data['area_derivacion']

        save_tramite(expediente_id, persona, persona_nombre, documento_identidad,
                     tipo_tramite, asunto, usuario, sede, area_derivacion)
    except:
        print("[!] Error generando expediente.")
        return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_200_OK)


def save_tramite(expediente_id, persona, persona_nombre, documento_identidad, tipo_tramite, asunto, usuario, sede, area_derivacion):
    """Crea un tramite nuevo, lo inserta y lo añade a seguimiento con estado activo en la base de datos."""

    tramite = Tramite(expediente_id=expediente_id,
                      persona_id=persona, persona_nombre=persona_nombre, documento_identidad=documento_identidad, tipo_tramite_id=tipo_tramite, asunto=asunto, usuario_id=usuario, sede_id=sede)

    tramite.save()

    iniciar_seguimiento(
        tramite_id=Tramite.get_last_tramite_id(),  area_derivacion=area_derivacion)


def iniciar_seguimiento(tramite_id, area_derivacion):
    """Agrega un tramite a seguimiento con estado activo."""

    seguimiento = SeguimientoTramite(
        tramite_id=tramite_id, area_derivacion_id=area_derivacion, is_iniciado=True)

    seguimiento.save()


@api_view(['POST'])
def derivar_tramite(request):
    """Cambia el estado de seguimiento del tramite a is_revision=True y el area_derivacion si se especifica."""

    data = request.data

    tramite_id = data['tramite_id']
    area_derivacion = data['area_derivacion']

    if not area_derivacion:
        iniciar_revision(tramite_id=tramite_id)
    else:
        iniciar_revision(tramite_id=tramite_id,
                         area_derivacion=area_derivacion)

    return Response(status=status.HTTP_200_OK)


def iniciar_revision(tramite_id, area_derivacion=None):
    """Inicia la revision de un tramite y lo deriva a un area en especifico, sino se especifica area_derivacion se asigna el area_derivacion del ultimo seguimiento."""

    if not area_derivacion:
        area_derivacion = SeguimientoTramite.get_area_derivacion_by_tramite_id(
            tramite_id=tramite_id)

        seguimiento = SeguimientoTramite(
            tramite_id=tramite_id, area_derivacion=Area(area_derivacion), is_revision=True)

    else:
        seguimiento = SeguimientoTramite(
            tramite_id=tramite_id, area_derivacion=Area(area_derivacion), is_revision=True)

    seguimiento.save()


@api_view(['POST'])
def concluir_tramite(request):
    """Concluye el seguimiento de un tramite en especifico."""

    data = request.data

    tramite_id = data['tramite_id']
    concluir_seguimiento(tramite_id=tramite_id)

    return Response(status=status.HTTP_200_OK)


def concluir_seguimiento(tramite_id, area_derivacion=None):
    """Cambia el estado de seguimiento de un tramite a is_concluido=True"""

    area_derivacion = SeguimientoTramite.get_area_derivacion_by_tramite_id(
        tramite_id=tramite_id)

    seguimiento = SeguimientoTramite(
        tramite_id=tramite_id, area_derivacion=Area(area_derivacion), is_concluido=True)

    seguimiento.save()


@ api_view(['GET'])
def get_estudiante_by_dni(request):
    """Filtra estudiantes por numero_documento en específico."""

    dni = request.GET.get('dni')

    estudiante = Persona.objects.filter(
        numero_documento__exact=dni).first()

    if not estudiante:
        return Response({'message': 'Alumno no encontrado'}, status=404)

    serializer = PersonaSerializer(estudiante)
    return Response(serializer.data)


@ api_view(['GET'])
def get_requisito_tramite_by_desc(request):
    """Filtra requisitos de tramites por descripcion en especifica."""

    descripcion = request.GET.get('descripcion')

    requisito = RequisitoTramite.objects.filter(
        descripcion__exact=descripcion).first()

    if not requisito:
        return Response({'message': 'Requisito no encontrado'}, status=404)

    serializer = RequisitoTramiteSerializer(requisito)

    return Response(serializer.data)


@ api_view(['GET'])
def get_tramite_by_asunto(request):
    """Filtra tramites por un asunto en especifico."""

    asunto = request.GET.get('asunto')

    tramite = Tramite.objects.filter(asunto__exact=asunto)

    if not tramite:
        return Response({'message': 'Tramite no encontrado'}, status=404)

    serializer = TramiteSerializer(tramite, many=True)

    return Response(serializer.data)
