from django.contrib import admin
from .models import Pedido, ItemPedido, Historial, Restaurante, RegistroHistorico

# --- CONFIGURACIÓN PARA ITEM PEDIDO ---
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1  # 🔹 Permite agregar más ítems dentro del pedido


# --- CONFIGURACIÓN PARA PEDIDO ---
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'mesero', 'estado', 'fecha_actual', 'calcular_total')
    list_filter = ('estado', 'fecha_actual')
    search_fields = ('numero', 'cliente__nombre', 'mesero__nombre')
    ordering = ('-fecha_actual',)
    inlines = [ItemPedidoInline]

    def calcular_total(self, obj):
        return obj.calcular_total()
    calcular_total.short_description = "Total Pedido"


# --- CONFIGURACIÓN PARA ITEM PEDIDO ---
@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cliente', 'producto', 'cantidad', 'calcular_subtotal')
    list_filter = ('pedido', 'cliente')
    search_fields = ('pedido__numero', 'cliente__nombre', 'producto__nombre')

    def calcular_subtotal(self, obj):
        return obj.calcular_subtotal()
    calcular_subtotal.short_description = "Subtotal"


# --- CONFIGURACIÓN PARA HISTORIAL ---
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'mostrar_pedidos')
    filter_horizontal = ('pedidos',)  # 🔹 Permite selección múltiple en admin

    def mostrar_pedidos(self, obj):
        return ", ".join([str(pedido) for pedido in obj.pedidos.all()])
    mostrar_pedidos.short_description = "Pedidos en el Historial"


# --- CONFIGURACIÓN PARA RESTAURANTE ---
@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cantidad_clientes', 'cantidad_meseros', 'cantidad_pedidos')
    filter_horizontal = ('clientes', 'meseros', 'personal_cocina', 'pedidos')

    def cantidad_clientes(self, obj):
        return obj.clientes.count()
    cantidad_clientes.short_description = "Clientes"

    def cantidad_meseros(self, obj):
        return obj.meseros.count()
    cantidad_meseros.short_description = "Meseros"

    def cantidad_pedidos(self, obj):
        return obj.pedidos.count()
    cantidad_pedidos.short_description = "Pedidos"


# --- CONFIGURACIÓN PARA REGISTRO HISTÓRICO ---
@admin.register(RegistroHistorico)
class RegistroHistoricoAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_registro', 'mostrar_lista_pedidos')
    filter_horizontal = ('pedidos',)  # 🔹 Permite selección múltiple en admin

    def mostrar_lista_pedidos(self, obj):
        return ", ".join([str(pedido) for pedido in obj.pedidos.all()])
    mostrar_lista_pedidos.short_description = "Pedidos en el Registro"
