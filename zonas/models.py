from django.db import models
# Create your models here.


class Pais(models.Model):
    nombre = models.CharField(max_length=50)
    iso = models.CharField(max_length=10)
    nacionalidad = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.iso}"


class Region(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.codigo}"


class Provincia(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.codigo}"


class Distrito(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10)
    ubigeo = models.CharField(max_length=6)
    is_active = models.BooleanField(default=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} - {self.codigo}"
