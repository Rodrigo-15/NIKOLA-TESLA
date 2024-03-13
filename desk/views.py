from rest_framework.permissions import IsAuthenticated
from backend.settings import URL_LOCAL, URL_PROD
from core.serializers import (
    CargoAreaSerializer,
    PersonSerializer,
    AreaSerializer,
    CargoAreaPersonSerializer,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view
from desk.NAMES import APP_NAME
from desk.models import File, Procedure
from django.contrib.auth.models import User
from django.db.models import Count, Q, Subquery, OuterRef
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.serializers import GroupSerializer, UserSerializer
from core.models import Apps, Menu, Persona, Area


from desk.serializers import ProcedureListSerializer, ProcedureSerializer
from core.decorators import check_app_name, check_is_auth, check_credentials
from core.models import Persona, CargoArea
from desk.models import (
    Procedure,
    ProcedureTracing,
    Procedure_ProcReq,
    ProcedureRequirement,
    Anexo,
    ProcedureCharge,
)
from desk.serializers import (
    ProcedureSerializer,
    ProcedureTracingSerializer,
    ProcedureTracingsList,
    AnexoListSerializer,
    ProcedureChargeSerializer,
)

from core.pagination import CustomPagination
from django.db.models.functions import TruncDate


# Create your views here.
@check_app_name(APP_NAME)
@api_view(["GET"])
def get_procedures_a(request):
    if request.method == "GET":
        user = request.user
        persona = Persona.objects.filter(user=user).first()
        if not persona:
            return Response(
                "User not found",
                status=status.HTTP_400_BAD_REQUEST,
            )
        cargo_area = CargoArea.objects.filter(persona=persona)
        if not cargo_area:
            return Response(
                "CargoArea not found",
                status=status.HTTP_400_BAD_REQUEST,
            )

        area = [area1.area_id for area1 in cargo_area]
        # area=cargo_area.area
        user_id = user.id
        #
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
        counters = get_counters_procedure(date, code_number, area, user_id)

        procedures = []

        if state == "started":
            procedures = get_started_procedures()
        elif state == "in_progress":
            procedures = get_in_progress_procedures(user_id)
        else:
            procedures = get_finished_procedures()

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in procedures]
        )

        procedures = get_filter_procedures_by_area(procedures, area)

        if date:
            procedures = procedures.filter(created_at__icontains=date)

        if code_number:
            procedures = procedures.filter(code_number__icontains=code_number)

        procedures = procedures.order_by("-created_at")[:20]

        serializer = ProcedureListSerializer(procedures, many=True)

        return Response({"procedures": serializer.data, "counters": counters})


def get_counters_procedure(date=None, code_number=None, area=None, user_id=None):
    counters = {
        "started": {
            "label": "",
            "total": 0,
            "count": 0,
        },
        "in_progress": {
            "label": "",
            "total": 0,
            "count": 0,
        },
        "finished": {
            "label": "",
            "total": 0,
            "count": 0,
        },
    }

    procedures_started = []
    procedures_in_progress = []
    procedures_finished = []

    procedures_started = get_started_procedures()
    procedures_started = Procedure.objects.filter(
        id__in=[procedure["procedure"] for procedure in procedures_started]
    )
    procedures_started = get_filter_procedures_by_area(procedures_started, area)
    counters["started"]["total"] = len(procedures_started)

    procedures_in_progress = get_in_progress_procedures(user_id)
    procedures_in_progress = Procedure.objects.filter(
        id__in=[procedure["procedure"] for procedure in procedures_in_progress]
    )
    procedures_in_progress = get_filter_procedures_by_area(procedures_in_progress, area)
    counters["in_progress"]["total"] = len(procedures_in_progress)

    procedures_finished = get_finished_procedures()
    procedures_finished = Procedure.objects.filter(
        id__in=[procedure["procedure"] for procedure in procedures_finished]
    )
    procedures_finished = get_filter_procedures_by_area(procedures_finished, area)
    counters["finished"]["total"] = len(procedures_finished)

    if date:
        procedures_started = procedures_started.filter(created_at__icontains=date)
        procedures_in_progress = procedures_in_progress.filter(
            created_at__icontains=date
        )
        procedures_finished = procedures_finished.filter(created_at__icontains=date)

    if code_number:
        procedures_started = procedures_started.filter(
            code_number__icontains=code_number
        )
        procedures_in_progress = procedures_in_progress.filter(
            code_number__icontains=code_number
        )
        procedures_finished = procedures_finished.filter(
            code_number__icontains=code_number
        )

    serializer_started = ProcedureListSerializer(procedures_started, many=True)
    serializer_in_progress = ProcedureListSerializer(procedures_in_progress, many=True)
    serializer_finished = ProcedureListSerializer(procedures_finished, many=True)

    counters["started"]["count"] = len(serializer_started.data)
    counters["in_progress"]["count"] = len(serializer_in_progress.data)
    counters["finished"]["count"] = len(serializer_finished.data)

    if date:
        counters["started"][
            "label"
        ] = f"{counters['started']['count']}/{counters['started']['total']}"
        counters["in_progress"][
            "label"
        ] = f"{counters['in_progress']['count']}/{counters['in_progress']['total']}"
        counters["finished"][
            "label"
        ] = f"{counters['finished']['count']}/{counters['finished']['total']}"
    elif code_number and len(code_number) > 5:
        counters["started"][
            "label"
        ] = f"{counters['started']['count']}/{counters['started']['total']}"
        counters["in_progress"][
            "label"
        ] = f"{counters['in_progress']['count']}/{counters['in_progress']['total']}"
        counters["finished"][
            "label"
        ] = f"{counters['finished']['count']}/{counters['finished']['total']}"
    else:
        counters["started"]["label"] = f"{counters['started']['total']}"
        counters["in_progress"]["label"] = f"{counters['in_progress']['total']}"
        counters["finished"]["label"] = f"{counters['finished']['total']}"

    return counters


def get_filter_procedures_by_area(procedures, area):
    if not area:
        procedures_trackings = ProcedureTracing.objects.filter(
            Q(from_area=area) | Q(to_area=area)
        )
    else:
        procedures_trackings = ProcedureTracing.objects.filter(from_area_id__in=area)
    procedure_ids_in_trackings = procedures_trackings.values_list(
        "procedure", flat=True
    )
    procedures = procedures.filter(id__in=procedure_ids_in_trackings)
    return procedures


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


def get_in_progress_procedures(user_id=None):
    """Get Procedures that have more than one TracingProcedure and it is not finished"""
    area_id = CargoArea.objects.filter(persona__user_id=user_id)
    area_id = [area.area_id for area in area_id]
    procedure_tracings = ProcedureTracing.objects.filter(
        is_finished=False,
        from_area_id__in=area_id,
        to_area_id__isnull=True,
        user_id=user_id,
    ).exclude(
        procedure_id__in=ProcedureTracing.objects.filter(is_finished=True).values(
            "procedure_id"
        ),
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
        counters = get_counters_procedure()

        procedures_started = counters.get("started").get("count")
        procedures_in_progress = counters.get("in_progress").get("count")
        procedures_finished = counters.get("finished").get("count")

        return Response(
            {
                "started": procedures_started,
                "in_progress": procedures_in_progress,
                "finished": procedures_finished,
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


@api_view(["GET"])
def years_for_procedures(request):
    if request.method == "GET":
        years = Procedure.objects.values("created_at__year").distinct()
        years = [year["created_at__year"] for year in years]
        return Response(years)


@api_view(["GET"])
@check_is_auth()
def get_user_profile(request):
    if request.method == "GET":
        user_id = request.user.id
        user = User.objects.filter(id=user_id).first()
        groups = user.groups.all()
        person = Persona.objects.get(user_id=user.id)
        headquarter = (
            CargoArea.objects.filter(persona_id=person.id)
            .values("headquarter_id", "headquarter__name")
            .first()
        )
        person_data = PersonSerializer(person).data
        from backend.settings import DEBUG, URL_LOCAL, URL_PROD

        url = URL_LOCAL if DEBUG else URL_PROD
        path = person_data["foto"]
        if path:
            path = path.replace("/media", "media")
            person_data["foto"] = url + path

        cargo_area = CargoArea.objects.filter(persona=person).first()
        if not cargo_area:
            area = {}
        area = AreaSerializer(cargo_area.area).data

        return Response(
            {
                "user": UserSerializer(user).data,
                "groups": GroupSerializer(groups, many=True).data,
                "person": person_data,
                "headquarter": headquarter,
                "area": area,
            }
        )


# new modification
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
            headquarter = (
                CargoArea.objects.filter(persona_id=person.id)
                .values("headquarter_id", "headquarter__name")
                .first()
            )
            person_data = PersonSerializer(person).data
            from backend.settings import DEBUG, URL_LOCAL, URL_PROD

            url = URL_LOCAL if DEBUG else URL_PROD
            path = person_data["foto"]
            if path:
                path = path.replace("/media", "media")
                person_data["foto"] = url + path

            cargo_area = CargoArea.objects.filter(persona=person).first()
            if not cargo_area:
                areas = []
            data_area = cargo_area.area.all()
            areas = AreaSerializer(data_area, many=True).data
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "groups": GroupSerializer(groups, many=True).data,
                    "token": token.key,
                    "person": person_data,
                    "headquarter": headquarter,
                    "area": areas,
                }
            )
        else:
            return Response(
                "User does not have permission",
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["GET"])
def get_procedures(request):
    if request.method == "GET":

        query = request.GET.get("query")
        date = request.GET.get("date")

        procedure_tracings = ProcedureTracing.objects.filter()

        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = (
            procedures.filter(
                Q(code_number__icontains=query)
                | Q(subject__icontains=query)
                | Q(file__person__full_name__icontains=query)
                | Q(file__area__nombre__icontains=query)
                | Q(file__legalperson__razon_social__icontains=query)
                | Q(file__person__numero_documento__icontains=query)
                | Q(file__legalperson__numero_documento__icontains=query),
                **({"created_at__date": date} if date else {}),
            )
            .annotate(created_at_date=TruncDate("created_at"))
            .order_by("-code_number")
        )
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_procedures_in_started(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")

        procedure_tracings = ProcedureTracing.objects.filter(
            is_finished=False,
            procedure_id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count=1)
            .values("procedure_id"),
        )

        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
            user_id=user_id,
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_procedures_in_assigned(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            areas = []
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data
        procedure_tracings = (
            ProcedureTracing.objects.filter(
                is_finished=False,
                is_approved=False,
                from_area_id__in=[area["id"] for area in areas],
                to_area_id__isnull=True,
                user_id=user_id,
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True
                ).values("procedure_id")
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count=1)
                .values("procedure_id"),
            )
            .exclude(
                id__lt=Subquery(
                    ProcedureTracing.objects.filter(
                        user_id=user_id, procedure_id=OuterRef("procedure_id")
                    )
                    .order_by("-id")
                    .values("id")[:1]
                )
            )
        )
        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_procedures_for_user(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        date = request.GET.get("date")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            return Response(
                "CargoArea not found",
                status=status.HTTP_400_BAD_REQUEST,
            )
        data_area = cargo_area.area.all()
        area_id = [area.id for area in data_area]

        procedure_tracings = ProcedureTracing.objects.filter(
            is_finished=False,
            from_area_id__in=area_id,
            user_id=user_id,
        )
        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = (
            procedures.filter(
                Q(code_number__icontains=query)
                | Q(subject__icontains=query)
                | Q(file__person__full_name__icontains=query)
                | Q(file__area__nombre__icontains=query)
                | Q(file__legalperson__razon_social__icontains=query)
                | Q(file__person__numero_documento__icontains=query)
                | Q(file__legalperson__numero_documento__icontains=query),
                **({"created_at__date": date} if date else {}),
            )
            .annotate(created_at_date=TruncDate("created_at"))
            .order_by("-code_number")
        )
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_procedure_by_id(request, procedure_id):
    if request.method == "GET":
        procedure = Procedure.objects.filter(id=procedure_id).first()
        data = ProcedureSerializer(procedure).data
        return Response(data)


@api_view(["GET"])
def get_procedure_and_tracing_by_id(request):
    if request.method == "GET":
        procedure_id = request.GET.get("procedure_id")

        procedure = Procedure.objects.filter(id=procedure_id).first()
        anexos = Anexo.objects.filter(procedure_id=procedure_id)
        procedure_tracings = ProcedureTracing.objects.filter(
            procedure_id=procedure_id
        ).order_by("-created_at")

        serializer_procedure = ProcedureSerializer(procedure)
        serializer_anexo = AnexoListSerializer(anexos, many=True)
        serializer_procedure_tracings = ProcedureTracingsList(
            procedure_tracings, many=True
        )

        return Response(
            {
                "procedure": serializer_procedure.data,
                "anexos": serializer_anexo.data,
                "procedure_tracings": serializer_procedure_tracings.data,
            }
        )


@api_view(["GET"])
def get_areas(request):
    if request.method == "GET":
        areas = Area.objects.filter(is_active=True)
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def get_user_for_area(request):
    if request.method == "POST":
        area_id = request.data["area_id"]
        users = CargoArea.objects.filter(area__id=area_id)
        serializer = CargoAreaPersonSerializer(users, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def save_procedure(request):
    if request.method == "POST":
        person_id = request.data["person_id"]
        subject = request.data["subject"]
        type_person = request.data["type_person"]
        description = (
            request.data["description"] if "description" in request.data else ""
        )
        attached_files = request.FILES.get("attached_files")
        procedure_type_id = request.data["procedure_type_id"]
        for_the_area_id = (
            request.data["for_the_area_id"]
            if "for_the_area_id" in request.data
            else None
        )
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

        number_of_sheets = request.data["number_of_sheets"]
        if not number_of_sheets:
            number_of_sheets = 0

        area_id = request.data["area_id"]

        if type_person == "0":
            file = File.objects.filter(area_id=area_id).first()
            if not file:
                File.objects.create(area_id=area_id)
        elif type_person == "1":
            file = File.objects.filter(person_id=person_id).first()
            if not file:
                File.objects.create(person_id=person_id)
        elif type_person == "2":
            file = File.objects.filter(legalperson_id=person_id).first()
            if not file:
                File.objects.create(legalperson_id=person_id)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Tipo de persona no valido"},
            )

        procedure = Procedure.objects.create(
            file_id=file.id,
            subject=subject,
            description=description,
            attached_files=attached_files,
            procedure_type_id=procedure_type_id,
            reference_doc_number=reference_doc_number,
            headquarter_id=headquarter_id,
            user_id=user_id,
            number_of_sheets=number_of_sheets,
            for_the_area_id=for_the_area_id,
        )

        ProcedureTracing.objects.create(
            procedure_id=procedure.id,
            from_area_id=area_id if area_id else None,
            user_id=user_id,
        )

        return Response(
            status=status.HTTP_200_OK, data={"code_number": procedure.code_number}
        )


@api_view(["POST"])
def update_procedure(request):
    if request.method == "POST":
        try:
            procedure_id = request.data["procedure_id"]
            subject = request.data["subject"]
            description = request.data["description"]
            attached_files = request.FILES.get("attached_files")
            reference_doc_number = request.data["reference_doc_number"]
            for_the_area_id = request.data["for_the_area_id"]
            number_of_sheets = request.data["number_of_sheets"]
            person_id = request.data["person_id"]
            type_person = request.data["type_person"]
            area_id = request.data["area_id"]
            procedure_type_id = request.data["procedure_type_id"]

        except KeyError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": "Fields are missing",
                    "fields": [
                        "procedure_id",
                        "subject",
                        "description",
                        "reference_doc_number",
                        "number_of_sheets",
                        "person_id",
                        "type_person",
                        "area_id",
                        "procedure_type_id",
                    ],
                },
            )

        procedure = Procedure.objects.filter(id=procedure_id).first()

        if not procedure:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "message": "No se encontró el procedimiento o no tiene permisos para editarlo"
                },
            )

        if type_person == "0":
            file = File.objects.filter(area_id=area_id).first()
            if not file:
                File.objects.create(area_id=area_id)
        elif type_person == "1":
            file = File.objects.filter(person_id=person_id).first()
            if not file:
                File.objects.create(person_id=person_id)
        elif type_person == "2":
            file = File.objects.filter(legalperson_id=person_id).first()
            if not file:
                File.objects.create(legalperson_id=person_id)
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Tipo de persona no valido"},
            )

        procedure.subject = subject
        procedure.description = description
        procedure.file_id = file.id
        procedure.procedure_type_id = procedure_type_id
        if attached_files:
            procedure.attached_files = attached_files
        procedure.reference_doc_number = reference_doc_number

        procedure.number_of_sheets = number_of_sheets
        procedure.for_the_area_id = for_the_area_id
        procedure.save()

        data = ProcedureSerializer(procedure).data

        return Response(status=status.HTTP_200_OK, data=data)


@api_view(["POST"])
def save_derive_procedure(request):
    if request.method == "POST":
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        number_of_sheets = (
            request.data["number_of_sheets"]
            if "number_of_sheets" in request.data
            else 0
        )
        document_response = request.FILES.get("document_response")
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )
        to_area_id = request.data["to_area_id"]
        action = request.data["action"]
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        assigned_user_id = request.data["assigned_user_id"]
        if assigned_user_id == "0":
            assigned_user_id = None

        procedure_tracing = (
            ProcedureTracing.objects.filter(
                is_approved=False, procedure_id=procedure_id
            )
            .exclude(to_area_id=None)
            .first()
        )

        if procedure_tracing:
            return Response(
                status=status.HTTP_202_ACCEPTED,
                data={
                    "message": "El tramite esta pendiente de aprobación por favor revise su bandeja de entrada"
                },
            )

        procedure = Procedure.objects.filter(id=procedure_id).first()
        procedure.number_of_sheets = number_of_sheets
        procedure.save()

        if assigned_user_id != None:
            ProcedureTracing.objects.create(
                procedure_id=procedure_id,
                from_area_id=from_area_id,
                to_area_id=to_area_id,
                user_id=user_id,
                action=action,
                assigned_user_id=assigned_user_id,
                ref_procedure_tracking_id=ref_procedure_tracking_id,
                document_response=document_response,
            )

            return Response(status=status.HTTP_200_OK)

        else:
            ProcedureTracing.objects.create(
                procedure_id=procedure_id,
                from_area_id=from_area_id,
                to_area_id=to_area_id,
                user_id=user_id,
                action=action,
                ref_procedure_tracking_id=ref_procedure_tracking_id,
                document_response=document_response,
            )

            return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_tracings_to_approved_for_area(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            areas = []
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data
        if not areas:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El usuario no tiene un area asignada"},
            )
        area_id = [area["id"] for area in areas]
        tracings_for_area = ProcedureTracing.objects.filter(
            to_area_id__in=area_id, is_approved=False, assigned_user_id=None
        ).order_by("-created_at")
        proceduretracing = ProcedureTracingSerializer(tracings_for_area, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_tracings_to_approved_for_user(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            areas = []
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data
        if not areas:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El usuario no tiene un area asignada"},
            )
        area_id = [area["id"] for area in areas]
        tracings_for_user = ProcedureTracing.objects.filter(
            to_area_id__in=area_id, assigned_user_id=user_id, is_approved=False
        ).order_by("-created_at")

        proceduretracing = ProcedureTracingSerializer(tracings_for_user, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
            user_id=user_id,
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
def approve_tracing(request):
    if request.method == "POST":
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        tracing_id = (
            ProcedureTracing.objects.filter(
                procedure_id=procedure_id, is_approved=False
            )
            .last()
            .id
        )
        ProcedureTracing.objects.filter(id=tracing_id).update(is_approved=True)

        from_area_id = ProcedureTracing.objects.filter(id=tracing_id).first().to_area_id
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )

        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
        )

        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def finally_procedure(request):
    if request.method == "POST":
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )
        action = request.data["action"]
        document_response = request.FILES.get("document_response")
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            action=action,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_finished=True,
            document_response=document_response,
        )

        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def get_procedures_requirements(request):
    if request.method == "POST":
        procedure_type_id = request.data["procedure_type_id"]
        requirements = Procedure_ProcReq.objects.filter(
            procedure_type_id=procedure_type_id, is_active=True
        )
        obj_requirements = []
        for r in requirements:
            requirement = ProcedureRequirement.objects.filter(
                id=r.requirement_id
            ).values("id", "description")
            obj_requirements.append(requirement[0])
        return Response(obj_requirements)


@api_view(["GET"])
def get_procedures_finished(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            areas = []
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El usuario no tiene un area asignada"},
            )
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data
        area_id = [area["id"] for area in areas]
        tracings_for_area = (
            ProcedureTracing.objects.filter(
                from_area_id__in=area_id, is_archived=False, is_finished=True
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True, is_archived=True
                ).values("procedure_id")
            )
            .order_by("-created_at")
        )
        proceduretracing = ProcedureTracingSerializer(tracings_for_area, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
        ).order_by("-code_number")

        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
def archive_procedure(request):
    if request.method == "POST":
        procedure_id = request.data["procedure_id"]
        user_id = request.data["user_id"]
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_archived=True,
            is_finished=True,
        )
        code_number = Procedure.objects.filter(id=procedure_id).first().code_number

        return Response(status=status.HTTP_200_OK, data={"code_number": code_number})


@api_view(["POST"])
def anexar_procedure(request):
    if request.method == "POST":
        procedure_id = request.data["procedure_id"]
        anexo_id = request.data["anexo_id"]
        user_id = request.data["user_id"]

        if not anexo_id or not procedure_id:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El anexo no existe"},
            )
        # crear el anexo
        anexo = Anexo.objects.create(
            procedure_id=procedure_id,
            procedure_anexo_id=anexo_id,
        )
        if not anexo:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "No se pudo crear el anexo"},
            )
        # finalizar el tramite anexado
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=anexo_id).last().from_area_id
        )
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=anexo_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=anexo_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_finished=True,
            is_anexed=True,
        )
        # mensaje anexo el tramite principal
        from_area_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .last()
            .from_area_id
        )
        ref_procedure_tracking_id = (
            ProcedureTracing.objects.filter(procedure_id=procedure_id).last().id
        )
        ProcedureTracing.objects.create(
            procedure_id=procedure_id,
            from_area_id=from_area_id,
            user_id=user_id,
            ref_procedure_tracking_id=ref_procedure_tracking_id,
            is_anexed=True,
        )

        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_procedures_charges(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        date = request.GET.get("date")

        procededure_charge = ProcedureCharge.objects.filter(
            user_id=user_id,
        )
        procededure_charge = (
            procededure_charge.filter(
                Q(correlative__icontains=query),
                **({"created_at__date": date} if date else {}),
            )
            .annotate(created_at_date=TruncDate("created_at"))
            .order_by("-correlative")
        )
        paginator = CustomPagination()
        paginated_procedures_charge = paginator.paginate_queryset(
            procededure_charge, request
        )
        serializer = ProcedureChargeSerializer(paginated_procedures_charge, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_procedures_derivations(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id")
        query = request.GET.get("query")
        date = request.GET.get("date")
        cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()
        if not cargo_area:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "El usuario no tiene un area asignada"},
            )
        data_area = cargo_area.area.all()
        areas = AreaSerializer(data_area, many=True).data

        trackins = (
            ProcedureTracing.objects.filter(
                user_id=user_id,
                from_area_id__in=[area["id"] for area in areas],
                to_area_id__isnull=False,
                procedure_charge__isnull=True,
                is_finished=False,
                is_archived=False,
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.filter(
                    is_finished=True,
                ).values("procedure_id")
            )
            .exclude(
                procedure_id__in=ProcedureTracing.objects.values("procedure_id")
                .annotate(count=Count("procedure_id"))
                .filter(count=1)
                .values("procedure_id")
            )
            .order_by("-created_at")
        )
        proceduretracing = ProcedureTracingSerializer(trackins, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = procedures.filter(
            Q(code_number__icontains=query)
            | Q(subject__icontains=query)
            | Q(file__person__full_name__icontains=query)
            | Q(file__area__nombre__icontains=query)
            | Q(file__legalperson__razon_social__icontains=query)
            | Q(file__person__numero_documento__icontains=query)
            | Q(file__legalperson__numero_documento__icontains=query),
            **({"created_at__date": date} if date else {}),
        ).order_by("-code_number")
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)
        return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
def create_procedure_charge(request):
    if request.method == "POST":

        user_id = request.data["user_id"]
        procedures = request.data["procedures"]
        procedure_charge = ProcedureCharge.objects.create(
            user_id=user_id,
        )

        for procedure in procedures:
            procedure_id = procedure["id"]
            trankins = (
                ProcedureTracing.objects.filter(
                    procedure_id=procedure_id,
                    user_id=user_id,
                    is_finished=False,
                    to_area_id__isnull=False,
                    procedure_charge__isnull=True,
                    from_area_id__isnull=False,
                )
                .order_by("-created_at")
                .first()
            )
            ProcedureTracing.objects.filter(id=trankins.id).update(
                procedure_charge_id=procedure_charge.id
            )

        return Response(
            status=status.HTTP_200_OK,
            data={
                "correlative": procedure_charge.correlative,
                "id": procedure_charge.id,
            },
        )


@api_view(["GET"])
def get_procedures_reports(request):
    if request.method == "GET":

        query = request.GET.get("query")
        date = request.GET.get("date")

        procedure_tracings = ProcedureTracing.objects.filter()

        proceduretracing = ProcedureTracingSerializer(procedure_tracings, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data]
        )
        procedures = (
            procedures.filter(
                Q(code_number__icontains=query)
                | Q(subject__icontains=query)
                | Q(file__person__full_name__icontains=query)
                | Q(file__area__nombre__icontains=query)
                | Q(file__legalperson__razon_social__icontains=query)
                | Q(file__person__numero_documento__icontains=query)
                | Q(file__legalperson__numero_documento__icontains=query),
                **({"created_at__date": date} if date else {}),
            )
            .annotate(created_at_date=TruncDate("created_at"))
            .order_by("-code_number")
        )
        paginator = CustomPagination()
        paginated_procedures = paginator.paginate_queryset(procedures, request)
        serializer = ProcedureListSerializer(paginated_procedures, many=True)

        return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def get_procedure_and_tracing_by_code_number(request):
    if request.method == "GET":
        code_number = request.GET.get("code_number")

        procedure = Procedure.objects.filter(code_number=code_number).first()
        anexos = Anexo.objects.filter(procedure_id=procedure.id)
        procedure_tracings = ProcedureTracing.objects.filter(
            procedure_id=procedure.id
        ).order_by("-created_at")

        serializer_procedure = ProcedureSerializer(procedure)
        serializer_anexo = AnexoListSerializer(anexos, many=True)
        serializer_procedure_tracings = ProcedureTracingsList(
            procedure_tracings, many=True
        )

        return Response(
            {
                "procedure": serializer_procedure.data,
                "anexos": serializer_anexo.data,
                "procedure_tracings": serializer_procedure_tracings.data,
            }
        )


@api_view(["POST"])
def save_procedure_externo(request):
    if request.method == "POST":
        person_id = request.data["person_id"]
        subject = request.data["subject"]
        attached_files = request.FILES.get("attached_files")
        procedure_type_id = request.data["procedure_type_id"]

        person = Persona.objects.filter(id=person_id).first()
        user_id = person.user_id
        headquarter_id = 1

        number_of_sheets = 0

        area_id = 3
        file = File.objects.filter(person_id=person_id).first()
        if not file:
            File.objects.create(person_id=person_id)

        procedure = Procedure.objects.create(
            file_id=file.id,
            subject=subject,
            attached_files=attached_files,
            procedure_type_id=procedure_type_id,
            headquarter_id=headquarter_id,
            user_id=user_id,
            number_of_sheets=number_of_sheets,
            is_external=True,
        )

        ProcedureTracing.objects.create(
            procedure_id=procedure.id,
            from_area_id=area_id if area_id else None,
            user_id=user_id,
        )

        return Response(
            status=status.HTTP_200_OK, data={"code_number": procedure.code_number}
        )


@api_view(["GET"])
def generete_code_hash(request):
    if request.method == "GET":

        procedure = Procedure.objects.all()

        import shortuuid

        for p in procedure:
            p.code_hash = shortuuid.ShortUUID().random(length=6)
            p.save()
        return Response(status=status.HTTP_200_OK, data={"message": "ok"})
