import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group

from core.models import Persona, TipoDocumento
from desk.models import (
    File,
    Headquarter,
    Procedure,
    ProcedureRequirement,
    ProcedureType,
)
from zonas.models import Pais

# Create your tests here.


def setup_database():
    """Function for setting up data to the test database."""

    # groups
    group_user = Group(id=1, name="usuario")
    group_user.save()

    group_admin = Group(id=2, name="admin")
    group_admin.save()

    # users
    user_1 = User(
        id=1,
        username="user_1",
        email="user1@mail.com",
        is_superuser=True,
        first_name="user",
        last_name="one",
        is_staff=True,
        is_active=True,
    )
    user_1.groups.add(1)
    user_1.groups.add(2)
    user_1.set_password("user1pass")
    user_1.save()

    user_2 = User(
        id=2,
        username="user_2",
        email="user2@mail.com",
        is_superuser=False,
        first_name="user",
        last_name="two",
        is_staff=False,
        is_active=True,
    )
    user_2.groups.add(1)
    user_2.set_password("user2pass")
    user_2.save()


    # countries
    pais_1 = Pais(id=1, nombre="Peru", iso="PE", nacionalidad="Peruana", is_active=True)
    pais_1.save()

    # tipos de documentos
    tipo_documento_1 = TipoDocumento(id=1, nombre="tipo documento 1", is_active=True)
    tipo_documento_1.save()

    # persons
    person_1 = Persona(
        id=1,
        numero_documento=1234,
        nombres="person 1",
        apellido_paterno="Masacre",
        apellido_materno="Masacre",
        sexo="M",
        fecha_nacimiento="1978-03-31",
        is_active=True,
        pais_id=1,
        tipo_documento_id=1,
        correo="user1@mail.com",
        user_id=1,
        celular=98765431,
    )
    person_1.save()


    # desk

    # -- headquarters
    headquarter_1 = Headquarter(id=1, name="headquarter 1", is_active=True)
    headquarter_1.save()

    headquarter_2 = Headquarter(id=2, name="headquarter 2", is_active=True)
    headquarter_2.save()

    # -- files
    file_1 = File(id=1, person=person_1, is_active=True)
    file_1.save()

    # -- procedure requirements
    procedure_req_1 = ProcedureRequirement(id=1, description="procedure requirement 1")
    procedure_req_1.save()

    # -- procedure types
    procedure_type_1 = ProcedureType(id=1, description="procedure type 1")
    procedure_type_1.save()

    # -- procedures
    procedure_2 = Procedure(
        id=2,
        file=file_1,
        code_number="",
        subject="procedure two subject",
        procedure_type=procedure_type_1,
        reference_doc_number="",
        user=user_1,
        headquarter=headquarter_1,
    )
    procedure_2.save()


class DeskTestCase(TestCase):
    def test_login_user(self):
        setup_database()

        client = APIClient()
        client.credentials(HTTP_APP_NAME="desk")

        response = client.post(
            "/desk/login/",
            {
                "email": "user1@mail.com", 
                "password": "user1pass",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content)
        self.assertIn("token", result)

    def test_create_procedure(self):
        setup_database()

        client = APIClient()

        response = client.post(
            "/desk/create_procedure/",
            {
                #"file_id": 1,
                "person_id": 1,
                "code_number": "",
                "subject": "test subject",
                "procedure_type_id": 1,
                "reference_doc_number": "",
                "user_id": 1,
                "headquarter_id": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_update_procedure(self):
        setup_database()

        client = APIClient()

        response = client.put(
            "/desk/update_procedure/",
            {
                "procedure_id": 2,

                "subject": "procedure two edited",
                "procedure_type_id": 1,
                "reference_doc_number": "01",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
