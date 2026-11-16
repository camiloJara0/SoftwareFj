"""
Módulo de logs del sistema Software FJ.

Centraliza el registro de eventos y errores en el archivo
logs/sistema.log. Toda la información se guarda únicamente
en archivos de texto: el sistema no utiliza bases de datos.
"""

import logging
import os
import traceback

from datetime import datetime

# Rutas relativas al proyecto.
RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
RUTA_LOGS = os.path.join(RUTA_PROYECTO, "logs")
RUTA_ARCHIVO = os.path.join(RUTA_LOGS, "sistema.log")

_FORMATO = "%(asctime)s - %(levelname)s - %(message)s"

_logger = None


def obtener_logger():
    """Devuelve (y configura una única vez) el logger del sistema."""

    global _logger

    if _logger is None:
        try:
            os.makedirs(RUTA_LOGS, exist_ok=True)

            logger = logging.getLogger("software_fj")

            if not logger.handlers:
                manejador = logging.FileHandler(
                    RUTA_ARCHIVO,
                    mode="a",
                    encoding="utf-8",
                )
                manejador.setFormatter(logging.Formatter(_FORMATO))
                logger.addHandler(manejador)

            logger.setLevel(logging.INFO)
            logger.propagate = False
            _logger = logger

        except (OSError, PermissionError) as error:
            # Si el archivo no puede escribirse, se informa por consola y el sistema continúa operando sin detenerse.
            print(f"[BITÁCORA] No fue posible abrir el archivo de logs: {error}")
            _logger = logging.getLogger("software_fj")

    return _logger


def registrar_evento(mensaje):
    """Registra un evento normal del sistema."""

    try:
        obtener_logger().info(mensaje)
    except Exception as error:
        print(f"[BITÁCORA] Error al registrar el evento: {error}")


def registrar_error(mensaje):
    """Registra un error detectado por el sistema."""

    try:
        obtener_logger().error(mensaje)
    except Exception as error:
        print(f"[BITÁCORA] Error al registrar el error: {error}")


def registrar_error_detallado(mensaje, error):
    """Registra un error con su tipo, mensaje y traza técnica."""

    traza = "".join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    registrar_error(f"{mensaje} | {type(error).__name__}: {error} | {traza.strip()}")


def leer_bitacora(cantidad=200):
    """Devuelve las últimas líneas del archivo de logs."""

    try:
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        return ["(La bitácora aún no ha sido creada.)"]
    except OSError as error:
        return [f"(No fue posible leer la bitácora: {error})"]

    seleccion = lineas[-cantidad:]
    return [linea.rstrip("\n") for linea in seleccion]


def resumen_bitacora():
    """Cuenta eventos y errores registrados en la bitácora."""

    eventos = 0
    errores = 0

    try:
        with open(RUTA_ARCHIVO, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                if " - ERROR - " in linea:
                    errores += 1
                elif " - INFO - " in linea:
                    eventos += 1
    except OSError:
        pass

    return {
        "eventos": eventos,
        "errores": errores,
        "archivo": RUTA_ARCHIVO,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
