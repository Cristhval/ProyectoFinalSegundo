from django.contrib import admin
from .models import (
    ItemPedido, Pedido, Historial, Restaurante, RegistroHistorico
)

# Configuración de ItemPedido en Admin
@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'cliente', 'observacion')
    search_fields = ('producto__nombre', 'cliente__nombre')
    list_filter = ('producto',)
    ordering = ('producto',)

# Configuración de Historial en Admin
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('id',)
    filter_horizontal = ('pedidos',)  # Permite una mejor gestión de los pedidos relacionados

# Configuración de Restaurante en Admin
@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    filter_horizontal = ('clientes', 'meseros', 'personal_cocina_list', 'pedidos')
    search_fields = ('nombre',)
    ordering = ('nombre',)

# Configuración de RegistroHistorico en Admin
@admin.register(RegistroHistorico)
class RegistroHistoricoAdmin(admin.ModelAdmin):
    list_display = ('id',)
    filter_horizontal = ('pedidos',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha_actual', 'cliente', 'mesero', 'mesa', 'estado')  # 🔹 Agregado mesero y mesa
    search_fields = ('numero', 'cliente__nombre', 'mesero__nombre')
    list_filter = ('estado', 'fecha_actual', 'mesero', 'mesa')
    ordering = ('-fecha_actual',)
    list_editable = ('estado',)

