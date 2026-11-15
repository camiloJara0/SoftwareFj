"""
Módulo encargado de gestionar las reservas
del sistema Software FJ.
"""

from entidades import Entidad
from clientes import Cliente
from servicios import Servicio

from excepciones import (
    DatosInvalidosError,
    ClienteNoEncontradoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError
)


class Reserva(Entidad):
    """Representa una reserva realizada por un cliente."""

    def __init__(self, cliente, servicio, duracion):
        super().__init__()

        self.__cliente = cliente
        self.__servicio = servicio

        try:
            self.__duracion = float(duracion)
        except (ValueError, TypeError) as error:
            raise DatosInvalidosError(
                "La duración debe ser un valor numérico."
            ) from error

        self.__estado = "Pendiente"

        self.validar()

    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def estado(self):
        return self.__estado

    def validar(self):
        """Valida la información necesaria para crear una reserva."""

        if not isinstance(self.__cliente, Cliente):
            raise ClienteNoEncontradoError(
                "La reserva debe estar asociada a un cliente válido."
            )

        if not isinstance(self.__servicio, Servicio):
            raise ReservaInvalidaError(
                "La reserva debe estar asociada a un servicio válido."
            )

        if self.__duracion <= 0:
            raise DatosInvalidosError(
                "La duración de la reserva debe ser mayor que cero."
            )

        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio seleccionado no está disponible."
            )

        return True

    def confirmar(self):
        """Confirma una reserva pendiente."""

        if self.__estado != "Pendiente":
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                "No se puede confirmar: el servicio no está disponible."
            )

        self.__estado = "Confirmada"

        return self.__estado

    def cancelar(self):
        """Cancela una reserva pendiente o confirmada."""

        if self.__estado not in ("Pendiente", "Confirmada"):
            raise OperacionNoPermitidaError(
                "No se puede cancelar una reserva que ya fue procesada o cancelada."
            )

        self.__estado = "Cancelada"

        return self.__estado

    def procesar(self):
        """Procesa una reserva confirmada y calcula su costo."""

        if self.__estado != "Confirmada":
            raise OperacionNoPermitidaError(
                "La reserva debe estar confirmada antes de procesarse."
            )

        costo_total = self.__servicio.calcular_costo(
            self.__duracion
        )

        self.__estado = "Procesada"

        return costo_total

    def __str__(self):
        """Devuelve un resumen de la reserva."""

        return (
            f"Reserva: {self.id} | "
            f"Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | "
            f"Duración: {self.__duracion} | "
            f"Estado: {self.__estado}"
        )