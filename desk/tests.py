import json
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group

from core.models import Persona, TipoDocumento
from zonas.models import Pais

# Create your tests here.


def setUp():
    """Function for setting up data to the test database."""

    pais = Pais(id=1, nombre="Peru", iso="PE", nacionalidad="Peruana", is_active=True)
    pais.save()

    tipo_documento = TipoDocumento(id=1, nombre="DNI", is_active=True)
    tipo_documento.save()

    grupo_usuario = Group(id=1, name="usuario")
    grupo_usuario.save()

    grupo_admin = Group(id=2, name="admin")
    grupo_admin.save()

    user = User(
        id=1,
        username="liomar",
        email="elmenteloca@mail.com",
        is_superuser=True,
        first_name="Liomar",
        last_name="Masacre",
        is_staff=True,
        is_active=True,
    )

    print(user.password)
    user.groups.add(1)
    user.groups.add(2)
    user.set_password("contrasena123")
    user.save()

    person = Persona(
        id=1,
        numero_documento=1234,
        nombres="Liomar",
        apellido_paterno="Masacre",
        apellido_materno="Masacre",
        sexo="M",
        fecha_nacimiento="1978-03-31",
        is_active=True,
        pais_id=1,
        tipo_documento_id=1,
        correo="elmenteloca@mail.com",
        user_id=1,
        celular=98765431,
    )
    person.save()


class UserTestCase(TestCase):
    def test_login_user(self):
        setUp()

        client = APIClient()
        client.credentials(HTTP_APP_NAME="desk")

        response = client.post(
            "/desk/login/",
            {"email": "elmenteloca@mail.com", "password": "contrasena123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.content)
        self.assertIn("token", result)
