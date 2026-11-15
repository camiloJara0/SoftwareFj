"""
Módulo encargado de gestionar los clientes
del sistema Software FJ.
"""

from entidades import Entidad
from excepciones import DatosInvalidosError


class Cliente(Entidad):
    """
    Representa a un cliente registrado en Software FJ.
    """

    def __init__(self, nombre, documento, correo, telefono):
        # Inicializamos la clase padre.
        super().__init__()

        # Encapsulamos los datos del cliente.
        self.__nombre = nombre.strip()
        self.__documento = documento.strip()
        self.__correo = correo.strip()
        self.__telefono = str(telefono).strip()

        # Validamos la información ingresada.
        self.validar()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def validar(self):
        """Comprueba que los datos del cliente sean correctos."""

        if not self.__nombre:
            raise DatosInvalidosError(
                "El nombre del cliente no puede estar vacío."
            )

        if len(self.__documento) < 5:
            raise DatosInvalidosError(
                "El documento debe tener al menos 5 dígitos."
            )
            
        if not self.__documento.isdigit():
            raise DatosInvalidosError(
                "El documento solo debe contener números"
            )

        if "@" not in self.__correo or "." not in self.__correo:
            raise DatosInvalidosError(
                "El correo electrónico no tiene un formato válido."
            )

        if not self.__telefono.isdigit() or not 7 <= len(self.__telefono) <= 15:
            raise DatosInvalidosError(
                "El teléfono debe contener entre 7 y 15 dígitos."
            )

        return True

    def __str__(self):
        """Devuelve una descripción del cliente."""

        return (
            f"Cliente: {self.__nombre} | "
            f"Documento: {self.__documento} | "
            f"Correo: {self.__correo} | "
            f"Teléfono: {self.__telefono}"
        )