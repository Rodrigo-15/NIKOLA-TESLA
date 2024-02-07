from datetime import date, datetime
from django.db import models

from core.models import Area, BaseModel, Persona, Headquarter

# concepto
from economicos.models import Concepto

# Create your models here.


class File(models.Model):
    person = models.ForeignKey(Persona, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
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
    attached_files = models.FileField(upload_to="tramites/", null=True, blank=True)
    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.CASCADE)
    reference_doc_number = models.CharField(max_length=20, null=True, blank=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    headquarter = models.ForeignKey(Headquarter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    number_of_sheets = models.IntegerField(default=0)
    for_the_area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="for_the_area", null=True, blank=True
    )

    class Meta:
        verbose_name = "procedure"
        verbose_name_plural = "procedures"

    def save(self, *args, **kwargs):
        if not self.id:
            self.code_number = self.generate_code()
        else:
            self.code_number = Procedure.objects.get(id=self.id).code_number
        super(Procedure, self).save(*args, **kwargs)

    def generate_code(self):
        return f"{Procedure.get_count_procedures_by_year(date.today().year) + 1:05d}-{date.today().year}"

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


class ProcedureTracing(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    from_area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="from_area", null=True, blank=True
    )
    to_area = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name="to_area", null=True, blank=True
    )
    action = models.TextField()
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
        upload_to="procedures/document_response/", null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.from_area and self.to_area:
            self.action_log = self.get_derivation_message(self)
        if self.from_area and not self.to_area and not self.is_finished:
            self.action_log = self.get_received_message(self)
            self.action = self.get_received_message(self)
        if self.from_area and self.is_finished:
            self.action_log = self.get_finished_message(self)
            self.action = self.action
        if not self.ref_procedure_tracking:
            self.action_log = self.action = self.get_created_message(self)

        super(ProcedureTracing, self).save(*args, **kwargs)

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
            return f"El documento fue derivado desde {self.from_area} a {self.to_area} {extra_message} por {self.user} el dia {date_formatter(self.created_at)}"
        return f"El documento fue derivado desde {self.from_area} a {self.to_area} {extra_message} por {person.get_full_name()} el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_received_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El documento fue recepcionado por {self.user} en el area {self.from_area} el dia {date_formatter(self.created_at)}"
        return f"El documento fue recepcionado por {person.get_full_name()} en el area {self.from_area} el dia {date_formatter(self.created_at)}"

    @staticmethod
    def get_finished_message(self):
        person = Persona.objects.filter(user=self.user).first()
        if not person:
            return f"El documento fue finalizado y entregado al tramitante  por el usuario {self.user} en el area {self.from_area} {date_formatter(self.created_at)}"
        return f"El documento fue finalizado y entregado al tramitante  por el usuario {person.get_full_name()} en el area {self.from_area} {date_formatter(self.created_at)}"

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

    def __str__(self):
        return self.action_log if self.action_log else self.action
