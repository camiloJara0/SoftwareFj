"""
Excepciones personalizadas del sistema Software FJ.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    pass


class DatosInvalidosError(SoftwareFJError):
    """Se produce cuando los datos ingresados no son válidos."""
    pass


class ClienteNoEncontradoError(SoftwareFJError):
    """Se produce cuando no se encuentra un cliente."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se produce cuando un servicio no está disponible."""
    pass


class ReservaInvalidaError(SoftwareFJError):
    """Se produce cuando una reserva presenta errores."""
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    """Se produce cuando se intenta realizar una operación no permitida."""
    pass