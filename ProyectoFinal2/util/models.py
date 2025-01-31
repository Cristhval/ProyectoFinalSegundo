from django.db import models
from enum import Enum
from django.contrib.auth.models import AbstractUser

# Enumerador para roles de personal
class Rol(Enum):
    MESERO = "MESERO"
    SECRETARIO = "SECRETARIO"
    ADMINISTRADOR = "ADMINISTRADOR"
    COCINERO = "COCINERO"

# Modelo base para Persona
class Persona(models.Model):
    cedula = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=50)
    edad = models.IntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True  # Se marca como abstracta para que no se cree en la BD

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"

    def validar_datos(self):
        """Verifica que la cédula y el teléfono sean válidos."""
        if len(self.cedula) not in [10, 13]:
            raise ValueError("La cédula debe tener 10 o 13 dígitos.")
        if len(self.telefono) < 7:
            raise ValueError("El número de teléfono no es válido.")

    def actualizar_datos(self, nombre=None, apellido=None, telefono=None, email=None, direccion=None):
        """Actualiza los datos personales de la persona."""
        if nombre:
            self.nombre = nombre
        if apellido:
            self.apellido = apellido
        if telefono:
            self.telefono = telefono
        if email:
            self.email = email
        if direccion:
            self.direccion = direccion
        self.save()

# Modelo Cliente
class Cliente(Persona):
    activo = models.BooleanField(default=True)
    historial_pedidos = models.ManyToManyField('pedidos.Pedido', blank=True, related_name='clientes_historial')

    def realizar_pedido(self, pedido):
        self.historial_pedidos.add(pedido)

    def modificar_pedido(self, pedido, nuevo_estado):
        pedido.actualizar_estado(nuevo_estado)

    def realizar_pago(self, factura):
        factura.calcular_total()

    def consultar_historial(self):
        """Devuelve una lista de pedidos del cliente."""
        return self.historial_pedidos.all()

    def hacer_reserva(self, datos_reserva):
        from mesas.models import Reserva
        reserva = Reserva.objects.create(
            cliente=self,
            mesa=datos_reserva['mesa'],
            cantidad_personas=datos_reserva['cantidad_personas'],
            fecha_reserva=datos_reserva['fecha_reserva'],
            horario_inicio=datos_reserva['horario_inicio']
        )
        reserva.save()
        return reserva


# Modelo Empleado (hereda de Persona)
class Empleado(Persona):
    identificacion = models.CharField(max_length=7, unique=True, null=True, editable=False)
    rol = models.CharField(
        max_length=15,
        choices=[(tag.name, tag.value) for tag in Rol],
        default=Rol.MESERO.name
    )

    class Meta:
        abstract = True  # Se mantiene abstracto en Django

    def actualizar_estado(self, estado, pedido):
        """Metodo que se sobrescribe en las clases hijas."""
        raise NotImplementedError("Este método debe ser implementado en una subclase.")

    def visualizar_estado(self, pedido):
        """Metodo que se sobrescribe en las clases hijas."""
        raise NotImplementedError("Este método debe ser implementado en una subclase.")
# Modelo Mesero
class Mesero(Empleado):
    esta_ocupado = models.BooleanField(default=False, editable=False)
    pedidos_atendidos = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.identificacion:
            letra_nombre = self.nombre[0].upper()
            empleados = Mesero.objects.filter(identificacion__startswith="11M").count() + 1
            self.identificacion = f"11M{letra_nombre}{empleados:02d}"
        super().save(*args, **kwargs)

    def entregar_pedido(self, pedido):
        self.actualizar_estado("SERVIDO", pedido)

    def actualizar_pedidos_atendidos(self):
        from facturacion.models import Factura
        self.pedidos_atendidos = Factura.objects.filter(mesero=self).count()
        self.save()

    def asignar_mesa(self, mesa):
        """Asigna una mesa al mesero."""
        if not self.esta_ocupado:
            self.esta_ocupado = True
            mesa.estado = "OCUPADA"
            mesa.save()
        else:
            raise ValueError("El mesero ya está ocupado.")

# Modelo Personal de Cocina
class PersonalCocina(Empleado):
    esta_cocinando = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        if not self.identificacion:
            letra_nombre = self.nombre[0].upper()
            empleados = PersonalCocina.objects.filter(identificacion__startswith="11P").count() + 1
            self.identificacion = f"11P{letra_nombre}{empleados:02d}"
        super().save(*args, **kwargs)

    def preparar_pedido(self, pedido):
        """Marca un pedido como en preparación."""
        pedido.actualizar_estado("EN_PREPARACION")

    def servir_pedido(self, pedido):
        """Marca un pedido como servido."""
        pedido.actualizar_estado("SERVIDO")
# Modelo Administrador
class Administrador(Empleado):
    revision = models.TextField()
    control = models.TextField()

    def crear_reporte(self):
        pass

# Modelo UsuarioPersonalizado para autenticación
class UsuarioPersonalizado(AbstractUser):
    class TipoUsuario(models.TextChoices):
        CLIENTE = "Cliente"
        EMPLEADO = "Empleado"
        ADMINISTRADOR = "Administrador"

    tipo_usuario = models.CharField(
        max_length=15,
        choices=TipoUsuario.choices,
        default=TipoUsuario.CLIENTE
    )

    cliente = models.OneToOneField(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    mesero = models.OneToOneField('util.Mesero', on_delete=models.SET_NULL, null=True, blank=True)
    personal_cocina = models.OneToOneField('util.PersonalCocina', on_delete=models.SET_NULL, null=True, blank=True)
    administrador = models.OneToOneField(Administrador, on_delete=models.SET_NULL, null=True, blank=True)

    def es_cliente(self):
        return self.tipo_usuario == self.TipoUsuario.CLIENTE

    def es_empleado(self):
        return self.tipo_usuario == self.TipoUsuario.EMPLEADO

    def es_admin(self):
        return self.tipo_usuario == self.TipoUsuario.ADMINISTRADOR

# Modelo Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    direccion = models.CharField(max_length=255)
    contacto = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} - {self.contacto}"

class Impuesto(models.Model):
    nombre = models.CharField(max_length=50)  # Ejemplo: IVA, ICE
    porcentaje = models.FloatField()  # Por ejemplo: 12.0 para el IVA
    descripcion = models.TextField(blank=True, null=True)  # Opcional para más detalles

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje}%"