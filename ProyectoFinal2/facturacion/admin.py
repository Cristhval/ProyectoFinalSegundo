from django.contrib import admin
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


# --- CONFIGURACIÓN PARA HISTORIAL DE FACTURA ---
@admin.register(HistorialDeFactura)
class HistorialFacturaAdmin(admin.ModelAdmin):
    list_display = ('factura',)
    search_fields = ('factura__numero',)
