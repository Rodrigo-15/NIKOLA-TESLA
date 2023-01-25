from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.serializers import GroupSerializer, UserSerializer
from core.models import Persona

# Create your views here.


@api_view(["POST"])
def login(request):
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        client = request.data.get("client", "")

        if not email or not password:
            return Response(
                "Email or password not specified.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if client == "":
            return Response(
                "Client not specified",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, is_active=True)
        except Exception:
            return Response(
                "User does not exist",
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            groups = user.groups.all()

            if client == "desk":
                if not groups.filter(name="usuarios").exists():
                    return Response(
                        "User does not exist",
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

            permissions = user.get_user_permissions()
            person = Persona.objects.get(correo=user.email)

            return Response(
                {
                    "user": UserSerializer(user).data,
                    "groups": GroupSerializer(groups, many=True).data,
                    "token": token.key,
                    "permissions": permissions,
                    "person_id": person.id,
                    "person_name": person.get_full_name(),
                }
            )

        else:
            return Response(
                "Incorrect email or password",
                status=status.HTTP_401_UNAUTHORIZED,
            )
