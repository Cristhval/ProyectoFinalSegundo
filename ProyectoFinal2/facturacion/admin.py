from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Factura, ItemFactura, Promocion,
    PagoTransferencia, PagoEfectivo, PagoTarjeta,
    HistorialDeFactura
)


# --- CONFIGURACIÓN PARA PROMOCIÓN ---
@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'porcentaje_descuento', 'tipo_clima', 'activa', 'producto')
    list_filter = ('tipo_clima', 'activa')
    search_fields = ('descripcion', 'producto__nombre')


# --- CONFIGURACIÓN PARA ITEMS EN FACTURA ---
class ItemFacturaInline(admin.TabularInline):
    model = ItemFactura
    extra = 1
    readonly_fields = ('cantidad', 'subtotal')  # 🔹 Ahora no se pueden editar manualmente


# --- CONFIGURACIÓN PARA FACTURA ---
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'total_a_pagar', 'pedido')
    readonly_fields = ("total", "subtotal", "impuesto_total", "descuento")
    list_filter = ('fecha',)
    search_fields = ('numero', 'pedido__cliente__nombre')
    ordering = ('-fecha',)
    inlines = [ItemFacturaInline]
    filter_horizontal = ('promociones',)


# --- CONFIGURACIÓN PARA MÉTODOS DE PAGO ---
@admin.register(PagoTransferencia, PagoEfectivo, PagoTarjeta)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('monto_pagado',)


# 🔹 FILTRO PERSONALIZADO PARA CLIENTE 🔹
class ClienteFilter(admin.SimpleListFilter):
    title = _('Cliente')  # Nombre del filtro en el admin
    parameter_name = 'cliente'

    def lookups(self, request, model_admin):
        """Define las opciones disponibles en el filtro"""
        clientes = set(Factura.objects.values_list('cliente__id', 'cliente__nombre'))
        return [(cliente[0], cliente[1]) for cliente in clientes if cliente[0] is not None]

    def queryset(self, request, queryset):
        """Filtra las facturas por cliente seleccionado"""
        if self.value():
            return queryset.filter(factura__cliente__id=self.value())
        return queryset


# --- CONFIGURACIÓN PARA HISTORIAL DE FACTURA ---
@admin.register(HistorialDeFactura)
class HistorialFacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'factura', 'get_cliente', 'get_fecha', 'get_monto_pagado')
    search_fields = ('factura__numero', 'factura__pedido__cliente__nombre')
    list_filter = ('factura__fecha', 'factura__pedido__cliente', 'factura__total')

    def get_cliente(self, obj):
        """Muestra el nombre del cliente asociado a la factura"""
        return obj.factura.pedido.cliente.nombre if obj.factura.pedido and obj.factura.pedido.cliente else "Sin cliente"
    get_cliente.short_description = "Cliente"

    def get_fecha(self, obj):
        """Muestra la fecha de la factura"""
        return obj.factura.fecha if obj.factura else "No disponible"
    get_fecha.short_description = "Fecha"

    def get_monto_pagado(self, obj):
        """Muestra el monto total pagado en la factura"""
        return f"${obj.factura.total}" if obj.factura else "No disponible"
    get_monto_pagado.short_description = "Monto Pagado"