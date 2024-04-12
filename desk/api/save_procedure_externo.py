from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure, File, ProcedureFiles
from core.models import Persona, CargoArea


def api_save_procedure_externo(request):
    try:
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
            procedure_type_id=procedure_type_id,
            headquarter_id=headquarter_id,
            user_id=user_id,
            number_of_sheets=number_of_sheets,
            is_external=True,
        )
        for attached_file in attached_files:
            ProcedureFiles.objects.create(procedure_id=procedure.id, file=attached_file)

        ProcedureTracing.objects.create(
            procedure_id=procedure.id,
            from_area_id=area_id if area_id else None,
            user_id=user_id,
        )

        return Response(
            status=status.HTTP_200_OK, data={"code_number": procedure.code_number}
        )
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
