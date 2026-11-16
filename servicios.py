"""
Módulo de servicios de Software FJ.
Implementación de herencia, abstracción y polimorfismo.
"""

from abc import ABC, abstractmethod
from math import isfinite

from bitacora import registrar_error
from entidades import Entidad
from excepciones import (
    DatosInvalidosError,
    CalculoInvalidoError,
    SoftwareFJError
)


class Servicio(Entidad, ABC):
    """Clase abstracta que representa un servicio."""

    def __init__(
        self, codigo, nombre, descripcion,
        precio_base, disponible=True
    ):
        try: 
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
        
        except SoftwareFJError as error:
            registrar_error(f"Servicio inválido: {error}")
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado al crear el servicio: "
                f"{type(error).__name__}: {error}"
            )
            raise DatosInvalidosError(
                "No fue posible construir el servicio con los datos recibidos."
            ) from error

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
    
    @staticmethod
    def _resolver_calculo(argumentos, opciones):
        """
        Resuelve las distintas variantes de llamada admitidas
        por calcular_costo (sobrecarga de métodos).

        Variantes soportadas:
            calcular_costo()
            calcular_costo(cantidad)
            calcular_costo(cantidad, porcentaje_impuesto)
            calcular_costo(cantidad, porcentaje_impuesto, porcentaje_descuento)
            calcular_costo(cantidad=..., impuesto=..., descuento=...)
            calcular_costo(porcentaje_impuesto=..., porcentaje_descuento=...)
        """

        alias = {
            "cantidad": "cantidad",
            "impuesto": "impuesto",
            "porcentaje_impuesto": "impuesto",
            "descuento": "descuento",
            "porcentaje_descuento": "descuento",
        }

        valores = {"cantidad": 1, "impuesto": 0, "descuento": 0}

        if argumentos and opciones:
            raise DatosInvalidosError(
                "No se pueden combinar argumentos posicionales "
                "con argumentos con nombre en calcular_costo."
            )

        if len(argumentos) > 3:
            raise DatosInvalidosError(
                "calcular_costo admite máximo 3 argumentos posicionales: "
                "cantidad, porcentaje_impuesto y porcentaje_descuento."
            )

        for nombre, valor in zip(
            ("cantidad", "impuesto", "descuento"), argumentos
        ):
            valores[nombre] = valor

        asignados = set()

        for clave, valor in opciones.items():
            if clave not in alias:
                raise DatosInvalidosError(
                    f"El parámetro '{clave}' no es válido en calcular_costo."
                )

            nombre = alias[clave]

            if nombre in asignados:
                raise CalculoInvalidoError(
                    f"El parámetro '{nombre}' fue indicado más de una vez."
                )

            asignados.add(nombre)
            valores[nombre] = valor

        for nombre, valor in valores.items():
            if (
                isinstance(valor, bool)
                or not isinstance(valor, (int, float))
                or not isfinite(valor)
            ):
                raise DatosInvalidosError(
                    f"El valor de {nombre} debe ser numérico y finito."
                )

        if valores["cantidad"] <= 0:
            raise CalculoInvalidoError("La cantidad debe ser mayor que cero.")

        if not 0 <= valores["impuesto"] <= 100:
            raise CalculoInvalidoError("El impuesto debe estar entre 0 y 100.")

        if not 0 <= valores["descuento"] <= 100:
            raise CalculoInvalidoError("El descuento debe estar entre 0 y 100.")

        return valores["cantidad"], valores["impuesto"], valores["descuento"]

    def calcular_costo(
        self, *argumentos, **opciones
    ):
        """
        Calcula el costo total de un servicio.

        Es un método sobrecargado: resuelve distintas variantes
        de llamada (con o sin impuestos, descuentos y con
        parámetros posicionales o con nombre).
        """
        try:
            cantidad, impuesto, descuento = self._resolver_calculo(
                argumentos, opciones
            )

            subtotal = self.precio_base * cantidad
            subtotal_con_descuento = subtotal * (1 - descuento / 100)
            total = subtotal_con_descuento * (1 + impuesto / 100)

            if not isfinite(total) or total < 0:
                raise CalculoInvalidoError(
                    "El cálculo arrojó un resultado inconsistente."
                )

        except SoftwareFJError:
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado calculando el costo de {self.codigo}: "
                f"{type(error).__name__}: {error}"
            )
            raise CalculoInvalidoError(
                f"No fue posible calcular el costo del servicio {self.codigo}."
            ) from error

        else:
            return round(total, 2)
        
    @abstractmethod
    def describir(self):
        """Devuelve la descripción del servicio."""
        pass
    
    def __eq__(self, otro):
        """Dos servicios son iguales si comparten código."""

        if not isinstance(otro, Servicio):
            return NotImplemented

        return self.codigo.upper() == otro.codigo.upper()

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (${self.precio_base:,.2f})"

    


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
    
    def calcular_costo(self, *argumentos, **opciones):
        """Sobrescritura polimórfica: añade recargo por uso prolongado."""

        cantidad, _, _ = self._resolver_calculo(argumentos, opciones)
        total = super().calcular_costo(*argumentos, **opciones)

        if cantidad > 4:
            total = round(total * 1.05, 2)

        return total

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
    
    def calcular_costo(self, *argumentos, **opciones):
        """Sobrescritura polimórfica: agrega el seguro obligatorio."""

        cantidad, _, _ = self._resolver_calculo(argumentos, opciones)
        total = super().calcular_costo(*argumentos, **opciones)
        seguro = round(
            self.precio_base * cantidad * (self.PORCENTAJE_SEGURO / 100), 2
        )

        return round(total + seguro, 2)

    def describir(self):
        """Devuelve la descripción del equipo."""
        return (
            f"Equipo: {self.nombre} | "
            f"Tipo: {self.tipo_equipo} | "
            f"Precio por día: ${self.precio_base:.2f}"
        )


class AsesoriaEspecializada(Servicio):
    """Representa el servicio de asesoría especializada."""

    HORAS_DESCUENTO = 10
    DESCUENTO_VOLUMEN = 10
    
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
    
    def calcular_costo(self, *argumentos, **opciones):
        """Sobrescritura polimórfica: descuento por volumen de horas."""

        cantidad, _, _ = self._resolver_calculo(argumentos, opciones)
        total = super().calcular_costo(*argumentos, **opciones)

        if cantidad >= self.HORAS_DESCUENTO:
            total = round(
                total * (1 - self.DESCUENTO_VOLUMEN / 100), 2
            )

        return total

    def describir(self):
        """Devuelve la descripción de la asesoría."""
        return (
            f"Asesoría: {self.nombre} | "
            f"Especialidad: {self.especialidad} | "
            f"Precio por hora: ${self.precio_base:.2f}"
        )