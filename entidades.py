from abc import ABC, abstractmethod
from uuid import uuid4


class Entidad(ABC):
    """
    Clase abstracta que representa una entidad general
    dentro del sistema Software FJ.
    """

    def __init__(self):
        # Identificador único de cada entidad.
        self._id = str(uuid4())

    @property
    def id(self):
        """Permite consultar el identificador de la entidad."""
        return self._id

    @abstractmethod
    def validar(self):
        """
        Método abstracto que cada clase hija
        deberá implementar.
        """
        pass