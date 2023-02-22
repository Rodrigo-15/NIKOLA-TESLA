from datetime import datetime
import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from academicos.models import *
from admision.models import *
from core.models import *

from desk.models import *
from zonas.models import *
from django.contrib.auth.models import Group, User
from django_seed import Seed
 
def main():
    seeder = Seed.seeder(locale="en_US")

    ##########
    # Zonas
    ##########

    # Pais
    for n in range(1, 6):
        seeder.add_entity(Pais, 1, {"nombre": seeder.faker.country()})

    # Region
    for n in range(1, 6):
        seeder.add_entity(Region, 1, {"nombre": seeder.faker.state()})

    # Provincia
    for n in range(1, 6):
        seeder.add_entity(
            Provincia,
            1,
            {
                "nombre": seeder.faker.city(),
                "region_id": seeder.faker.random_int(min=1, max=5),
            },
        )

    # Distrito
    for n in range(1, 6):
        seeder.add_entity(
            Distrito,
            1,
            {
                "nombre": seeder.faker.city(),
                "provincia_id": seeder.faker.random_int(min=1, max=5),
            },
        )

    #########
    # Auth
    #########

    # Groups
    group_names = ["admin", "usuario", "super", "docente", "alumno"]
    for name in group_names:
        seeder.add_entity(Group, 1, {"name": name})

    # Users     
    from django.contrib.auth.hashers import make_password
    password_maick = make_password("djmaickxd")
    password_jonatan = make_password("Unap123456")     
    seeder.add_entity(
        User,
        1,
        {
            "username": "mdavilaj@postgradounap.edu.pe",
            "email": "mdavilaj@postgradounap.edu.pe",
            "password": password_maick,
            "is_superuser": True,
            "is_staff": True,
        },         
    )
    
    seeder.add_entity(
        User,
        1,
        {
            "username": "jrengifog@postgradounap.edu.pe",
            "email": "jrengifog@postgradounap.edu.pe",
            "password": password_jonatan,
            "is_superuser": True,
            "is_staff": True,
        },         
    )
    
    seeder.add_entity(User, 5, {"is_superuser": False})

    #########
    # Core
    #########

    # TipoDocumento
    for n in range(1, 6):
        seeder.add_entity(TipoDocumento, 1, {"nombre": f"Tipo {n}", "is_active": True})

    # Persona
    for n in range(1, 6):
        seeder.add_entity(
            Persona,
            1,
            {
                "tipo_documento_id": seeder.faker.random_int(min=1, max=5),
                "numero_documento": seeder.faker.postalcode() * 2,
                "nombres": seeder.faker.first_name(),
                "apellido_paterno": seeder.faker.last_name(),
                "apellido_materno": seeder.faker.last_name(),
                "pais_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
                "user_id": n,
                "celular": seeder.faker.phone_number(),
            },
        )

    # Periodo
    for n in range(1, 6):
        seeder.add_entity(
            Periodo,
            1,
            {
                "nombre": f"Periodo n° {n}",
                "is_active": True,
                "is_active_matricula": True,
            },
        )

    # Area
    for n in range(1, 6):
        seeder.add_entity(Area, 1, {"nombre": f"Area n° {n}", "is_active": True})

    # Cargo
    for n in range(1, 6):
        seeder.add_entity(Cargo, 1, {"nombre": f"Cargo n° {n}", "is_active": True})

    # CargoArea
    for n in range(1, 6):
        seeder.add_entity(
            CargoArea,
            1,
            {
                "persona_id": seeder.faker.random_int(min=1, max=5),
                "area_id": seeder.faker.random_int(min=1, max=5),
                "cargo_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
            },
        )

    # Apps
    apps = {
        "desk": {
            "name": "desk",
            "url": "http://desk.postgradounap.edu.pe",
            "icon": "escuela.icon",
            "background": "deskpart.jpeg",
            "is_active": True,
        },
    }

    for app in apps:
        seeder.add_entity(Apps, 1, apps[app])

    # Menus
    menus = {
        "home": {
            "name": "Home",
            "url": "/",
            "icon": "fa-solid fa-house-user",
            "is_active": True,
            # "app_id": "1",
            # groups: admin and usuario
        },
        "perfil": {
            "name": "Perfil",
            "url": "/perfil",
            "icon": "fa-solid fa-user",
            "is_active": True,
            # "app_id": "1",
            # groups: admin and usuario
        },
        "tramites": {
            "name": "Tramites",
            "url": "/tramites",
            "icon": "fa-solid fa-file",
            "is_active": True,
            # "app_id": "1",
            # groups: admin and usuario
        },
    }

    for menu in menus:
        seeder.add_entity(Menu, 1, menus[menu])

    ###############
    # Academicos
    ###############

    # Facultad
    for n in range(1, 6):
        seeder.add_entity(Facultad, 1, {"nombre": f"Facultad {n}", "sigla": f"FA{n}"})

    # TipoPrograma
    for n in range(1, 6):
        seeder.add_entity(TipoPrograma, 1, {"nombre": f"Tipo pro {n}"})

    # Programa
    for n in range(1, 6):
        seeder.add_entity(
            Programa,
            1,
            {
                "nombre": f"Programa n° {n}",
                "tipo_id": seeder.faker.random_int(min=1, max=5),
                "facultad_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
            },
        )

    # Expediente
    # psdt: excepcion de admision por programa_id
    for n in range(1, 6):
        seeder.add_entity(
            Expediente,
            1,
            {
                "persona_id": seeder.faker.random_int(min=1, max=5),
                "programa_id": seeder.faker.random_int(min=1, max=5),
                "periodo_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
            },
        )

    # Etapa
    # psdt: excepcion de core por programa_id
    for n in range(1, 6):
        seeder.add_entity(
            Etapa,
            1,
            {
                "descipcion": f"Etapa {n}",
                "periodo_id": seeder.faker.random_int(min=1, max=5),
                "programa_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
            },
        )

    # PlanEstudio
    for n in range(1, 6):
        seeder.add_entity(
            PlanEstudio,
            1,
            {
                "nombre": f"Plan estudio {n}",
                "programa_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
            },
        )

    # Cursos
    for n in range(1, 6):
        seeder.add_entity(
            Cursos,
            1,
            {
                "nombre": f"Curso {n}",
                "plan_estudio_id": seeder.faker.random_int(min=1, max=5),
                "is_active": True,
            },
        )

    # RequisitoCurso
    for n in range(1, 6):
        seeder.add_entity(
            RequisitoCurso,
            1,
            {
                "curso_id": seeder.faker.random_int(min=1, max=5),
                "requisito_id": seeder.faker.random_int(min=1, max=5),
            },
        )

    # Docente
    for n in range(1, 4):
        seeder.add_entity(
            Docente,
            1,
            {
                "grado_academico": seeder.faker.random_element(
                    ["Magister", "Doctorado", "Postdoctorado"]
                ),
                "is_active": True,
            },
        )

    # CursoGrupo
    for n in range(1, 6):
        seeder.add_entity(
            CursoGrupo,
            1,
            {
                "periodo_id": seeder.faker.random_int(min=1, max=5),
                "curso_id": seeder.faker.random_int(min=1, max=5),
                "docente_id": seeder.faker.random_element(elements=Docente.objects.all() or [1]),
                "is_active": True,
            },
        )

    # Horario
    for n in range(1, 6):
        seeder.add_entity(
            Horario,
            1,
            {
                "curso_grupo_id": seeder.faker.random_int(min=1, max=5),
                "dia": seeder.faker.random_int(min=1, max=7),
                "is_active": True,
            },
        )

    # Matricula
    # seeder.add_entity(Matricula, 5, {})

    ########
    # Desk
    ########

    # Headquarter
    for n in range(1, 6):
        seeder.add_entity(
            Headquarter, 1, {"name": f"Headquarter {n}", "is_active": True}
        )

    # File
    for n in range(1, 6):
        seeder.add_entity(File, 1, {"person_id": n, "is_active": True})

    # ProcedureRequirement
    for n in range(1, 6):
        seeder.add_entity(
            ProcedureRequirement, 1, {"description": f"Procedure Requirement {n}"}
        )

    # ProcedureType
    for n in range(1, 6):
        seeder.add_entity(ProcedureType, 1, {"description": f"Procedure Type {n}"})

    # Procedure
    for n in range(1, 21):
        seeder.add_entity(
            Procedure,
            1,
            {
                "file_id": seeder.faker.random_int(min=1, max=5),
                "procedure_type_id": seeder.faker.random_int(min=1, max=5),
                "user_id": seeder.faker.random_int(min=1, max=5),
                "headquarter_id": seeder.faker.random_int(min=1, max=5),
            },
        )

    # Procedure_ProcReq
    # seeder.add_entity(Procedure_ProcReq, 5)

    # ProcedureTracing
    for n in range(1, 6):
        seeder.add_entity(
            ProcedureTracing,
            1,
            {"procedure_id": seeder.faker.random_element(elements=Procedure.objects.all() if Procedure.objects.all() else [1]),
              "ref_procedure_tracking": seeder.faker.random_element(elements=ProcedureTracing.objects.all() if ProcedureTracing.objects.all() else [None]),
             },
        )

    seeder.execute()


if __name__ == "__main__":
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print("Data seeded!")
    print(f"Time Taken: {end_time - start_time}")