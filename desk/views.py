from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from desk.models import File,Procedure
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token

from accounts.serializers import GroupSerializer, UserSerializer
from core.models import Persona

from django.db.models import  Q

from desk.serializers import ProcedureSerializer
# Create your views here.

@api_view(['POST'])
def get_procedures(request):
    if request.method == 'POST':
        data = request.data
        date = data['date']
        user_id = data['user_id']
        code_number = data['code_number']
        if user_id == '':
            procedures = Procedure.objects.filter(Q(created_at__icontains=date) | Q(code_number__icontains=code_number) )
        else:
            procedures = Procedure.objects.filter(Q(created_at__icontains=date) | Q(code_number__icontains=code_number), user_id=user_id )
        serilaizer = ProcedureSerializer(procedures, many=True)
        return Response(serilaizer.data)

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
                if (
                    not groups.filter(name="usuario").exists()
                    or not groups.filter(name="admin").exists()
                ):
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
