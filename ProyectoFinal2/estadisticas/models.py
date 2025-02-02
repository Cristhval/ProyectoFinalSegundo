from django.db import models
from django.db.models import Count, Sum
from datetime import date
from facturacion.models import Factura, ItemFactura
from pedidos.models import Pedido
from util.models import Cliente, Mesero
from menus.models import Producto
from mesas.models import Mesa
import matplotlib
import matplotlib.pyplot as plt
import io
import base64

# 🔹 Evita problemas de hilos en Django
matplotlib.use("Agg")

# --- MODELO ESTADISTICA ---
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
        mesero_mas_activo = (
            facturas.values('pedido__mesero__nombre')
            .annotate(total_pedidos=Count('pedido'))
            .order_by('-total_pedidos')
            .first()
        )
        return mesero_mas_activo['pedido__mesero__nombre'] if mesero_mas_activo else "No hay datos"

    def calcular_mesa_mas_usada(self):
        facturas = Factura.objects.filter(fecha__range=[self.fecha_inicio, self.fecha_fin])
        mesa_mas_usada = (
            facturas.values('pedido__mesa__identificador')
            .annotate(total=Count('pedido'))
            .order_by('-total')
            .first()
        )
        return mesa_mas_usada['pedido__mesa__identificador'] if mesa_mas_usada else "No hay datos"

    def calcular_producto_mas_vendido(self):
        item_facturas = ItemFactura.objects.filter(factura__fecha__range=[self.fecha_inicio, self.fecha_fin])
        producto_mas_vendido = (
            item_facturas.values('item_pedido__producto__nombre')
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')
            .first()
        )
        return producto_mas_vendido['item_pedido__producto__nombre'] if producto_mas_vendido else "No hay datos"

    def save(self, *args, **kwargs):
        self.mejor_mesero = self.calcular_mejor_mesero()
        self.mesa_mas_usada = self.calcular_mesa_mas_usada()
        self.producto_mas_vendido = self.calcular_producto_mas_vendido()
        super().save(*args, **kwargs)

# --- MODELO REPORTE ---
class Reporte(models.Model):
    titulo = models.CharField(max_length=50)
    fecha_inicio = models.DateField(default=date.today)
    fecha_fin = models.DateField(default=date.today)
    tipo_reporte = models.CharField(
        max_length=10,
        choices=[("DIARIO", "Diario"), ("SEMANAL", "Semanal"), ("MENSUAL", "Mensual")],
        default="MENSUAL"
    )

    def generar_estadisticas(self):
        estadistica, created = Estadistica.objects.get_or_create(
            fecha_inicio=self.fecha_inicio, fecha_fin=self.fecha_fin
        )
        return estadistica if not created else "No hay estadísticas disponibles."

    def __str__(self):
        return f"Reporte {self.titulo} - {self.tipo_reporte}"

# --- MODELO GRAFICO ---
class Grafico(models.Model):
    titulo = models.CharField(max_length=50)

    def generar_grafico_ventas(self):
        ventas = ItemFactura.objects.values("item_pedido__producto__nombre").annotate(total_vendido=Sum("cantidad"))
        productos = [venta["item_pedido__producto__nombre"] for venta in ventas]
        cantidades = [venta["total_vendido"] for venta in ventas]

        if not productos or not cantidades:
            return "No hay datos suficientes para generar un gráfico."

        matplotlib.use("Agg")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(productos, cantidades, color="blue")
        ax.set_xlabel("Producto")
        ax.set_ylabel("Cantidad Vendida")
        ax.set_title("Ventas por Producto")
        plt.xticks(rotation=45, ha="right")

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)

        return f'<img src="data:image/png;base64,{img_str}" />'

    def __str__(self):
        return self.titulo
