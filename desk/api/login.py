from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from core.models import Apps, Menu, Persona
from core.serializers import AreaSerializer, PersonSerializer
from core.models import CargoArea
from accounts.serializers import GroupSerializer, UserSerializer


def api_login(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")
        app_name = request.headers["app-name"]

        try:
            user = User.objects.get(username=email, is_active=True)
        except Exception:
            return Response(
                "User does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            groups = user.groups.all()

            app = Apps.objects.filter(name=app_name).first()
            menu = Menu.objects.filter(app=app).first()

            is_group_valid_app = False
            for group in groups:
                if group in menu.groups.all():
                    is_group_valid_app = True
                    break

            if not is_group_valid_app:
                return Response(
                    "User does not have permission",
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            person = Persona.objects.get(user_id=user.id)
            headquarter = (
                CargoArea.objects.filter(persona_id=person.id)
                .values("headquarter_id", "headquarter__name")
                .first()
            )
            person_data = PersonSerializer(person).data

            cargo_area = CargoArea.objects.filter(persona=person).first()
            if not cargo_area:
                areas = []
            data_area = cargo_area.area.all()
            areas = AreaSerializer(data_area, many=True).data
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "groups": GroupSerializer(groups, many=True).data,
                    "token": token.key,
                    "person": person_data,
                    "headquarter": headquarter,
                    "area": areas,
                }
            )
        else:
            return Response(
                "User does not have permission",
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
