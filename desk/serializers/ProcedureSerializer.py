from rest_framework import serializers
from desk.models import ProcedureTracing, Procedure, ProcedureType, Anexo
from core.models import Area, Headquarter, Persona, PersonaJuridica
from datetime import datetime, timedelta
from core.views import hollydays


class ProcedureSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    file_id = serializers.IntegerField()
    person_id = serializers.SerializerMethodField(source="get_person_id")
    area_id = serializers.SerializerMethodField(source="get_area_id")
    person_full_name = serializers.SerializerMethodField(source="get_person_full_name")
    person_document = serializers.SerializerMethodField(source="get_person_document")
    code_number = serializers.CharField()
    code_hash = serializers.CharField()
    procedure_type_id = serializers.IntegerField()
    procedure_type_description = serializers.SerializerMethodField(
        source="get_procedure_type_description"
    )
    subject = serializers.CharField()
    description = serializers.CharField()
    reference_doc_number = serializers.CharField()
    headquarter_id = serializers.IntegerField()
    headquarter_name = serializers.SerializerMethodField(source="get_headquarter_name")
    user_id = serializers.IntegerField()
    user_name = serializers.SerializerMethodField(source="get_user_name")
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    updated_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S %p")
    type_person = serializers.SerializerMethodField(source="get_type_person")
    state = serializers.SerializerMethodField(source="get_state")
    due_date = serializers.SerializerMethodField(source="get_due_date")
    state_date = serializers.SerializerMethodField(source="get_state_date")
    state_date_description = serializers.SerializerMethodField(
        source="get_state_date_description"
    )
    anexed_id = serializers.SerializerMethodField(source="get_anexed_id")
    anexed_code_number = serializers.SerializerMethodField(
        source="get_anexed_code_number"
    )
    number_of_sheets = serializers.IntegerField()

    def get_user_name(self, obj):
        person = Persona.objects.filter(user_id=obj.user_id).first()
        if person:
            return person.get_full_name()
        return None

    def get_headquarter_name(self, obj):
        headquarter = Headquarter.objects.filter(id=obj.headquarter_id).first()
        if headquarter:
            return headquarter.name
        return None

    def get_procedure_type_description(self, obj):
        procedure_type = ProcedureType.objects.filter(id=obj.procedure_type_id).first()
        if procedure_type:
            return procedure_type.description
        return None

    def get_person_document(self, obj):
        person = Persona.objects.filter(id=obj.file.person_id).first()
        if person:
            return person.numero_documento

        return None

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

    def get_person_id(self, obj):
        if obj.file.person_id:
            return obj.file.person_id
        elif obj.file.legalperson_id:
            return obj.file.legalperson_id
        return None

    def get_type_person(self, obj):
        if obj.file.person_id:
            return 1
        elif obj.file.legalperson_id:
            return 2
        elif obj.file.area_id:
            return 0
        return None

    def get_area_id(self, obj):
        if obj.file.area_id:
            return obj.file.area_id
        return None

    def get_attached_file(self, obj):
        if obj.attached_files:
            return obj.attached_files.url
        return "No adjunto"

    def get_state(self, obj):
        try:
            if ProcedureTracing.objects.filter(procedure_id=obj.id).count() == 1:
                return "Iniciado"
            elif (
                ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_archived
            ):
                return "Archivado"
            elif (
                ProcedureTracing.objects.filter(procedure_id=obj.id).last().is_finished
            ):
                return "Concluido"
            return "En proceso"
        except:
            return "Iniciado"

    def get_due_date(self, obj: Procedure):
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

    def get_anexed_id(self, obj):
        anexed = Anexo.objects.filter(procedure_anexo_id=obj.id).first()
        if anexed:
            return anexed.procedure_id
        return None

    def get_anexed_code_number(self, obj):
        anexed = Anexo.objects.filter(procedure_anexo_id=obj.id).first()
        if anexed:
            return anexed.procedure.code_number
        return None

    class Meta:
        model = Procedure
        fields = "__all__"
