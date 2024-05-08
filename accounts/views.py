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


@api_view(["GET"])
def create_users_alumnos(request):
    if request.method == "GET":
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


@api_view(["GET"])
def importar_persona_expediente_xlsx(request):
    if request.method == "GET":
        import openpyxl
        from core.models import  Persona
        from admision.models import Expediente
        from datetime import datetime
        import os
        from backend import settings

        # Ruta al archivo de Excel
        archivo = os.path.join(settings.MEDIA_ROOT, "importaciones.xlsx")

        # Cargar el archivo de Excel
        wb = openpyxl.load_workbook(archivo)
        # Seleccionar la hoja de trabajo
        ws = wb.active
        count_personas = 0
        count_expedientes = 0
        # Iterar a través de las filas en la hoja de trabajo
        for row in ws.iter_rows(min_row=2, values_only=True):
            numero_documento = row[0]
            nombres = row[1]
            apellido_paterno = row[2]
            apellido_materno = row[3]
            sexo = row[4]
            fecha_nacimiento = row[5]
            pais_id = row[6]
            tipo_documento_id = row[7]
            correo = row[8]
            celular = row[9]
            full_name = row[10]
            programa_id = row[11]
            periodo_id = row[13]
            promocion = row[14]

            # Crear una nueva persona
            if not Persona.objects.filter(numero_documento=numero_documento).exists():
                persona = Persona.objects.create(
                    numero_documento=numero_documento,
                    nombres=nombres,
                    apellido_paterno=apellido_paterno,
                    apellido_materno=apellido_materno,
                    sexo=sexo,
                    fecha_nacimiento=datetime.strptime(fecha_nacimiento, "%Y-%m-%d"),
                    pais_id=pais_id,
                    tipo_documento_id=tipo_documento_id,
                    correo=correo,
                    celular=celular,
                    full_name=full_name,
                )
                expediente = Expediente.objects.create(
                    persona=persona,
                    programa_id=programa_id,
                    periodo_id=periodo_id,
                    promocion=promocion,
                )
                count_personas += 1
                count_expedientes += 1
            else:
                persona = Persona.objects.get(numero_documento=numero_documento)
                if not Expediente.objects.filter(persona=persona, programa_id=programa_id, periodo_id=periodo_id).exists():
                    expediente = Expediente.objects.create(
                        persona=persona,
                        programa_id=programa_id,
                        periodo_id=periodo_id,
                        promocion=promocion,
                    )
                    count_expedientes += 1
        
        return Response(
            {
                "personas": count_personas,
                "expedientes": count_expedientes,
            }
        )


@api_view(["GET"])
def resend_email(request):
    if request.method == "GET":
        import resend
        from backend.settings import EMAIL_FROM, EMAIL_KEY, URL_PROD

        resend.api_key = EMAIL_KEY
        personas = Persona.objects.filter(
            is_active=True, expediente__promocion="2022-II", numero_documento = "73134712"
        )
        personas_count = 0
        link_de_consulta = f"https://intranet.postgradounap.edu.pe/#/"
        logoUnap = f"{URL_PROD}media/config/logo_UNAP.svg"
        for persona in personas:
            if persona.correo:
                html_content = f"""
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Bienvenida a la Intranet</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                        }}

                        .header {{
                            background-color: #f2f2f2;
                            padding: 20px;
                            text-align: center;
                        }}

                        .content {{
                            margin: 20px;
                            text-align: center;
                        }}

                        .footer {{
                            background-color: #f2f2f2;
                            padding: 10px;
                            text-align: center;
                            font-size: 12px;
                        }}

                        .bg-gray-100 {{
                            background-color: #f2f2f2;
                            padding: 20px;
                            text-align: center;
                        }}

                        .bg-white {{
                            background-color: #fff;
                            padding: 20px;
                            margin: 20px;
                        }}
                        
                        .bg-slate-100 {{
                            background-color: #708090;
                            padding: 20px;
                            color: #fff;
                            text-align: center;
                        }}

                        .text-3xl {{
                            font-size: 24px;
                        }}

                        .font-bold {{
                            font-weight: bold;
                        }}

                        .text-primary-800 {{
                            color: #333366;
                        }}

                        .text-xl {{
                            font-size: 20px;
                        }}

                        .text-primary-600 {{
                            color: #4d4dff;
                        }}

                        .text-xs {{
                            font-size: 12px;
                        }}

                        .text-white {{
                            color: #fff;
                        }}

                        .bg-primary {{
                            background-color: #3b5998;
                            color: #fff;
                        }}

                        .bg-primary:hover {{
                            background-color: rgba(59, 89, 152, 0.9);
                        }}

                        .btn {{
                            display: inline-block;
                            padding: 8px 16px;
                            margin: 10px;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                            text-decoration: none;
                        }}

                        .btn-primary {{
                            background-color: #3b5998;
                            color: #fff;
                        }}

                        .btn-primary:hover {{
                            background-color: rgba(59, 89, 152, 0.9);
                        }}
                    </style>
                </head>

                <body>
                    <div class="header">
                        <div class="bg-gray-100">
                            <img src="{logoUnap}" alt="logo-unap" style="width:180px; margin: auto;" />
                            <div class="flex flex-col items-center">
                                <h2 class="text-3xl font-bold text-primary-800">USUARIO DEL SISTEMA DE INTRANET</h2>
                            </div>
                        </div>
                    </div>

                    <div class="content">
                        <div class="bg-white">
                            <h3 class="text-xl font-bold text-primary-600">Estimado(a) {persona.nombres} {persona.apellido_paterno} {persona.apellido_materno}</h3>
                            <p class="text-xs">La Escuela de Posgrado de la Universidad Nacional de la Amazonia Peruana le da la bienvenida a los sistemas de intranet.</p>
                        </div>

                        <div class="flex flex-col items-center p-4">
                            <a href="{link_de_consulta}" class="btn btn-primary">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                                    class="icon icon-tabler icons-tabler-outline icon-tabler-download">
                                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                                    <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2"></path>
                                    <path d="M7 11l5 5l5 -5"></path>
                                    <path d="M12 4l0 12"></path>
                                </svg>
                                Sistema de intranet
                            </a>
                        </div>
                    </div>

                    <div class="footer">
                        <div class="bg-slate-100">
                            <p>© 2024 Escuela de Postgrado - UNAP</p>
                        </div>
                    </div>
                </body>

                </html>"""

                params = {
                    "from": f"Notificación <{EMAIL_FROM}>",
                    "to": [f"{persona.correo}"],
                    "subject": "CORREO INSTITUCIONAL PARA LOS SISTEMAS DE INTRANET EPG - UNAP",
                    "html": html_content,
                    "headers": {"X-Entity-Ref-ID": "123456789"},
                    # "attachments": [{"filename": "invoice.pdf", "content": list(f)}],
                }

                resend.Emails.send(params)  
                personas_count += 1


        return Response(
            {
                "correos_enviados": personas_count,
            }
        )
