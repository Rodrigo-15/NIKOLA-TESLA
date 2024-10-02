from rest_framework.response import Response
from rest_framework import status
from core.models import CargoArea
from core.serializers import CargoAreaPersonSerializer


def api_get_user_for_area(request):
    try:
        area_id = request.data["area_id"]
        users = CargoArea.objects.filter(area__id=area_id)
        serializer = CargoAreaPersonSerializer(users, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
