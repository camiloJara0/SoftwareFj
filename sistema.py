"""
Capa de negocio del sistema Software FJ.

Centraliza las listas en memoria de clientes, servicios y
reservas, aplicando las reglas del negocio y registrando
cada evento y cada rechazo en la bitácora.

No utiliza bases de datos: los datos viven en objetos y
listas mientras la aplicación está en ejecución.
"""

from bitacora import registrar_error, registrar_evento
from clientes import Cliente
from excepciones import (
    ClienteNoEncontradoError,
    CodigoRepetidoError,
    DatosInvalidosError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from reservas import Reserva
from servicios import (
    AlquilerEquipo,
    AsesoriaEspecializada,
    ReservaSala,
    Servicio,
)


TIPOS_SERVICIO = ("sala", "equipo", "asesoria")

_ETIQUETAS_TIPO = {
    "sala": "Reserva de sala",
    "equipo": "Alquiler de equipo",
    "asesoria": "Asesoría especializada",
}


def etiqueta_servicio(servicio):
    """Devuelve la etiqueta legible del tipo de un servicio."""

    if isinstance(servicio, ReservaSala):
        return _ETIQUETAS_TIPO["sala"]

    if isinstance(servicio, AlquilerEquipo):
        return _ETIQUETAS_TIPO["equipo"]

    if isinstance(servicio, AsesoriaEspecializada):
        return _ETIQUETAS_TIPO["asesoria"]

    return "Servicio"


class SistemaFJ:
    """
    Fachada del sistema integral Software FJ.

    Concentra las tres colecciones principales y las
    operaciones permitidas sobre ellas.
    """

    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []

        registrar_evento("Sistema Software FJ iniciado correctamente.")

    # =====================================================
    # CONSULTAS
    # =====================================================

    @property
    def clientes(self):
        """Devuelve una copia inmutable de la lista de clientes."""
        return tuple(self.__clientes)

    @property
    def servicios(self):
        """Devuelve una copia inmutable de la lista de servicios."""
        return tuple(self.__servicios)

    @property
    def reservas(self):
        """Devuelve una copia inmutable de la lista de reservas."""
        return tuple(self.__reservas)

    def estadisticas(self):
        """Resumen numérico del estado actual del sistema."""

        return {
            "clientes": len(self.__clientes),
            "servicios": len(self.__servicios),
            "reservas": len(self.__reservas),
            "confirmadas": len(
                [r for r in self.__reservas if r.estado == "Confirmada"]
            ),
            "procesadas": len(
                [r for r in self.__reservas if r.estado == "Procesada"]
            ),
        }

    # =====================================================
    # CLIENTES
    # =====================================================

    def registrar_cliente(self, nombre, documento, correo, telefono):
        """Registra un cliente válido y sin documento duplicado."""

        try:
            cliente = Cliente(nombre, documento, correo, telefono)

        except SoftwareFJError:
            # Cliente ya registró el detalle del error en la bitácora.
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado registrando el cliente: "
                f"{type(error).__name__}: {error}"
            )
            raise DatosInvalidosError(
                "No fue posible registrar el cliente."
            ) from error

        else:
            for registrado in self.__clientes:
                if registrado == cliente:
                    error = CodigoRepetidoError(
                        f"Ya existe un cliente con el documento "
                        f"{cliente.documento}."
                    )
                    registrar_error(f"Registro de cliente rechazado: {error}")
                    raise error

            self.__clientes.append(cliente)
            registrar_evento(
                f"Cliente registrado: {cliente.documento} - {cliente.nombre}"
            )
            return cliente

    def buscar_cliente(self, documento):
        """Busca un cliente por su documento."""

        if documento is None:
            error = ParametroFaltanteError(
                "Debe indicar el documento del cliente."
            )
            registrar_error(f"Búsqueda de cliente rechazada: {error}")
            raise error

        for cliente in self.__clientes:
            if cliente.documento == str(documento).strip():
                return cliente

        error = ClienteNoEncontradoError(
            f"No existe un cliente con documento {documento}."
        )
        registrar_error(f"Búsqueda de cliente rechazada: {error}")
        raise error

    # =====================================================
    # SERVICIOS
    # =====================================================

    def registrar_servicio(
        self, tipo, codigo, nombre, descripcion,
        precio_base, disponible, dato_adicional
    ):
        """
        Registra un servicio del tipo indicado.

        dato_adicional corresponde a la capacidad (sala),
        al tipo de equipo (alquiler) o a la especialidad (asesoría).
        """

        try:
            tipo_normalizado = self.normalizar_tipo(tipo)

            if codigo is None or nombre is None or descripcion is None:
                raise ParametroFaltanteError(
                    "El código, el nombre y la descripción del servicio "
                    "son obligatorios."
                )

            servicio = self.construir_servicio(
                tipo_normalizado, codigo, nombre, descripcion,
                precio_base, disponible, dato_adicional,
            )

        except SoftwareFJError:
            # El servicio ya registró el detalle del error en la bitácora.
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado registrando el servicio: "
                f"{type(error).__name__}: {error}"
            )
            raise DatosInvalidosError(
                "No fue posible registrar el servicio."
            ) from error

        else:
            for existente in self.__servicios:
                if existente == servicio:
                    error = CodigoRepetidoError(
                        f"Ya existe un servicio con el código "
                        f"{servicio.codigo}."
                    )
                    registrar_error(f"Registro de servicio rechazado: {error}")
                    raise error

            self.__servicios.append(servicio)
            registrar_evento(
                f"Servicio registrado: {servicio.codigo} - "
                f"{servicio.nombre} ({etiqueta_servicio(servicio)})"
            )
            return servicio

    @staticmethod
    def normalizar_tipo(tipo):
        """Valida y normaliza el tipo de servicio solicitado."""

        if tipo is None:
            raise ParametroFaltanteError(
                "Debe indicar el tipo de servicio."
            )

        tipo_normalizado = str(tipo).strip().lower()

        if tipo_normalizado not in TIPOS_SERVICIO:
            raise DatosInvalidosError(
                f"El tipo de servicio '{tipo}' no es válido. "
                f"Opciones: {', '.join(TIPOS_SERVICIO)}."
            )

        return tipo_normalizado

    @staticmethod
    def construir_servicio(
        tipo, codigo, nombre, descripcion,
        precio_base, disponible, dato_adicional
    ):
        """Crea la especialización de servicio correspondiente."""

        if tipo == "sala":
            servicio = ReservaSala(
                codigo, nombre, descripcion,
                precio_base, dato_adicional, disponible,
            )

        elif tipo == "equipo":
            servicio = AlquilerEquipo(
                codigo, nombre, descripcion,
                precio_base, dato_adicional, disponible,
            )

        else:
            servicio = AsesoriaEspecializada(
                codigo, nombre, descripcion,
                precio_base, dato_adicional, disponible,
            )

        return servicio

    # =====================================================
    # RESERVAS
    # =====================================================

    def crear_reserva(
        self, cliente, servicio, duracion,
        porcentaje_impuesto=0, porcentaje_descuento=0
    ):
        """Crea una reserva validando cliente, servicio y duración."""

        try:
            if not isinstance(cliente, Cliente):
                error = ClienteNoEncontradoError(
                    "Debe seleccionar un cliente válido."
                )
                registrar_error(f"Creación de reserva rechazada: {error}")
                raise error

            if cliente not in self.__clientes:
                error = ClienteNoEncontradoError(
                    f"El cliente {cliente.nombre} "
                    f"(documento {cliente.documento}) no está registrado."
                )
                registrar_error(f"Creación de reserva rechazada: {error}")
                raise error

            if not isinstance(servicio, Servicio):
                error = ReservaInvalidaError(
                    "Debe seleccionar un servicio válido."
                )
                registrar_error(f"Creación de reserva rechazada: {error}")
                raise error

            if servicio not in self.__servicios:
                error = ReservaInvalidaError(
                    f"El servicio {servicio.codigo} no está registrado "
                    f"en el sistema."
                )
                registrar_error(f"Creación de reserva rechazada: {error}")
                raise error

            reserva = Reserva(
                cliente, servicio, duracion,
                porcentaje_impuesto, porcentaje_descuento,
            )

        except SoftwareFJError:
            # Reserva ya registró el detalle del error en la bitácora.
            raise

        except Exception as error:
            registrar_error(
                f"Error inesperado creando la reserva: "
                f"{type(error).__name__}: {error}"
            )
            raise DatosInvalidosError(
                "No fue posible crear la reserva."
            ) from error

        else:
            self.__reservas.append(reserva)
            registrar_evento(
                f"Reserva creada: {reserva.id[:8]} - "
                f"{cliente.nombre} / {servicio.nombre}"
            )
            return reserva

    def confirmar_reserva(self, reserva):
        """Confirma una reserva registrada en el sistema."""

        self.verificar_reserva(reserva)
        return reserva.confirmar()

    def cancelar_reserva(self, reserva):
        """Cancela una reserva registrada en el sistema."""

        self.verificar_reserva(reserva)
        return reserva.cancelar()

    def procesar_reserva(self, reserva):
        """Procesa una reserva registrada y devuelve su costo."""

        self.verificar_reserva(reserva)
        return reserva.procesar()

    def verificar_reserva(self, reserva):
        """Comprueba que la reserva pertenezca al sistema."""

        if not isinstance(reserva, Reserva):
            error = ReservaInvalidaError(
                "Debe seleccionar una reserva válida."
            )
            registrar_error(f"Operación sobre reserva rechazada: {error}")
            raise error

        if reserva not in self.__reservas:
            error = ReservaInvalidaError(
                f"La reserva {reserva.id[:8]} no está registrada "
                f"en el sistema."
            )
            registrar_error(f"Operación sobre reserva rechazada: {error}")
            raise error

        return True
