from django.contrib.auth.models import User
from core.models import Persona
from django.contrib.auth.models import Group


class UserController:
    def create_users(type=None):
        # tipes: alumno, docente, economico                       
        personas = Persona.objects.filter(is_active=True,expediente__promocion='2022-II')
        personas_list = []
        for persona in personas:
            if  persona.user:
                continue
            apellido_paterno_a = persona.apellido_paterno.replace("Á", "A")
            apellido_paterno_e = apellido_paterno_a.replace("É", "E")
            apellido_paterno_i = apellido_paterno_e.replace("Í", "I")
            apellido_paterno_o = apellido_paterno_i.replace("Ó", "O")
            apellido_paterno_u = apellido_paterno_o.replace("Ú", "U")
            apellido_paterno_uu = apellido_paterno_u.replace("Ü", "U")
            apellido_paterno_n = apellido_paterno_uu.replace("Ñ", "N")
            apellido_paterno_sp = apellido_paterno_n.replace(" ", "")
            correo =  persona.nombres[0].lower()+apellido_paterno_sp.lower()+persona.apellido_materno[0].lower()+persona.numero_documento[5]+persona.numero_documento[6]+persona.numero_documento[7]+'@postgradounap.edu.pe'
            print(correo)
            user = User.objects.create_user(
                username=correo, password=persona.numero_documento, email=correo, is_active=False)
            user.first_name = persona.nombres
            user.last_name = persona.get_full_last_name()
            user.save()
            persona.user = user
            persona.save()
            personas_list.append(persona)             
            try:
                grupo = Group.objects.get(name=type)
                user.groups.add(grupo)
            except:
                pass
                
                
        return personas_list
