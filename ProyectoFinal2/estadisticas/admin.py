from django.contrib import admin
from .models import Estadistica, Reporte, Grafico


@admin.register(Estadistica)
class EstadisticaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    search_fields = ('titulo', 'mejor_mesero', 'mesa_mas_usada', 'producto_mas_vendido')
    list_filter = ('fecha_inicio', 'fecha_fin')

    def save_model(self, request, obj, form, change):
        """Recalcula estadísticas antes de guardar."""
        obj.mejor_mesero = obj.calcular_mejor_mesero()
        obj.mesa_mas_usada = obj.calcular_mesa_mas_usada()
        obj.producto_mas_vendido = obj.calcular_producto_mas_vendido()
        obj.save()

    def actualizar_estadisticas(self, request, queryset):
        """Acción personalizada para recalcular estadísticas manualmente desde el admin."""
        for estadistica in queryset:
            estadistica.mejor_mesero = estadistica.calcular_mejor_mesero()
            estadistica.mesa_mas_usada = estadistica.calcular_mesa_mas_usada()
            estadistica.producto_mas_vendido = estadistica.calcular_producto_mas_vendido()
            estadistica.save()
        self.message_user(request, "Estadísticas actualizadas correctamente.")

    actions = [actualizar_estadisticas]


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin', 'tipo_reporte')
    search_fields = ('titulo',)
    list_filter = ('tipo_reporte',)

    def save_model(self, request, obj, form, change):
        """Genera estadísticas automáticamente si no existen."""
        estadistica = obj.generar_estadisticas()
        obj.save()


@admin.register(Grafico)
class GraficoAdmin(admin.ModelAdmin):
    list_display = ('titulo',)

    def generar_grafico(self, request, queryset):
        """Genera gráficos de ventas manualmente desde el admin."""
        for grafico in queryset:
            grafico.generar_grafico_ventas()
        self.message_user(request, "Gráficos generados correctamente.")

    actions = [generar_grafico]
