from rest_framework.response import Response
from rest_framework import status
from desk.models import Procedure, File, ProcedureFiles
from desk.serializers import ProcedureSerializer


def api_update_procedure(request):
    try:
        try:
            procedure_id = request.data["procedure_id"]
            subject = request.data["subject"]
            description = request.data["description"]
            attached_files = request.FILES.getlist("attached_files[]")
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
        procedure.reference_doc_number = reference_doc_number
        procedure.number_of_sheets = number_of_sheets
        procedure.for_the_area_id = for_the_area_id
        procedure.save()

        if attached_files:
            ProcedureFiles.objects.filter(procedure_id=procedure_id).delete()
            for attached_file in attached_files:
                ProcedureFiles.objects.create(
                    procedure_id=procedure_id, file=attached_file
                )

        data = ProcedureSerializer(procedure).data

        return Response(status=status.HTTP_200_OK, data=data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
