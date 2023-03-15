from core.serializers import PersonSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from desk.NAMES import APP_NAME
from desk.models import File, Procedure
from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.serializers import GroupSerializer, UserSerializer
from core.models import Apps, Menu, Persona


from desk.serializers import ProcedureListSerializer, ProcedureSerializer
from core.decorators import check_app_name, check_credentials
from core.models import Persona, CargoArea
from desk.models import Procedure, ProcedureTracing
from desk.serializers import (
    ProcedureSerializer,
    ProcedureTracingSerializer,
    ProcedureTracingsList,
)

# Create your views here.


@check_app_name(APP_NAME)
@api_view(["GET"])
def get_procedures(request):
    if request.method == "GET":
        data = request.query_params
        STATES = ["started", "in_progress", "finished"]
        params = ["date", "code_number", "state"]
        if not all(param in data for param in params):
            return Response(
                "Missing parameters: " + str(params),
                status=status.HTTP_400_BAD_REQUEST,
            )

        date = data["date"]
        code_number = data["code_number"]
        state = data["state"]
        if state not in STATES:
            return Response(
                "Invalid state: " + str(STATES),
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        counters = { 
            "total": 0,
            "count": 0,
            "label": "0/0",
        }
        procedures = []
        if state == "started":
            procedures = get_started_procedures()
        elif state == "in_progress":
            procedures = get_in_progress_procedures()
        else:
            procedures = get_finished_procedures()
            

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in procedures]
        )

        counters["total"] = len(procedures)

        if date:
            procedures = procedures.filter(created_at__icontains=date)

        if code_number:
            procedures = procedures.filter(code_number__icontains=code_number)

        if not date and not code_number:
            procedures = procedures.order_by("-created_at")[:20]

        serializer = ProcedureListSerializer(procedures, many=True)

        counters["count"] = len(serializer.data)
        counters["label"] = f"{counters['count']}/{counters['total']}"
        
        return Response({"procedures": serializer.data, "counters": counters})


@api_view(["POST"])
@check_app_name()
@check_credentials()
def login(request):
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        app_name = request.headers["app-name"]

        try:
            user = User.objects.get(username=email, is_active=True)
        except Exception:
            return Response(
                "User does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            groups = user.groups.all()

            app = Apps.objects.filter(name=app_name).first()
            menu = Menu.objects.filter(app=app).first()

            is_group_valid_app = False
            for group in groups:
                if group in menu.groups.all():
                    is_group_valid_app = True
                    break

            if not is_group_valid_app:
                return Response(
                    "User does not have permission",
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            person = Persona.objects.get(user_id=user.id)
            headquarter = CargoArea.objects.filter(persona_id=person.id).values("headquarter_id","headquarter__name" ).first()
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "groups": GroupSerializer(groups, many=True).data,
                    "token": token.key,
                    "person": PersonSerializer(person).data,
                    "headquarter" : headquarter
                }
            )
        else:
            return Response(
                "User does not have permission",
                status=status.HTTP_401_UNAUTHORIZED,
            )


def get_started_procedures():
    """Get Procedures that have just one TracingProcedure and it is not finished"""

    procedure_tracings = ProcedureTracing.objects.filter(
        is_finished=False,
        procedure_id__in=ProcedureTracing.objects.values("procedure_id")
        .annotate(count=Count("procedure_id"))
        .filter(count=1)
        .values("procedure_id"),
    )
    serializer = ProcedureTracingSerializer(procedure_tracings, many=True)

    return serializer.data


def get_in_progress_procedures():
    """Get Procedures that have more than one TracingProcedure and it is not finished"""

    procedure_tracings = ProcedureTracing.objects.filter(
        is_finished=False,
        procedure_id__in=ProcedureTracing.objects.values("procedure_id")
        .annotate(count=Count("procedure_id"))
        .filter(count__gt=1)
        .values("procedure_id"),
    )
    serializer = ProcedureTracingSerializer(procedure_tracings, many=True)

    return serializer.data


def get_finished_procedures():
    """Get Procedures with TracingProcedure finished"""

    procedure_tracings = ProcedureTracing.objects.filter(is_finished=True)
    serializer = ProcedureTracingSerializer(procedure_tracings, many=True)

    return serializer.data


@api_view(["GET"])
def get_dashboard_procedures(request):
    """Get count of procedures"""

    if request.method == "GET":
        procedure_started_tracings = ProcedureTracing.objects.filter(
            procedure_id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count=1)
            .values("procedure_id")
        ).count()
        procedure_in_progress_tracings = (
            ProcedureTracing.objects.filter(
                is_finished=False,
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count__gt=1)
                .values("procedure_id"),
            )
            .distinct("procedure_id")
            .count()
        )
        procedure_fished = (
            ProcedureTracing.objects.filter(is_finished=True)
            .distinct("procedure_id")
            .count()
        )
        return Response(
            {
                "started": procedure_started_tracings,
                "in_progress": procedure_in_progress_tracings,
                "finished": procedure_fished,
            }
        )


@api_view(["GET"])
def get_tracings_procedures(request, status):
    if request.method == "GET":
        if status == 0:
            procedures = {"started": get_started_procedures()}
        if status == 1:
            procedures = {"in_process": get_in_process_procedures()}
        if status == 2:
            procedures = {"finished": get_finished_procedures()}

        return Response(procedures)


@api_view(["POST"])
def save_procedure(request):
    if request.method == "POST":
        person_id = request.data["person_id"]
        subject = request.data["subject"]
        description = (
            request.data["description"] if "description" in request.data else ""
        )
        procedure_type_id = request.data["procedure_type_id"]
        reference_doc_number = (
            request.data["reference_doc_number"]
            if "reference_doc_number" in request.data
            else ""
        )

        user_id = request.data["user_id"]
        headquarter = (
            CargoArea.objects.filter(persona__user_id=user_id)
            .values("headquarter_id")
            .first()
        )
        headquarter_id = headquarter["headquarter_id"]
        if not headquarter:
            headquarter_id = 1
        area_user = CargoArea.objects.filter(persona__user_id=user_id).first()
        file = File.objects.filter(person_id=person_id).first()

        if not file:
            file = File.objects.create(person_id=person_id)
        procedure = Procedure.objects.create(
            file_id=file.id,
            subject=subject,
            description=description,
            procedure_type_id=procedure_type_id,
            reference_doc_number=reference_doc_number,
            headquarter_id=headquarter_id,
            user_id=user_id,
        )

        ProcedureTracing.objects.create(
            procedure_id=procedure.id,
            from_area_id=area_user.area_id if area_user else None,
            user_id=user_id,
        )

        return Response(
            status=status.HTTP_200_OK, data={"code_number": procedure.code_number}
        )


@api_view(["POST"])
def get_procedure_and_tracing_by_id(request):
    if request.method == "POST":
        procedure_id = request.data["procedure_id"]

        procedure = Procedure.objects.filter(id=procedure_id).first()
        procedure_tracings = ProcedureTracing.objects.filter(
            procedure_id=procedure_id
        ).order_by("-created_at")

        serializer_procedure = ProcedureSerializer(procedure)
        serializer_procedure_tracings = ProcedureTracingsList(
            procedure_tracings, many=True
        )

        return Response(
            {
                "procedure": {
                    "id": procedure.id,
                    "file_id": procedure.file_id,
                    "person": procedure.file.person.get_full_name(),
                    "person_document": procedure.file.person.numero_documento,
                    "code_number": procedure.code_number,
                    "procedure_type_id": procedure.procedure_type_id,
                    "procedure_type": procedure.procedure_type.description,
                    "subject": procedure.subject,
                    "description": procedure.description,
                    "reference_doc_number": procedure.reference_doc_number,
                    "headquarter_id": procedure.headquarter_id,
                    "headquarter": procedure.headquarter.name,
                    "user_id": procedure.user_id,
                    "user": procedure.user.username,
                    "created_at": serializer_procedure.data["created_at"],
                    "updated_at": serializer_procedure.data["updated_at"],
                },
                "procedure_tracings": serializer_procedure_tracings.data,
            }
        )
    
@api_view(["GET"])
def years_for_procedures(request):
    if request.method == "GET":
        years = Procedure.objects.values("created_at__year").distinct()
        years = [year["created_at__year"] for year in years]
        return Response(years)