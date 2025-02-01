from django.contrib import admin
from .models import (
    Factura, ItemFactura, MetodoDePago, PagoTransferencia,
    PagoEfectivo, PagoTarjeta, HistorialDeFactura, Promocion
)

# Configuración de Promoción en Admin
@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('descripcion', 'porcentaje_descuento', 'tipo_clima', 'activa')  # 🔹 Agregar 'activa' para control de estado
    list_filter = ('tipo_clima', 'activa')  # 🔹 Facilita la búsqueda por clima y estado
    search_fields = ('descripcion', 'tipo_clima')  # 🔹 Permite búsqueda rápida
    ordering = ('descripcion',)
    list_editable = ('activa',)  # 🔹 Permite cambiar el estado directamente desde la lista

def calcular_total(obj):
    return round(obj.total, 2)  # Mostrar total redondeado
calcular_total.short_description = "Total"

def calcular_subtotal(obj):
    return round(obj.subtotal, 2)
calcular_subtotal.short_description = "Subtotal"

def calcular_impuesto(obj):
    return round(obj.impuesto_total, 2)
calcular_impuesto.short_description = "Impuesto Total"

def calcular_descuento(obj):
    return round(obj.descuento, 2)
calcular_descuento.short_description = "Descuento"

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'pedido', calcular_subtotal, calcular_impuesto, calcular_descuento, calcular_total)
    list_filter = ('fecha', 'pedido')
    search_fields = ('numero', 'pedido__cliente__nombre')
    ordering = ('-fecha',)

    def save_model(self, request, obj, form, change):
        obj.save()  # Esto forzará el cálculo antes de guardar

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
    list_display = ('monto_pagado', 'cambio')  # 🔹 Eliminado 'cuenta_por_cobrar'


@admin.register(PagoTarjeta)
class PagoTarjetaAdmin(admin.ModelAdmin):
    list_display = ('numero_tarjeta', 'titular', 'vencimiento', 'monto_pagado', 'cuenta_por_cobrar')
    search_fields = ('numero_tarjeta', 'titular')

# Configuración del Historial de Facturas en Admin
@admin.register(HistorialDeFactura)
class HistorialDeFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura',)
    search_fields = ('factura__numero',)