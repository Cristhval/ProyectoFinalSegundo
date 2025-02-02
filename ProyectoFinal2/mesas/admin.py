from django.contrib import admin
from .models import Mesa, Reserva

# --- CONFIGURACIÓN PARA MESA ---
@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'numero_asientos', 'ubicacion', 'estado', 'hora_disponible')
    search_fields = ('identificador', 'ubicacion')
    list_filter = ('estado',)

# --- CONFIGURACIÓN PARA RESERVA ---
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'cliente', 'mesa', 'cantidad_personas', 'fecha_reserva', 'horario_inicio', 'estado')
    search_fields = ('identificador', 'cliente__nombre', 'mesa__identificador')
    list_filter = ('estado', 'fecha_reserva')

