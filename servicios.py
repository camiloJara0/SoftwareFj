"""
Módulo de servicios de Software FJ.
Implementación de herencia, abstracción y polimorfismo.
"""

from abc import ABC, abstractmethod
from math import isfinite

from entidades import Entidad
from excepciones import DatosInvalidosError


class Servicio(Entidad, ABC):
    """Clase abstracta que representa un servicio."""

    def __init__(
        self, codigo, nombre, descripcion,
        precio_base, disponible=True
    ):
        super().__init__()

        if not all(isinstance(campo, str) for campo in (codigo, nombre, descripcion)):
            raise DatosInvalidosError(
                "El código, nombre y descripción deben ser cadenas de texto."
            )

        self.codigo = codigo.strip()
        self.nombre = nombre.strip()
        self.descripcion = descripcion.strip()

        if isinstance(precio_base, bool):
            raise DatosInvalidosError("El precio debe ser un valor numérico.")

        try:
            self.precio_base = float(precio_base)
        except (ValueError, TypeError) as error:
            raise DatosInvalidosError(
                "El precio debe ser un valor numérico."
            ) from error

        if not isinstance(disponible, bool):
            raise DatosInvalidosError(
                "La disponibilidad debe ser verdadera o falsa."
            )

        self.disponible = disponible
        self.validar()

    def validar(self):
        """Valida los datos generales del servicio."""
        if not self.codigo:
            raise DatosInvalidosError("El código del servicio es obligatorio.")

        if not self.nombre:
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")

        if not self.descripcion:
            raise DatosInvalidosError("La descripción del servicio es obligatoria.")

        if not isfinite(self.precio_base) or self.precio_base < 0:
            raise DatosInvalidosError(
                "El precio del servicio debe ser un número finito no negativo."
            )

        return True

    def calcular_costo(
        self, cantidad=1, porcentaje_impuesto=0,
        porcentaje_descuento=0
    ):
        """
        Calcula el costo aplicando cantidad, descuento e impuesto.

        El descuento se aplica primero y el impuesto se calcula
        sobre el valor resultante.
        """
        valores = {
            "cantidad": cantidad,
            "impuesto": porcentaje_impuesto,
            "descuento": porcentaje_descuento,
        }

        for nombre, valor in valores.items():
            if (
                isinstance(valor, bool)
                or not isinstance(valor, (int, float))
                or not isfinite(valor)
            ):
                raise DatosInvalidosError(
                    f"El valor de {nombre} debe ser numérico y finito."
                )

        if cantidad <= 0:
            raise DatosInvalidosError("La cantidad debe ser mayor que cero.")

        if not 0 <= porcentaje_impuesto <= 100:
            raise DatosInvalidosError("El impuesto debe estar entre 0 y 100.")

        if not 0 <= porcentaje_descuento <= 100:
            raise DatosInvalidosError("El descuento debe estar entre 0 y 100.")

        subtotal = self.precio_base * cantidad
        valor_descuento = subtotal * (porcentaje_descuento / 100)
        subtotal_con_descuento = subtotal - valor_descuento
        valor_impuesto = subtotal_con_descuento * (porcentaje_impuesto / 100)

        total = subtotal_con_descuento + valor_impuesto
        return round(total, 2)

    @abstractmethod
    def describir(self):
        """Devuelve la descripción del servicio."""
        pass


class ReservaSala(Servicio):
    """Representa el servicio de reserva de salas."""

    def __init__(
        self, codigo, nombre, descripcion,
        precio_base, capacidad, disponible=True
    ):
        self.capacidad = capacidad
        super().__init__(
            codigo, nombre, descripcion,
            precio_base, disponible
        )

    def validar(self):
        """Valida los datos específicos de la sala."""
        super().validar()

        if (
            isinstance(self.capacidad, bool)
            or not isinstance(self.capacidad, int)
            or self.capacidad <= 0
        ):
            raise DatosInvalidosError(
                "La capacidad de la sala debe ser un número entero positivo."
            )

        return True

    def describir(self):
        """Devuelve la descripción de la sala."""
        return (
            f"Sala: {self.nombre} | "
            f"Capacidad: {self.capacidad} personas | "
            f"Precio por hora: ${self.precio_base:.2f}"
        )


class AlquilerEquipo(Servicio):
    """Representa el servicio de alquiler de equipos."""

    def __init__(
        self, codigo, nombre, descripcion,
        precio_base, tipo_equipo, disponible=True
    ):
        if not isinstance(tipo_equipo, str):
            raise DatosInvalidosError(
                "El tipo de equipo debe ser una cadena de texto."
            )

        self.tipo_equipo = tipo_equipo.strip()
        super().__init__(
            codigo, nombre, descripcion,
            precio_base, disponible
        )

    def validar(self):
        """Valida los datos específicos del equipo."""
        super().validar()

        if not self.tipo_equipo:
            raise DatosInvalidosError("El tipo de equipo es obligatorio.")

        return True

    def describir(self):
        """Devuelve la descripción del equipo."""
        return (
            f"Equipo: {self.nombre} | "
            f"Tipo: {self.tipo_equipo} | "
            f"Precio por día: ${self.precio_base:.2f}"
        )


class AsesoriaEspecializada(Servicio):
    """Representa el servicio de asesoría especializada."""

    def __init__(
        self, codigo, nombre, descripcion,
        precio_base, especialidad, disponible=True
    ):
        if not isinstance(especialidad, str):
            raise DatosInvalidosError(
                "La especialidad de la asesoría debe ser una cadena de texto."
            )

        self.especialidad = especialidad.strip()
        super().__init__(
            codigo, nombre, descripcion,
            precio_base, disponible
        )

    def validar(self):
        """Valida los datos específicos de la asesoría."""
        super().validar()

        if not self.especialidad:
            raise DatosInvalidosError(
                "La especialidad de la asesoría es obligatoria."
            )

        return True

    def describir(self):
        """Devuelve la descripción de la asesoría."""
        return (
            f"Asesoría: {self.nombre} | "
            f"Especialidad: {self.especialidad} | "
            f"Precio por hora: ${self.precio_base:.2f}"
        )