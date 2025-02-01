from django.db import models
from enum import Enum
from django.db.models import Manager
from abc import ABC, abstractmethod
from util.models import Cliente

class EstadoMesa(Enum):
    LIBRE = "LIBRE"
    OCUPADA = "OCUPADA"
    RESERVADA = "RESERVADA"

class EstadoReserva(Enum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"
    ENCURSO = "ENCURSO"

# Modelos
class Mesa(models.Model):
    identificador = models.CharField(max_length=50)
    numero_asientos = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=10,
        choices=[(tag.name, tag.value) for tag in EstadoMesa],
        default=EstadoMesa.LIBRE.name,
        verbose_name="Estado"
    )
    mesas_unidas: Manager = models.ManyToManyField('self', blank=True, symmetrical=False)
    hora_disponible = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Mesa {self.identificador} - Capacidad {self.numero_asientos}"

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado not in [estado.name for estado in EstadoMesa]:
            raise ValueError(
                f"Estado '{nuevo_estado}' no es válido. Estados permitidos: {[estado.name for estado in EstadoMesa]}"
            )
        self.estado = nuevo_estado
        self.save()

    def validar_disponibilidad(self, horario_inicio):
        return self.hora_disponible > horario_inicio if self.hora_disponible else True


class Reserva(models.Model):
    identificador = models.CharField(max_length=50)
    cliente = models.ForeignKey('util.Cliente', on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    cantidad_personas = models.IntegerField()
    fecha_reserva = models.DateField()
    horario_inicio = models.DateTimeField()
    hora_reserva_finalizada = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=15,
        choices=[(tag.name, tag.value) for tag in EstadoReserva],
        default=EstadoReserva.CONFIRMADA.name
    )

    def __str__(self):
        return f"Reserva {self.cliente.nombre}"

    def modificar_reserva(self, nuevos_datos):
        for key, value in nuevos_datos.items():
            setattr(self, key, value)
        self.save()

    def verificar_disponibilidad(self, mesa, fecha, horario_inicio):
        return mesa.validar_disponibilidad(horario_inicio)

    def finalizar_reserva(self):
        self.estado = EstadoReserva.FINALIZADA.name
        self.save()

    def cancelar_reserva(self, identificador_reserva):
        if self.identificador == identificador_reserva:
            self.estado = EstadoReserva.CANCELADA.name
            self.save()
        else:
            raise ValueError("El identificador de reserva no coincide.")

class iReserva(ABC):
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