"""
Módulo encargado de gestionar las reservas
del sistema Software FJ.
"""

from datetime import datetime
from math import isfinite

from bitacora import registrar_error, registrar_evento
from entidades import Entidad
from clientes import Cliente
from servicios import Servicio

from excepciones import (
    CalculoInvalidoError,
    DatosInvalidosError,
    ClienteNoEncontradoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    SoftwareFJError
)


class Reserva(Entidad):
    """Representa una reserva realizada por un cliente."""

    def __init__(self, cliente, servicio, duracion, porcentaje_impuesto=0, porcentaje_descuento=0):
        try:
            
            super().__init__()
            
            self.__cliente = cliente
            self.__servicio = servicio

            self.__duracion = self.convertir_numero(
                duracion, "La duración"
            )
            self.__impuesto = self.convertir_numero(
                porcentaje_impuesto, "El porcentaje de impuesto"
            )
            self.__descuento = self.convertir_numero(
                porcentaje_descuento, "El porcentaje de descuento"
            )

            self.__estado = "Pendiente"
            self.__costo_final = None
            self.__fecha_creacion = datetime.now()

            self.validar()
        
        except SoftwareFJError as error:
            registrar_error(f"Reserva inválida: {error}")
            raise
        
        except Exception as error:
            registrar_error(
                f"Error inesperado al crear la reserva: "
                f"{type(error).__name__}: {error}"
            )
            raise DatosInvalidosError(
                "No fue posible contruir la reserva con los datos recibidos."
            ) from error

    @staticmethod
    def convertir_numero(valor, etiqueta):
        """Convierte un valor numérico y encadena el error original."""

        if valor is None:
            raise DatosInvalidosError(f"{etiqueta} es obligatorio.")

        try:
            return float(valor)
        except (ValueError, TypeError) as error:
            raise DatosInvalidosError(
                f"{etiqueta} debe ser un valor numérico."
            ) from error

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
    def porcentaje_impuesto(self):
        return self.__impuesto

    @property
    def porcentaje_descuento(self):
        return self.__descuento
    
    @property
    def estado(self):
        return self.__estado
    
    @property
    def costo_final(self):
        return self.__costo_final

    @property
    def fecha_creacion(self):
        return self.__fecha_creacion

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
            
        if not 0 <= self.__impuesto <= 100:
            raise CalculoInvalidoError(
                "El porcentaje de impuesto debe estar entre 0 y 100."
            )

        if not 0 <= self.__descuento <= 100:
            raise CalculoInvalidoError(
                "El porcentaje de descuento debe estar entre 0 y 100."
            )

        if not self.__servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio seleccionado no está disponible."
            )

        return True

    def confirmar(self):
        """Confirma una reserva pendiente."""

        try:
            if self.__estado != "Pendiente":
                raise OperacionNoPermitidaError(
                    "Solo se pueden confirmar reservas pendientes."
                )

            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(
                    "No se puede confirmar: el servicio no está disponible."
                )

        except SoftwareFJError as error:
            registrar_error(
                f"Confirmación rechazada ({self.id[:8]}): {error}"
            )
            raise
        
        else:
            self.__estado = "Confirmada"
            registrar_evento(
                f"Reserva {self.id[:8]} confirmada "
                f"para {self.__cliente.nombre}."
            )
            return self.__estado
        
        finally:
            registrar_evento(
                f"Intento de confirmación de la reserva "
                f"{self.id[:8]} finalizado (estado: {self.__estado})."
            )

    def cancelar(self):
        """Cancela una reserva pendiente o confirmada."""

        try:
            if self.__estado not in ("Pendiente", "Confirmada"):
                raise OperacionNoPermitidaError(
                    "No se puede cancelar una reserva que ya fue procesada o cancelada."
                )
                
        except SoftwareFJError as error:
            registrar_error(
                f"Cancelación rechazada ({self.id[:8]}): {error}"
            )
            raise
        
        else:
            self.__estado = "Cancelada"
            registrar_evento(
                f"Reserva {self.id[:8]} cancelada "
                f"para {self.__cliente.nombre}."
            )
            return self.__estado

        finally:
            registrar_evento(
                f"Intento de cancelación de la reserva "
                f"{self.id[:8]} finalizado (estado: {self.__estado})."
            )

    def procesar(self):
        """Procesa una reserva confirmada y calcula su costo."""

        try:
            
            if self.__estado != "Confirmada":
                raise OperacionNoPermitidaError(
                    "La reserva debe estar confirmada antes de procesarse."
                )
                
            if not self.__servicio.disponible:
                raise ServicioNoDisponibleError(
                    "No se puede procesar: el servicio no está disponible."
                )

            costo_total = self.__servicio.calcular_costo(
                self.__duracion,
                self.__impuesto,
                self.__descuento
            )
            
            if not isfinite(costo_total) or costo_total < 0:
                raise CalculoInvalidoError(
                    "El costo calculado para la reserva es inconsistente."
                )

        except SoftwareFJError as error:
            registrar_error(
                f"Procesamiento rechazado ({self.id[:8]}): {error}"
            )
            raise
        
        except Exception as error:
            registrar_error(
                f"Error inesperado al procesar la reserva {self.id[:8]}: "
                f"{type(error).__name__}: {error}"
            )
            raise CalculoInvalidoError(
                "No fue posible procesar la reserva."
            ) from error
        
        else:    
            self.__estado = "Procesada"
            self.__costo_final = costo_total
            registrar_evento(
                f"Reserva {self.id[:8]} procesada. "
                f"Costo total: ${costo_total:,.2f}"
            )
            return costo_total
        
        finally:
            registrar_evento(
                f"Intento de procesamiento de la reserva "
                f"{self.id[:8]} finalizado (estado: {self.__estado})."
            )

    def __str__(self):
        """Devuelve un resumen de la reserva."""

        texto = (
            f"Reserva: {self.id[:8]} | "
            f"Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} | "
            f"Duración: {self.__duracion:g} | "
            f"Impuesto: {self.__impuesto:g}% | "
            f"Descuento: {self.__descuento:g}% | "
            f"Estado: {self.__estado}"
        )

        if self.__costo_final is not None:
            texto += f" | Costo: ${self.__costo_final:,.2f}"

        return texto