from rest_framework.permissions import IsAuthenticated
from backend.settings import URL_LOCAL, URL_PROD
from core.serializers import (
    CargoAreaSerializer,
    PersonSerializer,
    AreaSerializer,
    CargoAreaPersonSerializer,
)
from .dashboardClasses import *
from django.core.cache import cache
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

from rest_framework.pagination import PageNumberPagination
from collections import defaultdict
from datetime import timedelta, datetime, date

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

from .getdata import *


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


# generators


@api_view(["GET"])
def generete_code_hash(request):
    if request.method == "GET":

        procedure = Procedure.objects.all()

        import shortuuid

        for p in procedure:
            p.code_hash = shortuuid.ShortUUID().random(length=6)
            p.save()
        return Response(status=status.HTTP_200_OK, data={"message": "ok"})


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
        # update
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
        procedure = Procedure.objects.filter(id=procedure_id).first()
        ProcedureTracing.objects.filter(id=tracing_id).update(is_approved=True)

        if procedure.is_external:
            from_area_id = (
                ProcedureTracing.objects.filter(id=tracing_id).first().from_area_id
            )

        else:
            from_area_id = (
                ProcedureTracing.objects.filter(id=tracing_id).first().to_area_id
            )
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
        code_hash = request.GET.get("code_hash")

        procedure = Procedure.objects.filter(
            code_number=code_number, code_hash=code_hash
        ).first()
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
        correo = request.data["correo"]
        celular = request.data["celular"]
        subject = request.data["subject"]
        attached_files = request.FILES.get("attached_files")
        procedure_type_id = request.data["procedure_type_id"]
        headquarter_id = 1

        number_of_sheets = 0
        # actualizar persona persona si el correo o celular estan null o ambos
        person = Persona.objects.filter(id=person_id).first()
        person.correo = correo
        person.celular = celular
        person.save()

        area_id = 3
        user_id = (
            CargoArea.objects.filter(area__id=area_id)
            .values("persona__user_id")
            .first()
        )["persona__user_id"]

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
def get_tracings_to_approved_for_external(request):
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
            is_approved=False, assigned_user_id=None, from_area_id__in=area_id
        ).order_by("-created_at")
        proceduretracing = ProcedureTracingSerializer(tracings_for_area, many=True)

        procedures = Procedure.objects.filter(
            id__in=[procedure["procedure"] for procedure in proceduretracing.data],
            is_external=True,
        ).exclude(
            id__in=ProcedureTracing.objects.values("procedure_id")
            .annotate(count=Count("procedure_id"))
            .filter(count__gt=1)
            .values("procedure_id"),
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
def save_procedure_externo_register(request):
    if request.method == "POST":
        # data person
        nombres = request.data["nombres"]
        numero_documento = request.data["numero_documento"]
        tipo_documento_id = 1
        apellido_paterno = request.data["apellido_paterno"]
        apellido_materno = request.data["apellido_materno"]
        correo = request.data["correo"]
        celular = request.data["celular"]
        # data procedure
        subject = request.data["subject"]
        attached_files = request.FILES.get("attached_files")
        procedure_type_id = request.data["procedure_type_id"]
        headquarter_id = 1

        number_of_sheets = 0
        # creeate person
        obj_person = Persona.objects.filter(
            numero_documento=numero_documento, tipo_documento_id=tipo_documento_id
        ).first()
        if obj_person:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "La persona ya se encuentra registrada"},
            )
        person = Persona.objects.create(
            nombres=nombres,
            numero_documento=numero_documento,
            tipo_documento_id=tipo_documento_id,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            correo=correo,
            celular=celular,
        )
        person_id = person.id

        area_id = 3
        user_id = (
            CargoArea.objects.filter(area__id=area_id)
            .values("persona__user_id")
            .first()
        )["persona__user_id"]

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
def get_dashboard_desk(request):
    dashboardData = YourView()
    data = dashboardData.get(request)

    return data


@api_view(["GET"])
def desk_notification(request):
    user_id = request.GET.get("user_id")
    obj_notify_area = []
    obj_notify_user = []
    obj_notify_external = []
    count_notify = {
        "notify_area": 0,
        "notify_user": 0,
        "notify_external": 0,
    }
    # for area
    cargo_area = CargoArea.objects.filter(persona__user_id=user_id).first()

    if not cargo_area:
        obj_notify_area = []

    data_area = cargo_area.area.all()

    areas = AreaSerializer(data_area, many=True).data
    if areas:
        area_id = [area["id"] for area in areas]

        tracings_for_area = ProcedureTracing.objects.filter(
            to_area_id__in=area_id, is_approved=False, assigned_user_id=None
        ).order_by("-created_at")

        for tracing in tracings_for_area:
            obj_notify_area.append(
                {
                    "procedure_id": tracing.procedure.id,
                    "message": f"{tracing.user}, te ha asignado un trámite con número {tracing.procedure.code_number}. Revisalo por favor.",
                    "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
    # for user
    tracings_for_user = ProcedureTracing.objects.filter(
        to_area_id__in=area_id, assigned_user_id=user_id, is_approved=False
    ).order_by("-created_at")
    for tracing in tracings_for_user:
        obj_notify_user.append(
            {
                "procedure_id": tracing.procedure.id,
                "message": f"{tracing.user}, te ha asignado un trámite con número {tracing.procedure.code_number}. Revisalo por favor.",
                "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    # for external
    tracings_for_external = ProcedureTracing.objects.filter(
        is_approved=False, assigned_user_id=None, from_area_id__in=area_id
    ).order_by("-created_at")
    proceduretracing = ProcedureTracingSerializer(tracings_for_external, many=True)

    procedures = Procedure.objects.filter(
        id__in=[procedure["procedure"] for procedure in proceduretracing.data],
        is_external=True,
    ).exclude(
        id__in=ProcedureTracing.objects.values("procedure_id")
        .annotate(count=Count("procedure_id"))
        .filter(count__gt=1)
        .values("procedure_id"),
    )
    procedures = ProcedureSerializer(procedures, many=True).data
    tracings_for_external = ProcedureTracing.objects.filter(
        procedure_id__in=[p["id"] for p in procedures],
        is_approved=False,
        assigned_user_id=None,
        from_area_id__in=area_id,
    ).order_by("-created_at")

    for tracing in tracings_for_external:
        obj_notify_external.append(
            {
                "procedure_id": tracing.procedure.id,
                "message": f"se creo un  un trámite en linea con número {tracing.procedure.code_number}. Revisalo por favor.",
                "date": tracing.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    count_notify["notify_area"] = len(obj_notify_area)
    count_notify["notify_user"] = len(obj_notify_user)
    count_notify["notify_external"] = len(obj_notify_external)

    return Response(
        {
            "count_notify": count_notify,
            "notify_area": obj_notify_area,
            "notify_user": obj_notify_user,
            "notify_external": obj_notify_external,
        }
    )
