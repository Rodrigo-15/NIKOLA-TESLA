from unicodedata import name
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from accounts.serializers import GroupSerializer, UserSerializer
from core.models import Persona


@api_view(["POST"])
def login(request):
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        cliente = request.data.get("cliente", "")

        if not email or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if cliente == "":
            return Response(
                {"error": "No se ha especificado el cliente"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=email, is_active=True)
            print(email)
        except:
            return Response(
                "El usuario   no existe",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            user_model = User.objects.get(email=email)
            groups = user_model.groups.all()
            if cliente == "matricula":
                if not groups.filter(name="alumno").exists():
                    if not groups.filter(name="docente").exists():
                        return Response(
                            "El usuario de matriculas con este correo electrónico no existe",
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
            if cliente == "economicos":
                if not groups.filter(name="usuario").exists():
                    return Response(
                        "El usuario con este correo electrónico no existe",
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            if cliente == "academicos":
                if not groups.filter(name="usuario").exists():
                    return Response(
                        "El usuario con este correo electrónico no existe",
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            if cliente == "mesapartes":
                if not groups.filter(name="usuario").exists():
                    return Response(
                        "El usuario con este correo electrónico no existe",
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            permissions = user_model.get_user_permissions()
            persona = Persona.objects.get(user=user_model)
            return Response(
                {
                    "user": UserSerializer(user_model).data,
                    "groups": GroupSerializer(groups, many=True).data,
                    "token": token.key,
                    "permissions": permissions,
                    "persona_id": persona.id,
                    "persona_nombres": persona.nombres,
                    "persona_apellido_paterno": persona.apellido_paterno,
                }
            )
        else:
            return Response(
                "Wrong email or password",
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["POST"])
def get_user_data_by_token(request):
    if request.method == "POST":
        user = request.user
        cliente = request.data.get("cliente", "")
        if cliente == "":
            return Response(
                {"error": "No se ha especificado el cliente"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, created = Token.objects.get_or_create(user=user)
        user_model = User.objects.get(email=user.email)
        groups = user_model.groups.all()
        if cliente == "matricula":
            if not groups.filter(name="alumno").exists():
                if not groups.filter(name="docente").exists():
                    return Response(
                        "El usuario con este correo electrónico no existe",
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
        if cliente == "economicos":
            if not groups.filter(name="usuario").exists():
                return Response(
                    "El usuario con este correo electrónico no existe",
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        permissions = user_model.get_user_permissions()
        persona = Persona.objects.get(user=user_model)
        return Response(
            {
                "user": UserSerializer(user_model).data,
                "groups": GroupSerializer(groups, many=True).data,
                "token": token.key,
                "permissions": permissions,
                "persona_id": persona.id,
            }
        )


@api_view(["POST"])
def create_users_alumnos(request):
    if request.method == "POST":
        from accounts.utils.user import UserController

        personas_list = UserController.create_users("alumno")
        count = len(personas_list)
        return Response(
            {
                "personas": count,
            }
        )


@api_view(["GET"])
def rename_files(request):
    if request.method == "GET":
        import re
        import os
        from django.conf import settings

        # Ruta al directorio que contiene el archivo
        directorio = "C:/Users/PC-01/Documents/Proyectos-epg/sigae-back/media/fotos"
        print(directorio)
        # Listar los archivos en el directorio
        archivos = os.listdir(directorio)

        # Iterar a través de los archivos en el directorio
        for nombre_archivo in archivos:
            # Utilizar una expresión regular para extraer los números del nombre del archivo
            numeros = re.sub(r"\D", "", nombre_archivo)

            # Comprobar si hay números en el nombre del archivo
            if numeros:
                # Construir el nuevo nombre del archivo con el número extraído
                nuevo_nombre_archivo = f"{numeros}.jpg"

                # Obtener la ruta completa del archivo original y del nuevo archivo
                ruta_original = os.path.join(directorio, nombre_archivo)
                nueva_ruta = os.path.join(directorio, nuevo_nombre_archivo)

                # Renombrar el archivo
                os.rename(ruta_original, nueva_ruta)

                # Imprimir el cambio
                print(
                    f"El archivo '{nombre_archivo}' ha sido renombrado como '{nuevo_nombre_archivo}'"
                )
            else:
                # Si no hay números en el nombre del archivo, imprimir un mensaje
                print(
                    f"El archivo '{nombre_archivo}' no contiene números y no ha sido renombrado."
                )

        return Response("OK")
