from rest_framework.response import Response
from rest_framework import status
from core.models import Area
from core.serializers import AreaSerializer


def api_get_areas(request):
    try:
        areas = Area.objects.filter(is_active=True)
        serializer = AreaSerializer(areas, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
