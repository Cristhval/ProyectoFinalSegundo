from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date
from django.shortcuts import render
from facturacion.models import Factura, ItemFactura  # Facturación
from pedidos.models import Pedido  # Pedidos
from util.models import Persona, Cliente, Mesero  # Util
from menus.models import Producto  # Menús
from mesas.models import Mesa  # Mesas

# Modelo para Producto (ya importado desde Menús, se mantiene para referencia)
class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precio = models.FloatField()
    categoria = models.CharField(max_length=50)
    cantidad_vendida = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def actualizar_cantidad_vendida(self):
        self.cantidad_vendida = (
            ItemFactura.objects.filter(producto=self).aggregate(cantidad_vendida=models.Sum('cantidad'))['cantidad_vendida'] or 0
        )
        self.save()

# Modelo para Factura
class Factura(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    fecha = models.DateField()
    impuesto_total = models.FloatField(default=0.0)
    descuento = models.FloatField()
    subtotal = models.FloatField(default=0)
    total = models.FloatField(default=0)
    mesero = models.ForeignKey('util.Mesero', null=True, blank=True, on_delete=models.SET_NULL)
    mesa = models.ForeignKey('mesas.Mesa', null=True, blank=True, on_delete=models.SET_NULL)
    pedido = models.ForeignKey('pedidos.Pedido', on_delete=models.CASCADE, related_name="facturas_estadisticas")  # 🔹 Se corrigió related_name

    def __str__(self):
        return self.numero

    def calcular_subtotal(self):
        if self.pedido:
            self.subtotal = self.pedido.calcular_total()
        else:
            self.subtotal = 0.0

    def calcular_total(self):
        self.total = self.subtotal + self.impuesto_total - self.descuento

    def save(self, *args, **kwargs):
        self.calcular_subtotal()
        self.calcular_total()
        super().save(*args, **kwargs)

@receiver(post_save, sender=Factura)
def actualizar_pedidos_mesero(sender, instance, **kwargs):
    if instance.mesero:
        instance.mesero.actualizar_pedidos_atendidos()
# Modelo para Estadísticas
class Estadistica(models.Model):
    titulo = models.CharField(max_length=50)
    fecha_inicio = models.DateField(default=date.today)
    fecha_fin = models.DateField(default=date.today)
    mejor_mesero = models.CharField(max_length=50, blank=True, null=True)
    mesa_mas_usada = models.CharField(max_length=50, blank=True, null=True)
    producto_mas_vendido = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} ({self.fecha_inicio} - {self.fecha_fin})"

    def calcular_mejor_mesero(self):
        facturas = Factura.objects.filter(fecha__range=[self.fecha_inicio, self.fecha_fin])
        mejor_mesero = (
            facturas.values('mesero')
            .annotate(total=models.Count('id'))
            .order_by('-total')
            .first()
        )
        if mejor_mesero:
            mesero = Mesero.objects.get(id=mejor_mesero['mesero'])
            return mesero.nombre
        return "No hay datos"

    def calcular_mesa_mas_usada(self):
        facturas = Factura.objects.filter(fecha__range=[self.fecha_inicio, self.fecha_fin])
        mesa_mas_usada = (
            facturas.values('mesa')
            .annotate(total=models.Count('id'))
            .order_by('-total')
            .first()
        )
        if mesa_mas_usada:
            mesa = Mesa.objects.get(id=mesa_mas_usada['mesa'])
            return mesa.codigo
        return "No hay datos"

    def calcular_producto_mas_vendido(self):
        item_facturas = ItemFactura.objects.filter(
            factura__fecha__range=[self.fecha_inicio, self.fecha_fin]
        )
        producto_mas_vendido = (
            item_facturas.values('producto')
            .annotate(total_vendido=models.Sum('cantidad'))
            .order_by('-total_vendido')
            .first()
        )
        if producto_mas_vendido:
            producto = Producto.objects.get(id=producto_mas_vendido['producto'])
            return producto.nombre
        return "No hay datos"

    def save(self, *args, **kwargs):
        self.mejor_mesero = self.calcular_mejor_mesero()
        self.mesa_mas_usada = self.calcular_mesa_mas_usada()
        self.producto_mas_vendido = self.calcular_producto_mas_vendido()
        super().save(*args, **kwargs)

class Reporte(models.Model):
    titulo = models.CharField(max_length=50)
    grafico = models.ForeignKey('Grafico', related_name='reporte', on_delete=models.CASCADE, null=True)

    fecha_inicio = models.DateField(default=date.today)
    fecha_fin = models.DateField(default=date.today)

    class TipoReporte(models.TextChoices):
        DIARIO = 'DIARIO'
        SEMANAL = 'SEMANAL'
        MENSUAL = 'MENSUAL'

    class TipoArchivo(models.TextChoices):
        PDF = 'PDF'
        IMAGEN = 'IMAGEN'

    def generar_estadisticas(self):
        # Crear un diccionario para recopilar datos
        datos = {
            "mejor_mesero": {},
            "mesas_usadas": [],
            "productos_vendidos": []
        }

        # Obtener datos para "Mejor Mesero"
        facturas = Factura.objects.filter(fecha__range=[self.fecha_inicio, self.fecha_fin])
        meseros = (
            facturas.values('mesero__nombre')
            .annotate(total=models.Count('id'))
            .order_by('-total')
        )
        if meseros.exists():
            datos["mejor_mesero"]["nombre"] = meseros[0]['mesero__nombre']
            datos["mejor_mesero"]["cantidad"] = meseros[0]['total']
            datos["mejor_mesero"]["detalles"] = list(meseros)

        # Obtener datos para "Mesa más usada"
        mesas = (
            facturas.values('mesa__codigo')
            .annotate(total=models.Count('id'))
            .order_by('-total')
        )
        if mesas.exists():
            datos["mesas_usadas"] = list(mesas)

        # Obtener datos para "Producto más vendido"
        item_facturas = ItemFactura.objects.filter(factura__fecha__range=[self.fecha_inicio, self.fecha_fin])
        productos = (
            item_facturas.values('producto__nombre')
            .annotate(total_vendido=models.Sum('cantidad'))
            .order_by('-total_vendido')
        )
        if productos.exists():
            datos["productos_vendidos"] = list(productos)

        return datos

    def imprimir_reporte(self, request):
        # Generar las estadísticas detalladas
        estadisticas = self.generar_estadisticas()

        # Renderizar un template HTML con las estadísticas
        return render(request, 'reporte.html', {
            'titulo': self.titulo,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'estadisticas': estadisticas
        })

    class TipoReporte(models.TextChoices):
        DIARIO = 'DIARIO'
        SEMANAL = 'SEMANAL'
        MENSUAL = 'MENSUAL'

    class TipoArchivo(models.TextChoices):
        PDF = 'PDF'
        IMAGEN = 'IMAGEN'

    def agregar_estadistica(Estadistica):
        pass

    def generar_ventas_totales(self):
        pass

    def visualizar_reporte(self):
        pass

    def exportar_reporte(self):
        pass

class Grafico(models.Model):
    titulo = models.CharField(max_length=50)

    def __str__(self):
        return self.titulo

    def generar_pastel(self):
        pass