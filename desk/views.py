from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.serializers import GroupSerializer, UserSerializer
from core.decorators import check_app_name, check_credentials
from core.models import Persona
from desk.models import Procedure, ProcedureTracing
from desk.serializers import ProcedureSerializer, ProcedureTracingSerializer

# Create your views here.


@api_view(["POST"])
def get_procedures(request):
    if request.method == "POST":
        data = request.data
        date = data["date"]
        user_id = data["user_id"]
        code_number = data["code_number"]
        if user_id == "":
            procedures = Procedure.objects.filter(
                Q(created_at__icontains=date) | Q(code_number__icontains=code_number)
            )
        else:
            procedures = Procedure.objects.filter(
                Q(created_at__icontains=date) | Q(code_number__icontains=code_number),
                user_id=user_id,
            )
        serilaizer = ProcedureSerializer(procedures, many=True)
        return Response(serilaizer.data)


@api_view(["POST"])
@check_app_name()
@check_credentials()
def login(request):
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        app_name = request.headers["app-name"]

        try:
            user = User.objects.get(email=email, is_active=True)
        except Exception:
            return Response(
                "User does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            groups = user.groups.all()

            if app_name == "desk":
                if (
                    not groups.filter(name="usuario").exists()
                    or not groups.filter(name="admin").exists()
                ):
                    return Response(
                        "User without required permissions",
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                person = Persona.objects.get(correo=user.email)

                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "groups": GroupSerializer(groups, many=True).data,
                        "token": token.key,
                        "person_id": person.id,
                        "person_name": person.get_full_name(),
                    }
                )
        else:
            return Response(
                "Incorrect password",
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["GET"])
def get_started_procedures(request):
    """Get procedures that have only one tracing and it is not finished"""

    if request.method == "GET":

        procedure_tracings = ProcedureTracing.objects.filter(
            procedure_id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count=1)
            .values("procedure_id")
        )

        serializer = ProcedureTracingSerializer(procedure_tracings, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def get_inprocess_procedures(request):
    """Get procedures that have more than one tracing and it is not finished"""

    if request.method == "GET":

        procedure_tracings = ProcedureTracing.objects.filter(
            procedure_id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count__gt=1)
            .values("procedure_id")
        )

        serializer = ProcedureTracingSerializer(procedure_tracings, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def get_finished_procedures(request):
    """Get finished procedures"""

    if request.method == "GET":
        procedure_tracings = ProcedureTracing.objects.filter(is_finished=True)
        serializer = ProcedureTracingSerializer(procedure_tracings, many=True)
        return Response(serializer.data)
