from django.db import models
from datetime import date
from util.models import Cliente, Impuesto  # Cliente e Impuesto desde util
from menus.models import Producto  # Producto desde menus
from pedidos.models import Pedido, ItemPedido  # Pedido e ItemPedido desde pedidos

# Modelo para la promoción
class Promocion(models.Model):
    descripcion = models.CharField(max_length=255)
    porcentaje_descuento = models.FloatField()
    tipo_clima = models.CharField(max_length=50,default="Desconocido", help_text="Ej: Lluvia, Soleado, Nublado")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.descripcion}-{self.porcentaje_descuento}%-{self.tipo_clima}"

# Modelo para la factura
class Factura(models.Model):
    numero = models.AutoField(primary_key=True)
    total = models.FloatField(default=0.0)
    subtotal = models.FloatField(default=0.0)
    impuesto_total = models.FloatField(default=0.0)
    descuento = models.FloatField(default=0.0)
    fecha = models.DateField(default=date.today)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)  # Relación con Pedido
    metodo_pago_efectivo = models.ForeignKey('PagoEfectivo', null=True, blank=True, on_delete=models.SET_NULL)
    metodo_pago_tarjeta = models.ForeignKey('PagoTarjeta', null=True, blank=True, on_delete=models.SET_NULL)
    metodo_pago_transferencia = models.ForeignKey('PagoTransferencia', null=True, blank=True, on_delete=models.SET_NULL)
    promocion = models.ForeignKey(Promocion, null=True, blank=True, on_delete=models.SET_NULL)

    def calcular_impuesto_total(self):
        impuesto_total = 0.0
        for item in self.pedido.itempedido_set.all():
            for impuesto in item.producto.impuestos.all():
                impuesto_total += item.subtotal() * (impuesto.porcentaje / 100)
        return impuesto_total

    def calcular_monto_total(self):
        self.subtotal = self.pedido.total_pedido()
        self.descuento = self.pedido.total_pedido() * (self.promocion.porcentaje_descuento / 100) if self.promocion else 0.0
        self.impuesto_total = self.calcular_impuesto_total()
        self.total = self.subtotal - self.descuento + self.impuesto_total

    def save(self, *args, **kwargs):
        self.calcular_monto_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.numero} para Pedido {self.pedido.numero} - Cliente: {self.pedido.cliente.nombre}"

# Modelo para los items de factura
class ItemFactura(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="items")
    item_pedido = models.ForeignKey(ItemPedido, on_delete=models.CASCADE)  # Relación con ItemPedido
    cantidad = models.PositiveIntegerField()
    subtotal = models.FloatField()

    def calcular_subtotal(self):
        self.subtotal = self.item_pedido.subtotal()  # Usa el subtotal de ItemPedido

    def save(self, *args, **kwargs):
        self.calcular_subtotal()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_pedido.producto.nombre} x {self.cantidad}"

# Modelo abstracto para métodos de pago
class MetodoDePago(models.Model):
    monto_pagado = models.FloatField()
    cuenta_por_cobrar = models.FloatField()

    class Meta:
        abstract = True

# Modelo para el pago por transferencia
class PagoTransferencia(MetodoDePago):
    numero_transferencia = models.CharField(max_length=50)
    banco_origen = models.CharField(max_length=255)

# Modelo para el pago en efectivo
class PagoEfectivo(MetodoDePago):
    cambio = models.FloatField()

# Modelo para el pago con tarjeta
class PagoTarjeta(MetodoDePago):
    numero_tarjeta = models.CharField(max_length=16)
    titular = models.CharField(max_length=255)
    vencimiento = models.DateField()

# Modelo para el historial de facturas
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
