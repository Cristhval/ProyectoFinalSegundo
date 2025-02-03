from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from util.models import Administrador, Proveedor
from pedidos.models import Pedido
from menus.models import Producto

# --- MODELO INSUMO ---
class Insumo(models.Model):
    identificador = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    cantidadDisponible = models.IntegerField(default=0)
    unidadMedida = models.CharField(max_length=30)
    nivelReorden = models.IntegerField()
    precioUnitario = models.FloatField()
    ubicacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.identificador} - {self.nombre} ({self.cantidadDisponible} {self.unidadMedida})"

    def verificar_nivel_reorden(self):
        """Genera una alerta si la cantidad disponible está por debajo del nivel de reorden."""
        if self.cantidadDisponible < self.nivelReorden:
            Alerta.objects.create(
                mensaje=f"Insumo '{self.nombre}' bajo el nivel de reorden, reabastezca.",
                fecha=timezone.now(),
                tipo='bajo_stock'
            )

# --- MODELO OPERACION ---
class Operacion(models.Model):
    TIPO_OPERACION_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_OPERACION_CHOICES)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name="operaciones")
    cantidad = models.IntegerField()
    fechaRegistro = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.insumo.nombre} ({self.cantidad} {self.insumo.unidadMedida})"

# --- MODELO HISTORIAL ---
class Historial(models.Model):
    operacion = models.OneToOneField(Operacion, on_delete=models.CASCADE, related_name="historial")
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial de {self.operacion}"

# --- MODELO ALERTA ---
class Alerta(models.Model):
    mensaje = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    TIPO_ALERTA_CHOICES = [
        ('bajo_stock', 'Bajo Stock'),
        ('vencimiento', 'Vencimiento'),
    ]
    tipo = models.CharField(max_length=50, choices=TIPO_ALERTA_CHOICES)

    def __str__(self):
        return f"[{self.tipo.upper()}] {self.mensaje} ({self.fecha.strftime('%d-%m-%Y %H:%M')})"

# --- MODELO REPORTE CONSUMO ---
class ReporteConsumo(models.Model):
    periodoInicio = models.DateField()
    periodoFin = models.DateField()
    datos = models.TextField(blank=True)

    def generarReporte(self):
        """Generar un reporte con los insumos más utilizados."""
        operaciones = Operacion.objects.filter(
            tipo='salida',
            fechaRegistro__gte=self.periodoInicio,
            fechaRegistro__lte=self.periodoFin
        ).values('insumo__nombre').annotate(total=models.Sum('cantidad')).order_by('-total')

        reporte = "\n".join([f"{op['insumo__nombre']}: {op['total']} unidades" for op in operaciones])
        self.datos = reporte
        self.save()
        return reporte

    def __str__(self):
        return f"Reporte de consumo ({self.periodoInicio} - {self.periodoFin})"

# --- MODELO INVENTARIO ---
class Inventario(models.Model):
    almacenamiento = models.CharField(max_length=200)

    def __str__(self):
        return f"Inventario en {self.almacenamiento}"

# --- MODELO REPORTE BODEGA ---
class ReporteBodega(models.Model):
    tipo = models.CharField(max_length=100)
    datos = models.TextField()

    def generarReporte(self):
        pass

    def actualizarReporte(self):
        pass

    def __str__(self):
        return f"Reporte de bodega ({self.tipo})"

# --- ACTUALIZACIÓN AUTOMÁTICA DEL INVENTARIO ---
@receiver(post_save, sender=Operacion)
def actualizar_inventario(sender, instance, **kwargs):
    """Actualizar la cantidad disponible en los insumos con cada operación de inventario."""
    insumo = instance.insumo
    if instance.tipo == 'entrada':
        insumo.cantidadDisponible += instance.cantidad
    elif instance.tipo == 'salida':
        insumo.cantidadDisponible -= instance.cantidad
    insumo.save()

    # Registrar en el historial
    historial, created = Historial.objects.get_or_create(
        operacion=instance,
        defaults={'descripcion': f"Se realizó una operación de {instance.tipo} con {instance.cantidad} de '{insumo.nombre}'."}
    )

    # Verificar niveles de reorden después de actualizar el inventario
    insumo.verificar_nivel_reorden()
