from django.contrib import admin
from .models import Estadistica, Reporte, Grafico

@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    search_fields = ('titulo', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    list_filter = ('fecha_inicio', 'fecha_fin')

    def save_model(self, request, obj, form, change):
        """Recalcula estadísticas antes de guardar."""
        obj.save()

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'tipo_reporte')
    search_fields = ('titulo',)
    list_filter = ('tipo_reporte',)

@admin.register(Grafico)
class GraficoAdmin(admin.ModelAdmin):
    list_display = ('titulo',)
