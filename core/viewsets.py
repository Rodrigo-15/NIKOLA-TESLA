from rest_framework.viewsets import ModelViewSet

from core.models import *
from core.serializers import *
from rest_framework.response import Response


class PersonaViewSet(ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonSerializer

    def update(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        persona = Persona.objects.get(id=id)
        data = request.data
        serializer = PersonSerializer(instance=persona, data=data)
        if not serializer.is_valid():
            if len(serializer.errors) == 1 and serializer.errors.get("foto"):
                data = request.data.copy()
                data["foto"] = persona.foto
                serializer = PersonSerializer(instance=persona, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                #
                final_data = serializer.data
                from backend.settings import DEBUG, URL_LOCAL, URL_PROD
                url = URL_LOCAL if DEBUG else URL_PROD
                path = final_data.get("foto")
                if path:
                    path = path.replace("/media", "media")
                    final_data["foto"] = url + path
                return Response(data=final_data, status=200)
            return Response(data=serializer.errors, status=400)
        serializer.save()
        return Response(data=serializer.data, status=200)


class AreaViewSet(ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer