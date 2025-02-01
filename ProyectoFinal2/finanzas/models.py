from django.db import models


class Impuesto(models.Model):
    nombre = models.CharField(max_length=50)  # Ejemplo: IVA, ICE
    porcentaje = models.FloatField()  # Por ejemplo: 12.0 para el IVA
    descripcion = models.TextField(blank=True, null=True)  # Opcional para más detalles

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje}%"