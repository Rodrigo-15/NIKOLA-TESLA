from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

from core.models import Area, Persona, TipoDocumento
from mesa_partes.models import RequisitoTramite, Sede, SeguimientoTramite, TipoTramite, Tramite
from zonas.models import Pais

# Create your tests here.


def setup_database():
    """Inserta datos a la base de datos de prueba."""

    pais = Pais(id=1, nombre="Peru", iso="PE",
                nacionalidad="Peruana", is_active=True)
    pais.save()

    tipo_documento = TipoDocumento(id=1, nombre="DNI", is_active=True)
    tipo_documento.save()

    usuario = User(id=1, first_name="PAULO")
    usuario.save()

    persona = Persona(id=1, numero_documento=1234, nombres="Walter",
                      apellido_paterno="Macedo", apellido_materno="Rojas", sexo="M", fecha_nacimiento="1978-03-31", is_active=True, pais_id=1, tipo_documento_id=1)
    persona.save()

    sede = Sede(id=1, nombre="Sede 1", is_active=True)
    sede.save()

    area_derivacion = Area(id=1, nombre="Area 1", is_active=1)
    area_derivacion.save()

    requisito_tramite = RequisitoTramite(id=1, descripcion="DNI")
    requisito_tramite.save()

    tipo_tramite = TipoTramite(
        id=1, descripcion="Tipo de tramite 1", is_active=True)
    tipo_tramite.save()

    tramite = Tramite(id=2, asunto="asunto random", persona_id=1,
                      sede_id=1, tipo_tramite_id=1, usuario_id=1)
    tramite.save()

    seguimiento_tramite = SeguimientoTramite(
        id=4, is_iniciado=True, is_revision=False, is_concluido=False, area_derivacion_id=1, tramite_id=2)
    seguimiento_tramite.save()


class MesaPartesViewTests(APITestCase):

    def test_get_tramites(self):
        url = reverse('mesa_partes:get_tramites')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_save_tramite(self):
        setup_database()

        url = reverse('mesa_partes:save_tramite')
        data = {'persona': 1, 'persona_nombre': 'nombre de prueba', 'documento_identidad': 987654321,
                'tipo_tramite': 1, 'asunto': 'asunto de prueba', 'usuario': 1, 'sede': 1, 'area_derivacion': 1, }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_derivar_tramite(self):
        setup_database()

        url = reverse('mesa_partes:derivar_tramite')
        data = {'tramite_id': 2, 'area_derivacion': 1}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_concluir_tramite(self):
        setup_database()

        url = reverse('mesa_partes:concluir_tramite')
        data = {'tramite_id': 2, 'area_derivacion': 1}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_estudiante_by_dni(self):
        setup_database()

        url = reverse('mesa_partes:get_estudiante_by_dni')
        data = {'dni': 1234}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_requisito_tramite_by_desc(self):
        setup_database()

        url = reverse('mesa_partes:get_requisito_tramite_by_desc')
        data = {'descripcion': 'DNI'}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_tramite_by_asunto(self):
        setup_database()

        url = reverse('mesa_partes:get_tramite_by_asunto')
        data = {'asunto': 'asunto random'}
        response = self.client.get(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
