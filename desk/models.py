from django.db import models

from core.models import Area, Persona

# Create your models here.


class Headquarter(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "headquarter"
        verbose_name_plural = "headquarters"

    def __str__(self):
        return self.name


class File(models.Model):
    subject = models.TextField()
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
        return self.subject


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
    description = models.CharField(max_length=50)

    class Meta:
        verbose_name = ("procedure type")
        verbose_name_plural = ("procedure types")

    def __str__(self):
        return self.description


class Procedure(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    person = models.ForeignKey(
        Persona, on_delete=models.CASCADE, null=True, blank=True)
    entity = models.CharField(max_length=50, null=True, blank=True)
    id_number = models.CharField(max_length=20, null=True, blank=True)
    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.CASCADE)
    subject = models.TextField(null=False, blank=False)
    reference_doc_number = models.CharField(max_length=20)
    # user who registered the procedure
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    headquarter = models.ForeignKey(Headquarter, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "procedure"
        verbose_name_plural = "procedures"

    @staticmethod
    def get_last_procedure_id():
        return Procedure.objects.filter().values("id").last()["id"]

    @staticmethod
    def get_procedure_by_id(procedure_id):
        return Procedure.objects.filter(id=procedure_id)

    def __str__(self):
        return f"{self.procedure_type} - {self.subject} - {self.headquarter} - {self.created_at} - {self.updated_at}"


class Procedure_ProcedureRequirement(models.Model):
    """
    Intermediate table between Procedure and ProcedureRequirement
    """

    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.CASCADE)
    requirement = models.ForeignKey(
        ProcedureRequirement, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "procedure_procedurerequirement"
        verbose_name_plural = "procedure_procedurerequirements"

    def __str__(self):
        return f"{self.procedure_type} - {self.requirement}"


class ProcedureTracing(models.Model):
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    referral_area = models.ForeignKey(Area, on_delete=models.CASCADE)
    action = models.TextField()
    is_started = models.BooleanField(default=False)
    is_revision = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "procedure tracing"
        verbose_name_plural = "procedure tracings"

    @staticmethod
    def get_tracing_by_procedure_id(procedure_id):
        return ProcedureTracing.objects.filter(procedure_id=procedure_id)

    @staticmethod
    def get_referral_area_by_procedure_id(procedure_id):
        return ProcedureTracing.objects.filter(procedure_id=procedure_id).values("referral_area_id").last()["referral_area_id"]

    def __str__(self):
        return f"{self.procedure_id} - {self.referral_area}"
