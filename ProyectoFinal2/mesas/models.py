from django.db import models
from abc import ABC, abstractmethod
from util.models import Cliente

# --- ENUMERADORES ---
class EstadoMesa(models.TextChoices):
    LIBRE = "LIBRE"
    OCUPADA = "OCUPADA"
    RESERVADA = "RESERVADA"

class EstadoReserva(models.TextChoices):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"
    EN_CURSO = "EN_CURSO"

# --- MODELO MESA ---
class Mesa(models.Model):
    identificador = models.CharField(max_length=50, unique=True)
    numero_asientos = models.PositiveIntegerField()
    ubicacion = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=10,
        choices=EstadoMesa.choices,
        default=EstadoMesa.LIBRE
    )
    hora_disponible = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Mesa {self.identificador} - Capacidad {self.numero_asientos}"

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in EstadoMesa.values:
            raise ValueError(
                f"Estado '{nuevo_estado}' no es válido. Estados permitidos: {list(EstadoMesa.values)}"
            )
        self.estado = nuevo_estado
        self.save()

    def validar_disponibilidad(self, horario_inicio):
        if self.hora_disponible is None:
            return True  # 🔹 Si no tiene horario de disponibilidad, asumimos que está libre
        return self.hora_disponible > horario_inicio

# --- MODELO RESERVA ---
class Reserva(models.Model):
    identificador = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    cantidad_personas = models.PositiveIntegerField()
    fecha_reserva = models.DateField()
    horario_inicio = models.DateTimeField()
    hora_reserva_finalizada = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=15,
        choices=EstadoReserva.choices,
        default=EstadoReserva.CONFIRMADA
    )

    def __str__(self):
        return f"Reserva {self.identificador} - Cliente {self.cliente.nombre}"

    def modificar_reserva(self, nuevos_datos):
        """Modifica la reserva si los datos son válidos."""
        for key, value in nuevos_datos.items():
            if hasattr(self, key):  # 🔹 Solo modifica si el atributo existe
                setattr(self, key, value)
        self.save()

    def verificar_disponibilidad(self):
        """Verifica si la mesa está disponible en la fecha y horario de la reserva."""
        return self.mesa.validar_disponibilidad(self.horario_inicio)

    def finalizar_reserva(self):
        self.estado = EstadoReserva.FINALIZADA
        self.hora_reserva_finalizada = models.DateTimeField.now()
        self.save()

    def cancelar_reserva(self):
        self.estado = EstadoReserva.CANCELADA
        self.save()

# --- INTERFAZ IRESERVA ---
class IReserva(ABC):  # 🔹 Corregido de "iReserva" a "IReserva"
    @abstractmethod
    def hacer_reserva(self, datos_reserva):
        """
        Realizar una nueva reserva.
        Parámetros:
        - datos_reserva: dict con la información necesaria para crear la reserva.
        """
        pass

    @abstractmethod
    def cancelar_reserva(self, identificador_reserva):
        """
        Cancelar una reserva existente.
        Parámetros:
        - identificador_reserva: ID único de la reserva a cancelar.
        """
        pass
