from django.contrib import admin
from .models import Insumo, Operacion, Historial, Alerta, ReporteConsumo, Inventario, ReporteBodega

# --- CONFIGURACIÓN PARA INSUMO ---
@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'nombre', 'cantidadDisponible', 'unidadMedida', 'nivelReorden', 'ubicacion')
    search_fields = ('identificador', 'nombre')
    list_filter = ('unidadMedida', 'ubicacion')
    ordering = ('identificador',)

# --- CONFIGURACIÓN PARA OPERACION ---
@admin.register(Operacion)
class OperacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'insumo', 'cantidad', 'fechaRegistro')
    list_filter = ('tipo', 'fechaRegistro')
    search_fields = ('insumo__nombre',)
    ordering = ('-fechaRegistro',)

# --- CONFIGURACIÓN PARA HISTORIAL ---
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('operacion', 'descripcion')
    search_fields = ('operacion__insumo__nombre',)

# --- CONFIGURACIÓN PARA ALERTA ---
@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'mensaje', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('mensaje',)

# --- CONFIGURACIÓN PARA REPORTE CONSUMO ---
@admin.register(ReporteConsumo)
class ReporteConsumoAdmin(admin.ModelAdmin):
    list_display = ('periodoInicio', 'periodoFin')
    search_fields = ('periodoInicio', 'periodoFin')
    ordering = ('-periodoInicio',)

# --- CONFIGURACIÓN PARA INVENTARIO ---
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('almacenamiento',)
    search_fields = ('almacenamiento',)

# --- CONFIGURACIÓN PARA REPORTE BODEGA ---
@admin.register(ReporteBodega)
class ReporteBodegaAdmin(admin.ModelAdmin):
    list_display = ('tipo',)
    search_fields = ('tipo',)
