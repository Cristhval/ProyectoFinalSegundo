from django.db import models
from datetime import date
from util.models import Cliente, Impuesto
from menus.models import Producto
from pedidos.models import Pedido, ItemPedido


# --- MODELO PROMOCIÓN ---
class Promocion(models.Model):
    descripcion = models.CharField(max_length=255)
    porcentaje_descuento = models.FloatField()
    tipo_clima = models.CharField(max_length=50, default="Desconocido", help_text="Ej: Lluvia, Soleado, Nublado")
    activa = models.BooleanField(default=True)
    producto = models.ForeignKey(Producto, null=True, blank=True, on_delete=models.CASCADE,
                                 help_text="Dejar en blanco si aplica a toda la factura")

    def __str__(self):
        return f"{self.descripcion} - {self.porcentaje_descuento}% - {self.tipo_clima} {'(General)' if not self.producto else '(Específico)'}"


# --- MODELO FACTURA ---
class Factura(models.Model):
    numero = models.AutoField(primary_key=True)
    total = models.FloatField(default=0.0, editable=False)
    subtotal = models.FloatField(default=0.0, editable=False)
    impuesto_total = models.FloatField(default=0.0, editable=False)
    descuento = models.FloatField(default=0.0, editable=False)
    fecha = models.DateField(default=date.today)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    metodo_pago_efectivo = models.ForeignKey('PagoEfectivo', null=True, blank=True, on_delete=models.SET_NULL)
    metodo_pago_tarjeta = models.ForeignKey('PagoTarjeta', null=True, blank=True, on_delete=models.SET_NULL)
    metodo_pago_transferencia = models.ForeignKey('PagoTransferencia', null=True, blank=True, on_delete=models.SET_NULL)
    promociones = models.ManyToManyField(Promocion, blank=True)

    def calcular_impuesto_total(self):
        """Calcula el total de impuestos, excluyendo productos exentos de impuestos."""
        total_impuesto = sum(
            (item.item_pedido.producto.precio * item.cantidad) * (impuesto.porcentaje / 100)
            for item in self.items.all()
            for impuesto in item.item_pedido.producto.impuestos.all()
            if impuesto.porcentaje > 0  # Excluye productos sin impuestos
        )
        return round(total_impuesto, 2)

    def calcular_descuento_total(self):
        """Calcula el descuento total, aplicando promociones a productos específicos y descuentos generales."""
        descuento_total = 0.0
        for promo in self.promociones.all():
            if promo.producto:
                # Aplica descuento solo a productos específicos
                items_promo = self.items.filter(item_pedido__producto=promo.producto)
                descuento_total += sum(item.subtotal * (promo.porcentaje_descuento / 100) for item in items_promo)
            else:
                # Aplica descuento general
                descuento_total += self.subtotal * (promo.porcentaje_descuento / 100)
        return round(descuento_total, 2)

    def calcular_monto_total(self):
        """Calcula el total de la factura incluyendo impuestos y descuentos."""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.impuesto_total = self.calcular_impuesto_total()
        self.descuento = self.calcular_descuento_total()
        self.total = self.subtotal - self.descuento + self.impuesto_total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda la factura antes de asignarle los items

        # Verifica si la factura ya tiene items, si no, los crea
        if not self.items.exists():
            for item_pedido in self.pedido.items.all():
                ItemFactura.objects.create(
                    factura=self,
                    item_pedido=item_pedido,
                    cantidad=item_pedido.cantidad,  # Se usa la cantidad del ItemPedido
                    subtotal=item_pedido.cantidad * item_pedido.producto.precio
                )

    def total_a_pagar(self):
        return f"{self.total} (Impuestos incluidos: {self.impuesto_total})"

    def __str__(self):
        return f"Factura {self.numero} - {self.pedido.cliente.nombre if self.pedido and self.pedido.cliente else 'Sin Cliente'}"


# --- MODELO ITEM FACTURA ---
class ItemFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="items")
    item_pedido = models.ForeignKey(ItemPedido, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(editable=False)  # 🔹 Se calcula automáticamente
    subtotal = models.FloatField(editable=False)  # 🔹 Se calcula automáticamente

    def calcular_subtotal(self):
        """Calcula el subtotal incluyendo impuestos, permitiendo productos exentos de impuestos."""
        precio_unitario = self.item_pedido.producto.precio
        self.cantidad = self.item_pedido.cantidad  # 🔹 Obtiene la cantidad directamente del ItemPedido
        impuestos = sum(impuesto.porcentaje for impuesto in self.item_pedido.producto.impuestos.all()) / 100
        precio_con_impuestos = precio_unitario * (1 + impuestos)
        self.subtotal = round(precio_con_impuestos * self.cantidad, 2)

    def save(self, *args, **kwargs):
        self.calcular_subtotal()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_pedido.producto.nombre} x {self.cantidad} - Subtotal: {self.subtotal}"


# --- MODELOS DE PAGO ---
class MetodoDePago(models.Model):
    monto_pagado = models.FloatField()
    cuenta_por_cobrar = models.FloatField()

    class Meta:
        abstract = True


class PagoTransferencia(MetodoDePago):
    numero_transferencia = models.CharField(max_length=50)
    banco_origen = models.CharField(max_length=255)

    def __str__(self):
        return f"Transferencia {self.numero_transferencia} - {self.banco_origen}"


class PagoEfectivo(MetodoDePago):
    cambio = models.FloatField()

    def __str__(self):
        return f"Efectivo: {self.monto_pagado} - Cambio: {self.cambio}"


class PagoTarjeta(MetodoDePago):
    numero_tarjeta = models.CharField(max_length=16)
    titular = models.CharField(max_length=255)
    vencimiento = models.DateField()

    def __str__(self):
        return f"Tarjeta {self.numero_tarjeta[-4:]} - {self.titular}"


# --- MODELO HISTORIAL FACTURA ---
class HistorialDeFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)

    @classmethod
    def consultar_por_fecha(cls, fecha_inicio, fecha_fin):
        return cls.objects.filter(factura__fecha__range=[fecha_inicio, fecha_fin])

    @classmethod
    def consultar_por_cliente(cls, cliente):
        return cls.objects.filter(factura__pedido__cliente=cliente)

    def __str__(self):
        return f"Historial de Factura {self.factura.numero}"


