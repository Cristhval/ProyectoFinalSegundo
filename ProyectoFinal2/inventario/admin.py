from django.contrib import admin
from .models import (
    Insumo, Operacion, Historial, Alerta, ReporteConsumo,
    Inventario, ReporteBodega
)

# Configuración de Insumos en Admin
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'nombre', 'cantidadDisponible', 'unidadMedida', 'nivelReorden', 'precioUnitario', 'ubicacion')
    search_fields = ('nombre', 'identificador')
    list_filter = ('unidadMedida',)
    ordering = ('nombre',)

# Configuración de Operaciones de Inventario en Admin
@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'insumo', 'cantidad', 'fechaRegistro', 'observaciones')
    list_filter = ('tipo', 'fechaRegistro')
    search_fields = ('insumo__nombre',)
    ordering = ('-fechaRegistro',)

# Configuración del Historial de Inventario en Admin
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('operacion', 'descripcion')
    search_fields = ('operacion__insumo__nombre',)
    ordering = ('operacion__fechaRegistro',)

# Configuración de Alertas en Admin
@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('mensaje', 'fecha', 'tipo')
    list_filter = ('tipo', 'fecha')
    search_fields = ('mensaje',)

# Configuración de Reportes de Consumo en Admin
@admin.register(ReporteConsumo)
class ReporteConsumoAdmin(admin.ModelAdmin):
    list_display = ('periodoInicio', 'periodoFin', 'datos')
    search_fields = ('periodoInicio', 'periodoFin')
    ordering = ('-periodoInicio',)

# Configuración del Inventario en Admin
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('almacenamiento',)
    search_fields = ('almacenamiento',)

# Configuración de Reportes de Bodega en Admin
@admin.register(ReporteBodega)
class ReporteBodegaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'datos')
    search_fields = ('tipo',)
