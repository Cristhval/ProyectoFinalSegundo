from django.contrib import admin
from .models import (
    Factura, ItemFactura, MetodoDePago, PagoTransferencia,
    PagoEfectivo, PagoTarjeta, HistorialDeFactura, Promocion
)

# Configuración de Promoción en Admin
@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'porcentaje_descuento')
    search_fields = ('descripcion',)
    ordering = ('descripcion',)

# Configuración de Factura en Admin
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'pedido', 'subtotal', 'impuesto_total', 'descuento', 'total')
    list_filter = ('fecha', 'pedido')
    search_fields = ('numero', 'pedido__cliente__nombre')
    ordering = ('-fecha',)

# Configuración de Items de Factura en Admin
@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura', 'item_pedido', 'cantidad', 'subtotal')
    list_filter = ('factura',)
    search_fields = ('factura__numero', 'item_pedido__producto__nombre')

# Configuración de Métodos de Pago en Admin
@admin.register(PagoTransferencia)
class PagoTransferenciaAdmin(admin.ModelAdmin):
    list_display = ('numero_transferencia', 'banco_origen', 'monto_pagado', 'cuenta_por_cobrar')
    search_fields = ('numero_transferencia', 'banco_origen')

@admin.register(PagoEfectivo)
class PagoEfectivoAdmin(admin.ModelAdmin):
    list_display = ('monto_pagado', 'cambio', 'cuenta_por_cobrar')
    search_fields = ('monto_pagado',)

@admin.register(PagoTarjeta)
class PagoTarjetaAdmin(admin.ModelAdmin):
    list_display = ('numero_tarjeta', 'titular', 'vencimiento', 'monto_pagado', 'cuenta_por_cobrar')
    search_fields = ('numero_tarjeta', 'titular')

# Configuración del Historial de Facturas en Admin
@admin.register(HistorialDeFactura)
class HistorialDeFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura',)
    search_fields = ('factura__numero',)
