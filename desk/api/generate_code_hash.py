from desk.models import Procedure
import shortuuid
from rest_framework import status
from rest_framework.response import Response


def api_generete_code_hash(request):
    try:
        procedure = Procedure.objects.all()
        for p in procedure:
            p.code_hash = shortuuid.ShortUUID().random(length=6)
            p.save()

        if procedure:
            return Response(
                {"message": "codigo generado correctamente"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                "Error al generar el código", status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
