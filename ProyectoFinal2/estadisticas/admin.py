from django.contrib import admin
from .models import Estadistica, Reporte, Grafico  # ❌ Se eliminó Factura

# Configuración de Estadísticas en Admin
@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('titulo',)
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
