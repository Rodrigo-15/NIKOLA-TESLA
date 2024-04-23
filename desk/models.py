from datetime import date, datetime
from django.db import models

from core.models import Area, BaseModel, Persona, Headquarter, PersonaJuridica

# concepto
from economicos.models import Concepto

# Create your models here.


class File(models.Model):
    person = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    legalperson = models.ForeignKey(
        PersonaJuridica, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateField(auto_now_add=True, auto_now=False)
    updated_at = models.DateField(auto_now_add=False, auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "file"
        verbose_name_plural = "files"

    @staticmethod
    def get_last_file_id():
        return File.objects.filter().values("id").last()["id"]

    def __str__(self):
        if self.person:
            return self.person.nombres
        if self.area:
            return self.area.nombre
        return "Unnamed"


class ProcedureRequirement(models.Model):
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = "procedure requirement"
        verbose_name_plural = "procedure requirements"

    @staticmethod
    def get_procedure_requirement_by_desc(description):
        return ProcedureRequirement.objects.filter(description)

    def __str__(self):
        return self.description


class ProcedureType(models.Model):
    concepto = models.ForeignKey(
        Concepto, on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    days = models.IntegerField(default=0)

    class Meta:
        verbose_name = "procedure type"
        verbose_name_plural = "procedure types"

    def __str__(self):
        return self.description


class Procedure(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    code_number = models.CharField(max_length=15, null=True, blank=True)
    subject = models.TextField(null=False, blank=False)
    description = models.TextField(null=True, blank=True, default="")
    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.CASCADE)
    reference_doc_number = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    headquarter = models.ForeignKey(Headquarter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    number_of_sheets = models.IntegerField(default=0)
    for_the_area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name="for_the_area",
        null=True,
        blank=True,
    )
    is_external = models.BooleanField(default=False)
    code_hash = models.CharField(max_length=12, null=True, blank=True)

    class Meta:
        verbose_name = "procedure"
        verbose_name_plural = "procedures"

    def save(self, *args, **kwargs):
        if not self.id:
            self.code_number = self.generate_code()
            self.code_hash = self.generate_code_hash()
            super(Procedure, self).save(*args, **kwargs)
            self.notification_email()
        else:
            super(Procedure, self).save(*args, **kwargs)

    def generate_code(self):
        return f"{Procedure.get_count_procedures_by_year(date.today().year) + 1:05d}-{date.today().year}"

    def generate_code_hash(self):
        import shortuuid

        return shortuuid.ShortUUID().random(length=6)

    @staticmethod
    def get_count_procedures_by_year(year):
        return Procedure.objects.filter(created_at__year=year).count()

    @staticmethod
    def get_last_procedure_id():
        if Procedure.objects.filter().values("id").last():
            return Procedure.objects.filter().values("id").last()["id"]
        return 0

    @staticmethod
    def get_procedure_by_id(procedure_id):
        return Procedure.objects.filter(id=procedure_id)

    def notification_email(self):
        import resend
        from backend.settings import EMAIL_FROM, EMAIL_KEY, URL_PROD

        resend.api_key = EMAIL_KEY
        code_number = self.code_number
        code_hash = self.code_hash
        logoUnap = f"{URL_PROD}media/config/logo_UNAP.svg"
        if self.file.person:
            correo = self.file.person.correo
            tramitante = (
                self.file.person.nombres
                + " "
                + self.file.person.apellido_paterno
                + " "
                + self.file.person.apellido_materno
            )
        elif self.file.legalperson:
            correo = self.file.legalperson.correo
            tramitante = self.file.legalperson.razon_social
        elif self.file.area:
            correo = self.file.area.correo
            tramitante = self.file.area.nombre

        if correo:
            html_content = f"""
                <html>
                    <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
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
                        }}
                        .text-3xl {{
                            font-size: 24px;
                        }}
                        .font-bold {{
                            font-weight: bold;
                        }}
                        .text-primary-800{{
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
                        .bg-[#3b5998] {{
                            background-color: #3b5998;
                        }}
                        .hover\:bg-[#3b5998]\/90:hover {{
                            background-color: rgba(59, 89, 152, 0.9);
                        }}
                        .icon-tabler-outline {{
                            fill: none;
                            stroke: currentColor;
                            stroke-width: 2;
                            stroke-linecap: round;
                            stroke-linejoin: round;
                        }}
                    </style>
                    </head>
                    <body>
                    
                        <div class="header">
                    <div class="bg-gray-100">
                    <img src="{logoUnap}" alt="logo-unap" style="width:180px; margin: auto;" />
                    <div class="flex flex-col items-center">
                    <h2 class="text-3xl font-bold text-primary-800">Expediente N° {code_number}</h2>
                    <h3 class="text-xl font-semibold">
                                        Código de trámite: <span class="text-primary-600">{code_hash}</span>
                    </h3>
                    </div>
                    </div>
                    <div class="bg-white">
                    <p>
                    <span class="font-bold">Remitente: </span> {tramitante}
                    </p>
                    <p>
                    <span class="font-bold">Tipo de trámite: </span>{self.procedure_type.description}
                    </p>
                    <p>
                    <span class="font-bold">Fecha de registro: </span> {self.created_at.strftime("%d/%m/%Y %H:%M %p")}
                    </p>
                    <p>
                    <span class="font-bold">Asunto: </span> {self.subject}
                    </p>
                    </div>
                    <div class="flex flex-col items-center p-4">
                    <button type="button" class="text-white bg-[#3b5998] hover:bg-[#3b5998]/90 focus:ring-4 focus:outline-none focus:ring-[#3b5998]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#3b5998]/55 me-2 mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-download">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2"></path>
                    <path d="M7 11l5 5l5 -5"></path>
                    <path d="M12 4l0 12"></path>
                    </svg>
                                    consulta tu trámite en línea
                    </button>
                    </div>
                    <div class="py-4 bg-slate-100"></div>
                    </div>
                    
                    </body>
                    </html>"""

            params = {
                "from": f"Notificación <{EMAIL_FROM}>",
                "to": [f"{correo}"],
                "subject": "REGISTRO DE TRAMITE EN LINEA - EPG-UNAP",
                "html": html_content,
                # "headers": {"X-Entity-Ref-ID": "123456789"},
                "headers": {"X-Entity-Ref-ID": f"{code_hash}"},
                # "attachments": [{"filename": "invoice.pdf", "content": list(f)}],
            }

            resend.Emails.send(params)
        pass

    def __str__(self):
        return f"{self.file_id} - {self.code_number} - {self.subject} - {self.procedure_type} -\
                 {self.reference_doc_number} - {self.headquarter}"


class Procedure_ProcReq(models.Model):
    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.CASCADE)
    requirement = models.ForeignKey(ProcedureRequirement, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "procedure_procreq"
        verbose_name_plural = "procedure_procreqs"

    def __str__(self):
        return f"{self.procedure_type} - {self.requirement}"


def date_formatter(date):
    if date is None:
        return datetime.now().strftime("%d/%m/%Y %H:%M %p")
    return date.strftime("%d/%m/%Y %H:%M %p")


class ProcedureCharge(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    correlative = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name = "procedure charge"
        verbose_name_plural = "procedure charges"

    def save(self, *args, **kwargs):
        if not self.id:
            self.correlative = self.generate_correlative()
        super(ProcedureCharge, self).save(*args, **kwargs)

    def generate_correlative(self):
        # by year and area
        return f"{ProcedureCharge.get_count_charges_by_year(date.today().year) + 1:05d}-{date.today().year}-EPG-UNAP"

    @staticmethod
    def get_count_charges_by_year(year):
        return ProcedureCharge.objects.filter(created_at__year=year).count()

    def __str__(self):
        return f"{self.correlative} - {self.user}"


class procedureAction(models.Model):
    id = models.AutoField(primary_key=True)
    action = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "procedure action"
        verbose_name_plural = "procedure actions"

    def __str__(self):
        return f"{self.id} - {self.action}"


class ProcedureTracing(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    from_area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="from_area", null=True, blank=True
    )
    to_area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="to_area", null=True, blank=True
    )
    action = models.ForeignKey(
        procedureAction, on_delete=models.CASCADE, null=True, blank=True
    )
    action_description = models.TextField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    ref_procedure_tracking = models.ForeignKey(
        "desk.ProcedureTracing",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="procedure_tracking",
    )
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    assigned_user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="assigned_user",
    )
    action_log = models.TextField(null=True, blank=True)
    document_response = models.FileField(
        upload_to="tramites/seguimiento/", null=True, blank=True
    )
    is_archived = models.BooleanField(default=False)
    is_anexed = models.BooleanField(default=False)
    procedure_charge = models.ForeignKey(
        ProcedureCharge, on_delete=models.CASCADE, null=True, blank=True
    )
    is_internal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_anexed and self.is_finished:
            self.action_log = self.action_description = self.get_anexed_message(self)
        elif self.is_internal:
            self.action_log = self.get_internal_message(self)
        elif not self.ref_procedure_tracking and self.procedure.is_external:
            self.action_log = self.action_description = self.get_external_message(self)
        elif not self.ref_procedure_tracking:
            self.action_log = self.action_description = self.get_created_message(self)
        elif self.is_anexed and not self.is_finished:
            self.action_log = self.action_description = self.get_in_anexed_message(self)
        elif self.is_finished and self.is_archived:
            self.action_log = self.action_description = self.get_archived_message(self)
        elif self.from_area and self.to_area:
            self.action_log = self.get_derivation_message(self)
        elif self.from_area and not self.to_area and not self.is_finished:
            self.action_log = self.get_received_message(self)
            self.action_description = self.get_received_message(self)
        elif self.from_area and self.is_finished:
            self.action_log = self.get_finished_message(self)
            self.action_description = self.action_description
        super(ProcedureTracing, self).save(*args, **kwargs)
        if self.is_finished:
            self.notification_email()

    class Meta:
        verbose_name = "procedure tracing"
        verbose_name_plural = "procedure tracings"

    @staticmethod
    def get_created_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El Tramite fue creado por {self.user} en el area {self.from_area} el dia {date_formatter(self.created_at)}"
        return f"El Tramite fue creado por {person.get_full_name()} en el area {self.from_area} el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_derivation_message(self):
        extra_message = (
            f" para el usuario {self.assigned_user}" if self.assigned_user else ""
        )
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El tramite fue derivado desde {self.from_area} a {self.to_area} {extra_message} por {self.user} el dia {date_formatter(self.created_at)}"
        return f"El tramite fue derivado desde {self.from_area} a {self.to_area} {extra_message} por {person.get_full_name()} el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_received_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El tramite fue recepcionado por {self.user} en el area {self.from_area} el dia {date_formatter(self.created_at)}"
        return f"El tramite fue recepcionado por {person.get_full_name()} en el area {self.from_area} el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_finished_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El tramite fue finalizado por el usuario {self.user} en el area {self.from_area} {date_formatter(self.created_at)}"
        return f"El tramite fue finalizado por el usuario {person.get_full_name()} en el area {self.from_area} {date_formatter(self.created_at)}"

    @staticmethod
    def get_anexed_message(self):
        person = Persona.objects.filter(user=self.user).first()
        anexo = Anexo.objects.filter(procedure_anexo_id=self.procedure_id).first()
        procedure = Procedure.objects.filter(id=anexo.procedure_id).first()
        code_number = procedure.code_number
        if not person:
            return f"El trámite actual ha sido anexado al trámite N° {code_number} por el usuario {self.user} en el area {self.from_area} {date_formatter(self.created_at)}"
        return f"El trámite actual ha sido anexado al trámite N° {code_number} por el usuario {person.get_full_name()} en el area {self.from_area} {date_formatter(self.created_at)}"

    @staticmethod
    def get_in_anexed_message(self):
        person = Persona.objects.filter(user=self.user).first()
        anexo = Anexo.objects.filter(procedure_id=self.procedure_id).first()
        procedure = Procedure.objects.filter(id=anexo.procedure_anexo_id).first()
        code_number_anexed = procedure.code_number
        if not person:
            return f"El trámite N° {code_number_anexed} ha sido anexado al trámite {self.procedure.code_number} porl el usuario {self.user} en el area {self.from_area} {date_formatter(self.created_at)}"
        return f"El trámite N° {code_number_anexed} ha sido anexado al trámite {self.procedure.code_number} por el usuario {person.get_full_name()} en el area {self.from_area} {date_formatter(self.created_at)}"

    @staticmethod
    def get_archived_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El tramite fue archivado por el usuario {self.user} en el area {self.from_area} {date_formatter(self.created_at)}"
        return f"El tramite fue archivado por el usuario {person.get_full_name()} en el area {self.from_area} {date_formatter(self.created_at)}"

    @staticmethod
    def get_external_message(self):
        person = Persona.objects.filter(id=self.procedure.file.person_id).first()
        return f"El tramite fue creado por el usuario {person.get_full_name()} por el sistema en linea el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_internal_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"Accion interna realizada por el usuario {self.user} en el area {self.from_area} el dia {date_formatter(self.created_at)}"
        return f"Accion interna realizada por el usuario {person.get_full_name()} en el area {self.from_area} el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_tracing_by_procedure_id(procedure_id):
        return ProcedureTracing.objects.filter(procedure_id=procedure_id)

    @staticmethod
    def get_referral_area_by_procedure_id(procedure_id):
        return (
            ProcedureTracing.objects.filter(procedure_id=procedure_id)
            .values("referral_area_id")
            .last()["referral_area_id"]
        )

    def notification_email(self):
        import resend
        from backend.settings import EMAIL_FROM, EMAIL_KEY, URL_PROD

        resend.api_key = EMAIL_KEY
        code_number = self.procedure.code_number
        logoUnap = f"{URL_PROD}media/config/logo_UNAP.svg"
        if self.procedure.file.person:
            correo = self.procedure.file.person.correo
            tramitante = (
                self.procedure.file.person.nombres
                + " "
                + self.procedure.file.person.apellido_paterno
                + " "
                + self.procedure.file.person.apellido_materno
            )
        elif self.procedure.file.legalperson:
            correo = self.procedure.file.legalperson.correo
            tramitante = self.procedure.file.legalperson.razon_social
        elif self.procedure.file.area:
            correo = self.procedure.file.area.correo
            tramitante = self.procedure.file.area.nombre
        if correo:
            html_content = f"""
                <html>
                    <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
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
                        }}
                        .text-3xl {{
                            font-size: 24px;
                        }}
                        .font-bold {{
                            font-weight: bold;
                        }}
                        .text-primary-800{{
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
                        .bg-[#3b5998] {{
                            background-color: #3b5998;
                        }}
                        .hover\:bg-[#3b5998]\/90:hover {{
                            background-color: rgba(59, 89, 152, 0.9);
                        }}
                        .icon-tabler-outline {{
                            fill: none;
                            stroke: currentColor;
                            stroke-width: 2;
                            stroke-linecap: round;
                            stroke-linejoin: round;
                        }}
                    </style>
                    </head>
                    <body>
                    
                        <div class="header">
                    <div class="bg-gray-100">
                    <img src="{logoUnap}" alt="logo-unap" style="width:180px; margin: auto;" />
                    <div class="flex flex-col items-center">
                    <h2 class="text-3xl font-bold text-primary-800">Expediente N° {code_number} has sido concluido</h2>
                    </div>
                    </div>
                    <div class="bg-white">
                    <p>
                    <span class="font-bold">Remitente: </span> {tramitante}
                    </p>
                    <p>
                    <span class="font-bold">Tipo de trámite: </span>{self.procedure.procedure_type.description}
                    </p>
                    <p>
                    <span class="font-bold">Fecha de registro: </span> {self.created_at.strftime("%d/%m/%Y %H:%M %p")}
                    </p>
                    <p>
                    <span class="font-bold">Asunto: </span> {self.procedure.subject}
                    </p>
                    </div>
                    <div class="flex flex-col items-center p-4">
                    <button type="button" class="text-white bg-[#3b5998] hover:bg-[#3b5998]/90 focus:ring-4 focus:outline-none focus:ring-[#3b5998]/50 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center dark:focus:ring-[#3b5998]/55 me-2 mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon icon-tabler icons-tabler-outline icon-tabler-download">
                    <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                    <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2"></path>
                    <path d="M7 11l5 5l5 -5"></path>
                    <path d="M12 4l0 12"></path>
                    </svg>
                                    consulta tu trámite en línea
                    </button>
                    </div>
                    <div class="py-4 bg-slate-100"></div>
                    </div>
                    
                    </body>
                    </html>"""

            params = {
                "from": f"Notificación <{EMAIL_FROM}>",
                "to": [f"{correo}"],
                "subject": "FINALIZACION DE TRAMITE - EPG-UNAP",
                "html": html_content,
                "headers": {"X-Entity-Ref-ID": "123456789"},
                # "attachments": [{"filename": "invoice.pdf", "content": list(f)}],
            }

            resend.Emails.send(params)
        pass

    def __str__(self):
        return self.action_log if self.action_log else self.action


class Anexo(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    procedure_anexo = models.ForeignKey(
        Procedure, on_delete=models.CASCADE, related_name="procedure_anexo"
    )
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "anexo"
        verbose_name_plural = "anexos"

    def __str__(self):
        return f"{self.procedure} - {self.procedure_anexo}"


class ProcedureFiles(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    file = models.FileField(upload_to="tramites/adjunto/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "procedure file"
        verbose_name_plural = "procedure files"

    def __str__(self):
        return f"{self.procedure} - {self.file}"
