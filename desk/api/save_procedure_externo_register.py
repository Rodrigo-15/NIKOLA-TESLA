from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure, File, ProcedureFiles
from core.models import Persona, CargoArea


def api_save_procedure_externo_register(request):
    try:
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
        attached_files = request.FILES.getlist("attached_files[]")
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
            procedure_type_id=procedure_type_id,
            headquarter_id=headquarter_id,
            user_id=user_id,
            number_of_sheets=number_of_sheets,
            is_external=True,
        )
        if attached_files:
            for attached_file in attached_files:
                ProcedureFiles.objects.create(
                    procedure_id=procedure.id, file=attached_file
                )
        ProcedureTracing.objects.create(
            procedure_id=procedure.id,
            from_area_id=area_id if area_id else None,
            user_id=user_id,
            action_id=1,
        )

        return Response(
            status=status.HTTP_200_OK, data={"code_number": procedure.code_number}
        )

    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
