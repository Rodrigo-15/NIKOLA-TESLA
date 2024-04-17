from rest_framework.response import Response
from rest_framework import status
from desk.models import ProcedureTracing, Procedure


def api_save_derive_procedure(request):
    try:
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
        action_id = request.data["action_id"]
        action_description = request.data["action_description"]
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
                action_id=action_id,
                action_description=action_description,
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
                action_id=action_id,
                action_description=action_description,
                ref_procedure_tracking_id=ref_procedure_tracking_id,
                document_response=document_response,
            )

            return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
