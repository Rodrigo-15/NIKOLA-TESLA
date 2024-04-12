from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure, File, ProcedureTracing
from core.models import CargoArea


def api_save_procedure(request):
    try:
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

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
