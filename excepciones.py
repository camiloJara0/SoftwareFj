"""
Excepciones personalizadas del sistema Software FJ.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    pass


class DatosInvalidosError(SoftwareFJError):
    """Se produce cuando los datos ingresados no son válidos."""
    pass

class ParametroFaltanteError(SoftwareFJError):
    """Se produce cuando falta un parámetro obligatorio."""
    pass


class CodigoRepetidoError(SoftwareFJError):
    """Se produce cuando un cliente o un servicio ya está registrado."""
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


class CalculoInvalidoError(SoftwareFJError):
    """Se produce cuando un cálculo arroja resultados inconsistentes."""
    pass
