"""
Sistema Software FJ
Programa principal con menú interactivo.

Los datos se almacenan únicamente en listas y objetos
mientras el programa permanece en ejecución.
No utiliza bases de datos ni persistencia de información.
"""

from math import isfinite

from bitacora import registrar_error, registrar_error_detallado, registrar_evento
from excepciones import DatosInvalidosError, SoftwareFJError
from sistema import SistemaFJ, etiqueta_servicio
from clientes import Cliente
from servicios import (
    ReservaSala,
    AlquilerEquipo,
    AsesoriaEspecializada,
)
from reservas import Reserva
from excepciones import SoftwareFJError, DatosInvalidosError


# =====================================================
# LISTAS EN MEMORIA
# =====================================================

sistema = SistemaFJ()
clientes = []
servicios = []
reservas = []


# =====================================================
# FUNCIONES AUXILIARES PARA CAPTURAR DATOS
# =====================================================

def mostrar_titulo(titulo):
    print("\n" + "=" * 55)
    print(titulo.center(55))
    print("=" * 55)


def pedir_texto(mensaje):
    return input(mensaje).strip()


def pedir_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Error: debe ingresar un número entero.")


def pedir_decimal(mensaje):
    while True:
        try:
            numero = float(input(mensaje))
            if isfinite(numero):
                return numero
            print("Error: ingrese un número finito válido.")
        except ValueError:
            print("Error: debe ingresar un valor numérico.")


def pedir_si_no(mensaje):
    while True:
        respuesta = input(mensaje).strip().lower()

        if respuesta in ("s", "si", "sí"):
            return True

        if respuesta in ("n", "no"):
            return False

        print("Ingrese S para sí o N para no.")


def seleccionar_elemento(lista, descripcion):
    """Permite seleccionar un objeto de una lista."""
    if not lista:
        print(f"No hay {descripcion} registrados.")
        return None

    for indice, elemento in enumerate(lista, start=1):
        print(f"{indice}. {elemento}")

    while True:
        opcion = pedir_entero("Seleccione una opción: ")

        if 1 <= opcion <= len(lista):
            return lista[opcion - 1]

        print("La opción seleccionada no existe.")


# =====================================================
# GESTIÓN DE CLIENTES
# =====================================================

def registrar_cliente():
    mostrar_titulo("REGISTRO DE CLIENTES")

    nombre = pedir_texto("Nombre: ")
    documento = pedir_texto("Documento: ")
    correo = pedir_texto("Correo electrónico: ")
    telefono = pedir_texto("Teléfono: ")

    cliente = sistema.registrar_cliente(
        nombre,
        documento,
        correo,
        telefono,
    )

    print("\nCliente registrado correctamente.")
    print(cliente)


def mostrar_clientes():
    mostrar_titulo("LISTADO DE CLIENTES")

    if not clientes:
        print("No hay clientes registrados.")
        return

    for indice, cliente in enumerate(clientes, start=1):
        print(f"\nCliente {indice}")
        print(cliente)


# =====================================================
# GESTIÓN DE SERVICIOS
# =====================================================

def registrar_servicio():
    mostrar_titulo("REGISTRO DE SERVICIOS")

    print("1. Reserva de sala")
    print("2. Alquiler de equipo")
    print("3. Asesoría especializada")

    opcion = pedir_entero("\nSeleccione el tipo de servicio: ")

    if opcion not in (1, 2, 3):
        raise DatosInvalidosError(
            "El tipo de servicio seleccionado no es válido."
        )

    tipo = {1: "sala", 2: "equipo", 3: "asesoria"}[opcion]

    codigo = pedir_texto("Código del servicio: ")
    nombre = pedir_texto("Nombre del servicio: ")
    descripcion = pedir_texto("Descripción: ")
    precio = pedir_decimal("Precio base: ")
    disponible = pedir_si_no("¿El servicio está disponible? (S/N): ")

    if opcion == 1:
        dato_adicional = pedir_entero("Capacidad de la sala: ")


    elif opcion == 2:
        dato_adicional = pedir_texto("Tipo de equipo: ")

    else:
        dato_adicional = pedir_texto("Especialidad: ")

    servicio = sistema.registrar_servicio(
        tipo,
        codigo,
        nombre,
        descripcion,
        precio,
        disponible,
        dato_adicional,
    )

    print("\nServicio registrado correctamente.")
    print(servicio.describir())


def mostrar_servicios():
    mostrar_titulo("LISTADO DE SERVICIOS")

    if not servicios:
        print("No hay servicios registrados.")
        return

    for indice, servicio in enumerate(servicios, start=1):
        estado = "Disponible" if servicio.disponible else "No disponible"

        print(f"\nServicio {indice}")
        print(f"Código: {servicio.codigo}")
        print(f"Tipo: {etiqueta_servicio(servicio)}")
        print(servicio.describir())
        print(f"Descripción: {servicio.descripcion}")
        print(f"Estado: {estado}")


# =====================================================
# GESTIÓN DE RESERVAS
# =====================================================

def crear_reserva():
    mostrar_titulo("CREACIÓN DE RESERVAS")

    if not sistema.clientes:
        print("Primero debe registrar al menos un cliente.")
        return

    if not sistema.servicios:
        print("Primero debe registrar al menos un servicio.")
        return

    print("\nCLIENTES REGISTRADOS")
    cliente = seleccionar_elemento(list(sistema.clientes), "clientes")
    if cliente is None:
        return

    print("\nSERVICIOS DISPONIBLES")
    servicio = seleccionar_elemento(list(sistema.servicios), "servicios")
    if servicio is None:
        return

    duracion = pedir_decimal(
        "\nIngrese la duración (horas o días según el servicio): "
    )
    impuesto = pedir_decimal("Porcentaje de impuesto (0-100): ")
    descuento = pedir_decimal("Porcentaje de descuento (0-100): ")

    reserva = Reserva(
        cliente,
        servicio,
        duracion,
        impuesto,
        descuento
    )

    reservas.append(reserva)

    print("\nReserva creada correctamente.")
    print(reserva)


def mostrar_reservas():
    mostrar_titulo("LISTADO DE RESERVAS")

    if not sistema.reservas:
        print("No hay reservas registradas.")
        return

    for indice, reserva in enumerate(reservas, start=1):
        print(f"\nReserva {indice}")
        print(reserva)


def gestionar_reserva():
    mostrar_titulo("GESTIÓN DE RESERVAS")

    if not sistema.reservas:
        print("No hay reservas para gestionar.")
        return

    reserva = seleccionar_elemento(sistema.reservas, "reservas")
    if reserva is None:
        return

    print("\n¿Qué operación desea realizar?")
    print("1. Confirmar reserva")
    print("2. Procesar reserva")
    print("3. Cancelar reserva")
    print("4. Volver")

    opcion = pedir_entero("\nSeleccione una opción: ")

    if opcion == 1:
        estado = sistema.confirmar_reserva()
        print(f"\nReserva confirmada. Estado: {estado}")

    elif opcion == 2:
        costo = sistema.procesar_reserva()
        print("\nReserva procesada correctamente.")
        print(f"Costo total: ${costo:,.2f}")

    elif opcion == 3:
        estado = sistema.cancelar_reserva()
        print(f"\nReserva cancelada. Estado: {estado}")

    elif opcion == 4:
        return

    else:
        raise DatosInvalidosError("La operación seleccionada no es válida.")

    print("\nEstado actual de la reserva:")
    print(reserva)


# =====================================================
# MENÚ PRINCIPAL
# =====================================================

def menu_principal():
    while True:
        mostrar_titulo("SISTEMA SOFTWARE FJ")

        print("1. Registrar cliente")
        print("2. Consultar clientes")
        print("3. Registrar servicio")
        print("4. Consultar servicios")
        print("5. Crear reserva")
        print("6. Consultar reservas")
        print("7. Gestionar reserva")
        print("0. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        try:
            if opcion == "1":
                registrar_cliente()
            elif opcion == "2":
                mostrar_clientes()
            elif opcion == "3":
                registrar_servicio()
            elif opcion == "4":
                mostrar_servicios()
            elif opcion == "5":
                crear_reserva()
            elif opcion == "6":
                mostrar_reservas()
            elif opcion == "7":
                gestionar_reserva()
            elif opcion == "0":
                print("\nGracias por utilizar Software FJ.")
                print("Los datos de esta sesión no serán almacenados.")
                break
            else:
                print("\nOpción no válida. Intente nuevamente.")

        except SoftwareFJError as error:
            print(f"\nOperación rechazada: {error}")

        except Exception as error:
            registrar_error_detallado(
                "Error inesperado en el menú del sistema", error
            )
            print("\nSe presentó un error inesperado.")
            print("El sistema continuará funcionando.")
            print(f"Detalle técnico: {type(error).__name__}: {error}")

        else:
            if opcion in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                registrar_evento(
                    f"Operación del menú '{opcion}' ejecutada sin errores."
                )
                
        finally:
            if opcion != "0":
                input("\nPresione ENTER para continuar...")

# =====================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# =====================================================

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nEjecución interrumpida por el usuario.")
    finally:
        print("\nFin de la ejecución de Software FJ.")