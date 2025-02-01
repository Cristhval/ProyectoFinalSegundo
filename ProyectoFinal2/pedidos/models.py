from enum import Enum
from django.db import models
from util.models import Cliente, Mesero, PersonalCocina
from menus.models import Producto, Menu
from mesas.models import Mesa
from abc import ABC, abstractmethod

# Enumerador de estados del pedido
class Estado(models.TextChoices):
    EN_PREPARACION = 'EN_PREPARACION'
    PAGADO = 'PAGADO'
    PENDIENTE = 'PENDIENTE'
    SERVIDO = 'SERVIDO'


# ✅ Interfaz corregida (sin models.Model)
class InteraccionPedido(ABC):
    @abstractmethod
    def actualizar_estado(self, estado: Estado, pedido: 'Pedido'):
        pass

    @abstractmethod
    def visualizar_estado(self, pedido: 'Pedido'):
        pass


class InteraccionCliente(ABC):  # ✅ Ya no hereda de models.Model
    @abstractmethod
    def agregar_cliente(self):
        pass

    @abstractmethod
    def anotar_pedido(self, pedido: 'Pedido'):
        pass

    @abstractmethod
    def asignar_mesa(self):
        pass

    @abstractmethod
    def atender_pedido(self):
        pass

    @abstractmethod
    def gestionar_pedido(self):
        pass

    @abstractmethod
    def mostrar_cuenta(self):
        pass

    @abstractmethod
    def mostrar_menu(self):
        pass

    @abstractmethod
    def realizar_reserva(self):
        pass


# Modelo para los ítems dentro de un pedido
class ItemPedido(models.Model):
    cantidad = models.PositiveIntegerField(default=1)
    observacion = models.CharField(max_length=100, blank=True, default='Ninguna')
    cliente = models.ForeignKey("util.Cliente", on_delete=models.CASCADE, related_name='item_pedido_list')
    producto = models.ForeignKey("menus.Producto", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"

    def subtotal(self):
        """Calcula el subtotal del item basado en cantidad y precio del producto"""
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} | {self.cantidad} | {self.cliente.nombre} | {self.observacion}"


# Modelo de Pedido
class Pedido(models.Model):
    fecha_actual = models.DateTimeField(auto_now=True)
    informacion = models.TextField(editable=False)
    numero = models.PositiveIntegerField(unique=True)
    mesa = models.ForeignKey("mesas.Mesa", null=True, blank=True, on_delete=models.SET_NULL)
    cliente = models.ForeignKey('util.Cliente', on_delete=models.CASCADE, related_name='pedidos_cliente', null=True)
    mesero = models.ForeignKey('util.Mesero', null=True, blank=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)
    item_pedido_list = models.ManyToManyField(ItemPedido, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = Pedido.objects.count() + 1
        super().save(*args, **kwargs)

    def agregar_item(self, item):
        self.item_pedido_list.add(item)
        self.save()

    def calcular_total(self):  # 🔹 Ahora se llama igual que en Factura
        return sum(item.producto.precio * item.cantidad for item in self.item_pedido_list.all())

    def mostrar_tiempo_espera(self):
        pass

    def registrar_informacion(self):
        pass

    def remover_item(self, item):
        self.item_pedido_list.remove(item)
        self.save()

    def __str__(self):
        return f"{self.numero} | {self.fecha_actual} | {self.estado}"


# Modelo de Historial de pedidos
class Historial(models.Model):
    pedidos = models.ManyToManyField("pedidos.Pedido", related_name="historial_pedidos")

    class Meta:
        verbose_name = "Historial"
        verbose_name_plural = "Historiales"

    def agregar_pedido(self, pedido):
        self.pedidos.add(pedido)
        self.save()

    def mostrar_informacion(self):
        return self.pedidos.all()

    def __str__(self):
        return f"Historial {self.id}"


# Modelo de Restaurante
class Restaurante(models.Model):  # ✅ Ya no hereda de InteraccionCliente
    nombre = models.CharField(max_length=50)
    clientes = models.ManyToManyField(Cliente, blank=True)
    meseros = models.ManyToManyField(Mesero, blank=True)
    personal_cocina_list = models.ManyToManyField(PersonalCocina, blank=True)
    pedidos = models.ManyToManyField(Pedido, blank=True)

    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"

    def agregar_cliente(self, cliente):
        self.clientes.add(cliente)
        self.save()

    def agregar_mesero(self, mesero):
        self.meseros.add(mesero)
        self.save()

    def agregar_personal_cocina(self, personal):
        self.personal_cocina_list.add(personal)
        self.save()

    def mostrar_historial(self):
        return Historial.objects.all()

    def mostrar_mesas_disponibles(self):
        return Mesa.objects.filter(estado="LIBRE")

    def mostrar_registro_historico(self):
        pass

    def remover_mesa(self, mesa):
        self.mesas.remove(mesa)
        self.save()

    def __str__(self):
        return self.nombre

    # Métodos implementados manualmente en lugar de heredar de InteraccionCliente
    def anotar_pedido(self, pedido: 'Pedido'):
        self.pedidos.add(pedido)
        self.save()

    def asignar_mesa(self):
        pass

    def atender_pedido(self):
        pass

    def gestionar_pedido(self):
        pass

    def mostrar_cuenta(self):
        pass

    def mostrar_menu(self):
        pass

    def realizar_reserva(self):
        pass


# Modelo de Registro Histórico de pedidos
class RegistroHistorico(models.Model):
    pedidos = models.ManyToManyField(Pedido, editable=False, blank=True)

    class Meta:
        verbose_name = "Registro Histórico"
        verbose_name_plural = "Registros Históricos"

    def registrar_pedido(self, pedido):
        self.pedidos.add(pedido)
        self.save()

    def mostrar_lista_pedidos(self):
        return self.pedidos.all()

    def __str__(self):
        return f"Registro Histórico {self.id}"
