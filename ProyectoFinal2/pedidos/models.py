from django.db import models
from django.db.models import Sum, F
from util.models import Cliente, Mesero, PersonalCocina
from menus.models import Producto
from mesas.models import Mesa

class EstadoPedido(models.TextChoices):
    EN_PREPARACION = "EN_PREPARACION"
    PAGADO = "PAGADO"
    PENDIENTE = "PENDIENTE"
    PREPARADO = "PREPARADO"
    SERVIDO = "SERVIDO"
    RESERVADO = "RESERVADO"

# --- MODELO ITEM PEDIDO ---
class ItemPedido(models.Model):
    cantidad = models.PositiveIntegerField(default=1)
    observacion = models.CharField(max_length=100, blank=True, default='Ninguna')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='items_pedido')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey("pedidos.Pedido", on_delete=models.CASCADE, related_name="items")

        # 🔹 Campos para guardar el Pokémon asignado a la Cajita Feliz
    pokemon_id = models.PositiveIntegerField(null=True, blank=True)
    pokemon_nombre = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Item del Pedido"
        verbose_name_plural = "Items del Pedido"

    def calcular_subtotal(self):
        """Calcula el subtotal del ítem (precio * cantidad) y maneja `None` en precio."""
        return (self.producto.precio or 0) * self.cantidad

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} - Cliente: {self.cliente.nombre}"

# --- MODELO PEDIDO ---
class Pedido(models.Model):
    fecha_actual = models.DateTimeField(auto_now=True, editable=False)
    numero = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="pedidos_cliente")
    mesero = models.ForeignKey(Mesero, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="pedidos_mesero")
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos_mesa")
    estado = models.CharField(
        max_length=50,
        choices=EstadoPedido.choices,
        default=EstadoPedido.PENDIENTE
    )

    def calcular_total(self):
        """Optimiza el cálculo del total usando `aggregate`."""
        total = self.items.aggregate(total=Sum(F('producto__precio') * F('cantidad')))['total']
        return total if total else 0.0

    def __str__(self):
        return f"Pedido {self.numero} - {self.estado}"

# --- MODELO HISTORIAL ---
class Historial(models.Model):
    pedidos = models.ManyToManyField(Pedido)

    class Meta:
        verbose_name = "Historial"
        verbose_name_plural = "Historiales"

    def agregar_pedido(self, pedido):
        self.pedidos.add(pedido)
        self.save()

    def __str__(self):
        return f"Historial {self.id}"

# --- MODELO RESTAURANTE ---
class Restaurante(models.Model):
    nombre = models.CharField(max_length=50)
    clientes = models.ManyToManyField(Cliente, blank=True)
    meseros = models.ManyToManyField(Mesero, blank=True)
    personal_cocina = models.ManyToManyField(PersonalCocina, blank=True)
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
        self.personal_cocina.add(personal)
        self.save()

    def mostrar_historial(self):
        return Historial.objects.all()

    def mostrar_mesas_disponibles(self):
        return Mesa.objects.filter(estado="LIBRE")

    def __str__(self):
        return self.nombre

# --- MODELO REGISTRO HISTÓRICO ---
class RegistroHistorico(models.Model):
    pedidos = models.ManyToManyField(Pedido, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def registrar_pedido(self, pedido):
        self.pedidos.add(pedido)
        self.save()

    def mostrar_lista_pedidos(self):
        return "\n".join([str(pedido) for pedido in self.pedidos.all()])

    def __str__(self):
        return f"Registro {self.id} - {self.fecha_registro.strftime('%d-%m-%Y %H:%M')}"


