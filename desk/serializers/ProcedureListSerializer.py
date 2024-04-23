from rest_framework import serializers
from desk.models import ProcedureTracing, ProcedureType
from core.models import Area, Persona, PersonaJuridica
from datetime import datetime, timedelta
from core.views import hollydays


class ProcedureListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code_number = serializers.CharField()
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    reference_doc_number = serializers.CharField()
    subject = serializers.CharField()
    person_full_name = serializers.SerializerMethodField(source="get_person_full_name")
    last_action = serializers.SerializerMethodField(source="get_last_action")
    state = serializers.SerializerMethodField(source="get_state")
    number_of_sheets = serializers.IntegerField()
    area_id = serializers.SerializerMethodField(source="get_area_id")
    due_date = serializers.SerializerMethodField(source="get_due_date")
    state_date = serializers.SerializerMethodField(source="get_state_date")
    state_date_description = serializers.SerializerMethodField(
        source="get_state_date_description"
    )
    for_the_area_id = serializers.IntegerField()

    def get_person_full_name(self, obj):
        file = obj.file
        if file.person_id is None and file.legalperson_id is None:
            area = Area.objects.filter(id=file.area_id).first()
            return area.nombre
        elif file.area_id is None and file.legalperson_id is None:
            person = Persona.objects.filter(id=file.person_id).first()
            return person.get_full_name()

        elif file.area_id is None and file.person_id is None:
            legal_person = PersonaJuridica.objects.filter(
                id=file.legalperson_id
            ).first()
            return legal_person.razon_social

        else:
            return "No registrado"

    def get_last_action(self, obj):
        procedure_tracing = (
            ProcedureTracing.objects.filter(procedure_id=obj.id)
            .order_by("-created_at")
            .first()
        )
        if procedure_tracing:
            return procedure_tracing.action_log
        return "No registrado"

    def get_state(self, obj):
        if ProcedureTracing.objects.filter(procedure_id=obj.id).count() == 1:
            return "Iniciado"
        elif ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_archived:
            return "Archivado"
        elif ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_finished:
            return "Concluido"
        return "En proceso"

    def get_area_id(self, obj):
        if obj.file.area_id:
            return obj.file.area_id
        return None

    def get_due_date(self, obj):
        # Obtener el tipo de procedimiento y los días hábiles necesarios
        procedure_type = ProcedureType.objects.filter(id=obj.procedure_type_id).first()
        procedure_type_days = procedure_type.days
        # Asumiendo que obj.created_at es un objeto datetime
        create_date = obj.created_at.date()
        # Feriados en Perú desde una api externa
        feriados = hollydays()
        # Contador para los días hábiles
        days_added = 0
        current_date = create_date

        # Bucle para contar solo días hábiles (excluyendo sábados y domingos)
        while days_added < procedure_type_days:
            current_date += timedelta(days=1)
            # Lunes=0, Domingo=6 y feriados
            if (
                current_date.weekday() < 5
                and current_date.strftime("%Y-%m-%d") not in feriados
            ):
                days_added += 1

        return current_date.strftime("%Y-%m-%d")

    def get_state_date(self, obj):
        # Obtener el tipo de procedimiento y los días hábiles necesarios
        procedure_type = ProcedureType.objects.filter(id=obj.procedure_type_id).first()
        procedure_type_days = procedure_type.days
        # verificar la fecha del tramite
        traking = (
            ProcedureTracing.objects.filter(procedure_id=obj.id, is_finished=True)
            .order_by("-created_at")
            .first()
        )

        # Asumiendo que obj.created_at es un objeto datetime
        create_date = obj.created_at.date()
        # Feriados en Perú desde una api externa
        feriados = hollydays()
        # Contador para los días hábiles
        days_added = 0
        current_date = create_date

        # Bucle para contar solo días hábiles (excluyendo sábados y dom ingos)
        while days_added < procedure_type_days:
            current_date += timedelta(days=1)
            # Lunes=0, Domingo=6 y feriados
            if (
                current_date.weekday() < 5
                and current_date.strftime("%Y-%m-%d") not in feriados
            ):
                days_added += 1

        # calcular si esta en plazo, si esta a menos de 3 dias de venicimiento o si ya vencio VALIDANDO SI EL TRAMITE ESTA CONCLUIDO
        if traking and traking.is_finished:
            if current_date < traking.created_at.date():
                return 3
            elif current_date - traking.created_at.date() <= timedelta(days=3):
                return 2
            else:
                return 1
        else:
            if current_date < datetime.now().date():
                return 3
            elif current_date - datetime.now().date() <= timedelta(days=3):
                return 2
            else:
                return 1

    def get_state_date_description(self, obj):
        # Obtener el tipo de procedimiento y los días hábiles necesarios
        procedure_type = ProcedureType.objects.filter(id=obj.procedure_type_id).first()
        procedure_type_days = procedure_type.days
        # verificar la fecha del tramite
        traking = (
            ProcedureTracing.objects.filter(procedure_id=obj.id, is_finished=True)
            .order_by("-created_at")
            .first()
        )

        # Asumiendo que obj.created_at es un objeto datetime
        create_date = obj.created_at.date()
        # Feriados en Perú desde una api externa
        feriados = hollydays()
        # Contador para los días hábiles
        days_added = 0
        current_date = create_date

        # Bucle para contar solo días hábiles (excluyendo sábados y dom ingos)
        while days_added < procedure_type_days:
            current_date += timedelta(days=1)
            # Lunes=0, Domingo=6 y feriados
            if (
                current_date.weekday() < 5
                and current_date.strftime("%Y-%m-%d") not in feriados
            ):
                days_added += 1

        # calcular si esta en plazo, si esta a menos de 3 dias de venicimiento o si ya vencio VALIDANDO SI EL TRAMITE ESTA CONCLUIDO
        if traking and traking.is_finished:
            if current_date < traking.created_at.date():
                return "Vencido"
            elif current_date - traking.created_at.date() <= timedelta(days=3):
                return f"Por vencer en {(current_date - traking.created_at.date()).days} días"
            else:
                return "En plazo"
        else:
            if current_date < datetime.now().date():
                return "Vencido"
            elif current_date - datetime.now().date() <= timedelta(days=3):
                return (
                    f"Por vencer en {(current_date - datetime.now().date()).days} días"
                )

            else:
                return "En plazo"
