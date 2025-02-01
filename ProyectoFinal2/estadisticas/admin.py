from django.contrib import admin
from .models import Factura, Estadistica, Reporte, Grafico

# Configuración de Factura en Admin
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'pedido', 'subtotal', 'impuesto_total', 'descuento', 'total')
    list_filter = ('fecha', 'pedido', 'mesero', 'mesa')  # 🔹 Referencias corregidas
    search_fields = ('numero', 'pedido__cliente__nombre', 'mesero__nombre', 'mesa__codigo')
    ordering = ('-fecha',)


# Configuración de Estadísticas en Admin
@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    ordering = ('-fecha_inicio',)

# Configuración de Reporte en Admin
@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('titulo',)
    ordering = ('-fecha_inicio',)

# Configuración de Gráficos en Admin
@admin.register(Grafico)
class GraficoAdmin(admin.ModelAdmin):
    list_display = ('titulo',)
    search_fields = ('titulo',)
    ordering = ('titulo',)
