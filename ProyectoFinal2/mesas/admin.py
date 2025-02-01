from django.contrib import admin
from .models import Mesa, Reserva

# Configuración de Mesa en Admin
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'numero_asientos', 'ubicacion', 'estado', 'hora_disponible')
    list_filter = ('estado', 'ubicacion')
    search_fields = ('identificador', 'ubicacion')
    ordering = ('identificador',)
    list_editable = ('estado',)

# Configuración de Reserva en Admin
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'cliente', 'mesa', 'cantidad_personas', 'fecha_reserva', 'horario_inicio', 'estado')
    list_filter = ('estado', 'fecha_reserva')
    search_fields = ('identificador', 'cliente__nombre', 'mesa__identificador')
    ordering = ('fecha_reserva',)
    list_editable = ('estado',)