"""
Interfaz gráfica del sistema Software FJ.

Aplicación construida con Tkinter que permite gestionar
clientes, servicios y reservas, ejecutar la simulación
de operaciones y consultar la bitácora de eventos.

Toda la interacción está protegida con bloques
try/except/else/finally: ningún error detiene la ventana.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from bitacora import leer_bitacora, registrar_error, registrar_evento
from bitacora import registrar_error_detallado, resumen_bitacora
from excepciones import DatosInvalidosError, SoftwareFJError
from sistema import SistemaFJ, etiqueta_servicio

# MAPEO DE TIPOS DE SERVICIOS

TIPOS_VISIBLES = (
    "Reserva de sala",
    "Alquiler de equipo",
    "Asesoría especializada",
)

MAPEO_TIPOS = {
    "Reserva de sala": "sala",
    "Alquiler de equipo": "equipo",
    "Asesoría especializada": "asesoria",
}

# FUNCIONES AUXILIARES DE VALIDACIÓN

def texto_obligatorio(valor, etiqueta):
    """Convierte un valor a texto obligatorio no vacío."""

    texto = "" if valor is None else str(valor).strip()

    if not texto:
        raise DatosInvalidosError(f"{etiqueta} es obligatorio.")

    return texto


def a_entero(valor, etiqueta):
    """Convierte un valor a entero encadenando el error original."""

    texto = "" if valor is None else str(valor).strip()

    if not texto:
        raise DatosInvalidosError(f"{etiqueta} es obligatorio.")

    try:
        return int(texto)
    except (ValueError, TypeError) as error:
        raise DatosInvalidosError(f"{etiqueta} debe ser un número entero.") from error


def a_decimal(valor, etiqueta):
    """Convierte un valor a número decimal encadenando el error original."""

    texto = "" if valor is None else str(valor).strip()

    if not texto:
        raise DatosInvalidosError(f"{etiqueta} es obligatorio.")

    try:
        return float(texto)
    except (ValueError, TypeError) as error:
        raise DatosInvalidosError(
            f"{etiqueta} debe ser un valor numérico."
        ) from error


def crear_formulario(parent, campos):
    """Crea un formulario de dos columnas y devuelve sus entradas."""

    entradas = {}

    for indice, (clave, etiqueta) in enumerate(campos):
        fila = indice // 2
        columna = (indice % 2) * 2

        etiqueta_widget = ttk.Label(parent, text=etiqueta)
        etiqueta_widget.grid(row=fila, column=columna, sticky="e", padx=6, pady=5)

        entrada = ttk.Entry(parent, width=32)
        entrada.grid(row=fila, column=columna + 1, sticky="we", padx=6, pady=5)
        entradas[clave] = entrada

    parent.columnconfigure(1, weight=1)
    parent.columnconfigure(3, weight=1)

    return entradas


def crear_lista(parent, columnas, anchos):
    """Crea un Treeview con scrollbars y lo devuelve."""

    marco = ttk.Frame(parent)
    marco.pack(fill="both", expand=True, padx=8, pady=8)

    arbol = ttk.Treeview(marco, columns=columnas, show="headings", height=10)

    for nombre, ancho in zip(columnas, anchos):
        arbol.heading(nombre, text=nombre.capitalize())
        arbol.column(nombre, width=ancho, anchor="w", stretch=True)

    scroll_vertical = ttk.Scrollbar(
        marco, orient="vertical", command=arbol.yview
    )
    scroll_horizontal = ttk.Scrollbar(
        marco, orient="horizontal", command=arbol.xview
    )

    arbol.configure(
        yscrollcommand=scroll_vertical.set,
        xscrollcommand=scroll_horizontal.set,
    )

    arbol.grid(row=0, column=0, sticky="nsew")
    scroll_vertical.grid(row=0, column=1, sticky="ns")
    scroll_horizontal.grid(row=1, column=0, sticky="ew")

    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)

    return arbol


def agregar_texto_scroll(parent, estado_inicial="disabled"):
    """Crea un cuadro de texto con scroll y lo devuelve."""

    marco = ttk.Frame(parent)
    marco.pack(fill="both", expand=True, padx=8, pady=8)

    texto = tk.Text(marco, wrap="none", height=20, state=estado_inicial)
    scroll_vertical = ttk.Scrollbar(
        marco, orient="vertical", command=texto.yview
    )
    scroll_horizontal = ttk.Scrollbar(
        marco, orient="horizontal", command=texto.xview
    )

    texto.configure(
        yscrollcommand=scroll_vertical.set,
        xscrollcommand=scroll_horizontal.set,
    )

    texto.grid(row=0, column=0, sticky="nsew")
    scroll_vertical.grid(row=0, column=1, sticky="ns")
    scroll_horizontal.grid(row=1, column=0, sticky="ew")

    marco.rowconfigure(0, weight=1)
    marco.columnconfigure(0, weight=1)

    return texto

# APLICACIÓN PRINCIPAL

class AplicacionSoftwareFJ:
    """Ventana principal del sistema Software FJ."""

    def __init__(self, root, sistema=None):
        self.__root = root
        self.__sistema = sistema if sistema is not None else SistemaFJ()

        self.__lista_clientes = []
        self.__lista_servicios = []
        self.__lista_reservas = []

        self.__root.title("Software FJ - Sistema Integral de Gestión")
        self.__root.geometry("1020x680")
        self.__root.minsize(900, 600)

        # self.__crear_menu()
        self.__crear_pestanas()
        self.__crear_barra_estado()
        self.__refrescar()

        registrar_evento("Interfaz gráfica abierta correctamente.")

    # ESTRUCTURA GENERAL

    def __crear_menu(self):
        barra = tk.Menu(self.__root)

        menu_archivo = tk.Menu(barra, tearoff=0)
        menu_archivo.add_command(
            label="Actualizar listados",
            command=self.__accion_actualizar,
        )
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.__cerrar)
        barra.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ayuda = tk.Menu(barra, tearoff=0)
        menu_ayuda.add_command(
            label="Acerca de",
            command=self.__acerca_de,
        )
        barra.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.__root.config(menu=barra)

    def __crear_pestanas(self):
        self.__pestanas = ttk.Notebook(self.__root)
        self.__pestanas.pack(fill="both", expand=True)

        self.__pestanas.add(
            self.__crear_pestana_clientes(), text="Clientes"
        )
        self.__pestanas.add(
            self.__crear_pestana_servicios(), text="Servicios"
        )
        self.__pestanas.add(
            self.__crear_pestana_reservas(), text="Reservas"
        )
        self.__pestanas.add(
            self.__crear_pestana_bitacora(), text="Bitácora"
        )

    def __crear_barra_estado(self):
        self.__variable_estado = tk.StringVar()
        barra = ttk.Label(
            self.__root,
            textvariable=self.__variable_estado,
            anchor="w",
            relief="groove",
            padding=(8, 4),
        )
        barra.pack(fill="x", side="bottom")
        self.__estado("Sistema listo.")

    def __estado(self, mensaje):
        self.__variable_estado.set(str(mensaje))

    # PESTAÑA DE CLIENTES

    def __crear_pestana_clientes(self):
        marco = ttk.Frame(self.__pestanas)

        formulario = ttk.LabelFrame(marco, text="Nuevo cliente")
        formulario.pack(fill="x", padx=8, pady=8)

        self.__entradas_cliente = crear_formulario(
            formulario,
            [
                ("nombre", "Nombre:"),
                ("documento", "Documento:"),
                ("correo", "Correo:"),
                ("telefono", "Teléfono:"),
            ],
        )

        botones = ttk.Frame(marco)
        botones.pack(fill="x", padx=8, pady=(0, 4))

        ttk.Button(
            botones, text="Registrar cliente",
            command=self.__accion_registrar_cliente,
        ).pack(side="left", padx=4)
        ttk.Button(
            botones, text="Limpiar",
            command=lambda: self.__limpiar(self.__entradas_cliente),
        ).pack(side="left", padx=4)

        self.__arbol_clientes = crear_lista(
            marco,
            ("documento", "nombre", "correo", "telefono"),
            (110, 220, 240, 140),
        )

        return marco

    def __accion_registrar_cliente(self):
        def operacion():
            entradas = self.__entradas_cliente
            return self.__sistema.registrar_cliente(
                texto_obligatorio(entradas["nombre"].get(), "El nombre"),
                texto_obligatorio(entradas["documento"].get(), "El documento"),
                texto_obligatorio(entradas["correo"].get(), "El correo"),
                texto_obligatorio(entradas["telefono"].get(), "El teléfono"),
            )

        if self.__ejecutar(operacion, "Cliente registrado correctamente."):
            self.__limpiar(self.__entradas_cliente)

    # PESTAÑA DE SERVICIOS

    def __crear_pestana_servicios(self):
        marco = ttk.Frame(self.__pestanas)

        formulario = ttk.LabelFrame(marco, text="Nuevo servicio")
        formulario.pack(fill="x", padx=8, pady=8)

        fila_tipo = ttk.Frame(formulario)
        fila_tipo.pack(fill="x", padx=6, pady=5)

        ttk.Label(fila_tipo, text="Tipo de servicio:").pack(side="left")

        self.__tipo_servicio = tk.StringVar(value=TIPOS_VISIBLES[0])
        combo_tipo = ttk.Combobox(
            fila_tipo,
            textvariable=self.__tipo_servicio,
            values=TIPOS_VISIBLES,
            state="readonly",
            width=30,
        )
        combo_tipo.pack(side="left", padx=8)
        combo_tipo.bind("<<ComboboxSelected>>", self.__actualizar_etiqueta_tipo)

        self.__var_disponible = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fila_tipo,
            text="Disponible",
            variable=self.__var_disponible,
        ).pack(side="left", padx=12)

        self.__etiqueta_adicional = ttk.Label(fila_tipo, text="Capacidad:")
        self.__etiqueta_adicional.pack(side="left", padx=8)

        contenedor_servicio = ttk.Frame(formulario)
        contenedor_servicio.pack(fill="x", padx=6, pady=5)

        self.__entradas_servicio = crear_formulario(
            contenedor_servicio,
            [
                ("codigo", "Código:"),
                ("nombre", "Nombre:"),
                ("descripcion", "Descripción:"),
                ("precio", "Precio base:"),
                ("adicional", "Campo Adicional:"),
            ],
        )
        self.__entradas_servicio["adicional"].delete(0, "end")
        self.__entradas_servicio["adicional"].insert(0, "20")

        botones = ttk.Frame(marco)
        botones.pack(fill="x", padx=8, pady=(0, 4))

        ttk.Button(
            botones, text="Registrar servicio",
            command=self.__accion_registrar_servicio,
        ).pack(side="left", padx=4)
        ttk.Button(
            botones, text="Limpiar",
            command=lambda: self.__limpiar(self.__entradas_servicio),
        ).pack(side="left", padx=4)

        self.__arbol_servicios = crear_lista(
            marco,
            ("codigo", "tipo", "nombre", "precio", "estado", "detalle"),
            (90, 150, 190, 100, 110, 220),
        )

        return marco

    def __actualizar_etiqueta_tipo(self, _evento=None):
        """Cambia la etiqueta del dato adicional según el tipo."""

        tipo = MAPEO_TIPOS.get(self.__tipo_servicio.get())

        textos = {
            "sala": "Capacidad:",
            "equipo": "Tipo de equipo:",
            "asesoria": "Especialidad:",
        }

        self.__etiqueta_adicional.config(
            text=textos.get(tipo, "Dato adicional:")
        )

        if tipo == "sala":
            self.__entradas_servicio["adicional"].delete(0, "end")
            self.__entradas_servicio["adicional"].insert(0, "20")

    def __accion_registrar_servicio(self):
        def operacion():
            entradas = self.__entradas_servicio
            tipo = MAPEO_TIPOS.get(self.__tipo_servicio.get())

            if tipo is None:
                raise DatosInvalidosError(
                    "Debe seleccionar un tipo de servicio válido."
                )

            adicional = entradas["adicional"].get()

            if tipo == "sala":
                dato = a_entero(adicional, "La capacidad")
            else:
                dato = texto_obligatorio(
                    adicional,
                    "El tipo de equipo" if tipo == "equipo"
                    else "La especialidad",
                )

            return self.__sistema.registrar_servicio(
                tipo,
                texto_obligatorio(entradas["codigo"].get(), "El código"),
                texto_obligatorio(entradas["nombre"].get(), "El nombre"),
                texto_obligatorio(
                    entradas["descripcion"].get(), "La descripción"
                ),
                a_decimal(entradas["precio"].get(), "El precio base"),
                bool(self.__var_disponible.get()),
                dato,
            )

        if self.__ejecutar(operacion, "Servicio registrado correctamente."):
            self.__limpiar(self.__entradas_servicio)

    # PESTAÑA DE RESERVAS

    def __crear_pestana_reservas(self):
        marco = ttk.Frame(self.__pestanas)

        formulario = ttk.LabelFrame(marco, text="Nueva reserva")
        formulario.pack(fill="x", padx=8, pady=8)

        fila_seleccion = ttk.Frame(formulario)
        fila_seleccion.pack(fill="x", padx=6, pady=5)

        ttk.Label(fila_seleccion, text="Cliente:").pack(side="left")
        self.__combo_cliente = ttk.Combobox(
            fila_seleccion, state="readonly", width=42
        )
        self.__combo_cliente.pack(side="left", padx=6)

        ttk.Label(fila_seleccion, text="Servicio:").pack(side="left", padx=8)
        self.__combo_servicio = ttk.Combobox(
            fila_seleccion, state="readonly", width=42
        )
        self.__combo_servicio.pack(side="left", padx=6)

        contenedor_reserva = ttk.Frame(formulario)
        contenedor_reserva.pack(fill="x", padx=6, pady=5)

        self.__entradas_reserva = crear_formulario(
            contenedor_reserva,
            [
                ("duracion", "Duración:"),
                ("impuesto", "Impuesto %:"),
                ("descuento", "Descuento %:"),
            ],
        )
        self.__entradas_reserva["impuesto"].insert(0, "0")
        self.__entradas_reserva["descuento"].insert(0, "0")

        botones = ttk.Frame(marco)
        botones.pack(fill="x", padx=8, pady=(0, 4))

        ttk.Button(
            botones, text="Crear reserva",
            command=self.__accion_crear_reserva,
        ).pack(side="left", padx=4)
        ttk.Button(
            botones, text="Confirmar",
            command=self.__accion_confirmar_reserva,
        ).pack(side="left", padx=4)
        ttk.Button(
            botones, text="Procesar",
            command=self.__accion_procesar_reserva,
        ).pack(side="left", padx=4)
        ttk.Button(
            botones, text="Cancelar",
            command=self.__accion_cancelar_reserva,
        ).pack(side="left", padx=4)
        ttk.Button(
            botones, text="Limpiar",
            command=lambda: self.__limpiar(
                self.__entradas_reserva, excluir=("impuesto", "descuento")
            ),
        ).pack(side="left", padx=4)

        self.__arbol_reservas = crear_lista(
            marco,
            ("id", "cliente", "servicio", "duracion", "impuesto",
             "descuento", "estado", "costo"),
            (90, 160, 170, 80, 80, 90, 110, 110),
        )

        return marco

    def __accion_crear_reserva(self):
        def operacion():
            entradas = self.__entradas_reserva
            indice_cliente = self.__combo_cliente.current()
            indice_servicio = self.__combo_servicio.current()

            if indice_cliente < 0 or indice_cliente >= len(self.__lista_clientes):
                raise DatosInvalidosError(
                    "Debe seleccionar un cliente de la lista."
                )

            if indice_servicio < 0 or indice_servicio >= len(self.__lista_servicios):
                raise DatosInvalidosError(
                    "Debe seleccionar un servicio de la lista."
                )

            return self.__sistema.crear_reserva(
                self.__lista_clientes[indice_cliente],
                self.__lista_servicios[indice_servicio],
                a_decimal(entradas["duracion"].get(), "La duración"),
                a_decimal(
                    entradas["impuesto"].get().strip() or "0", "El impuesto"
                ),
                a_decimal(
                    entradas["descuento"].get().strip() or "0", "El descuento"
                ),
            )

        if self.__ejecutar(operacion, "Reserva creada correctamente."):
            self.__limpiar(
                self.__entradas_reserva, excluir=("impuesto", "descuento")
            )

    def __seleccionar_reserva(self):
        """Obtiene la reserva seleccionada en la lista."""

        seleccion = self.__arbol_reservas.selection()

        if not seleccion:
            raise DatosInvalidosError(
                "Debe seleccionar una reserva de la lista."
            )

        identificador = seleccion[0]

        for reserva in self.__lista_reservas:
            if reserva.id == identificador:
                return reserva

        raise DatosInvalidosError(
            "La reserva seleccionada ya no está disponible."
        )

    def __accion_confirmar_reserva(self):
        self.__ejecutar(
            lambda: self.__sistema.confirmar_reserva(
                self.__seleccionar_reserva()
            ),
            "Reserva confirmada correctamente.",
        )

    def __accion_procesar_reserva(self):
        def operacion():
            reserva = self.__seleccionar_reserva()
            costo = self.__sistema.procesar_reserva(reserva)
            messagebox.showinfo(
                "Reserva procesada",
                f"Costo total: ${costo:,.2f}",
                parent=self.__root,
            )
            return reserva

        self.__ejecutar(operacion, "Reserva procesada correctamente.")

    def __accion_cancelar_reserva(self):
        self.__ejecutar(
            lambda: self.__sistema.cancelar_reserva(
                self.__seleccionar_reserva()
            ),
            "Reserva cancelada correctamente.",
        )

    # PESTAÑA DE BITÁCORA

    def __crear_pestana_bitacora(self):
        marco = ttk.Frame(self.__pestanas)

        superior = ttk.Frame(marco)
        superior.pack(fill="x", padx=8, pady=8)

        ttk.Button(
            superior, text="Actualizar bitácora",
            command=self.__accion_bitacora,
        ).pack(side="left", padx=4)

        self.__etiqueta_bitacora = ttk.Label(superior, text="")
        self.__etiqueta_bitacora.pack(side="left", padx=8)

        self.__texto_bitacora = agregar_texto_scroll(marco)

        return marco

    def __accion_bitacora(self):
        try:
            lineas = leer_bitacora(300)
            resumen = resumen_bitacora()

        except Exception as error:
            registrar_error(
                f"Error inesperado leyendo la bitácora: "
                f"{type(error).__name__}: {error}"
            )
            messagebox.showerror(
                "Bitácora no disponible",
                f"{type(error).__name__}: {error}",
                parent=self.__root,
            )

        else:
            self.__texto_bitacora.config(state="normal")
            self.__texto_bitacora.delete("1.0", "end")
            self.__texto_bitacora.insert("1.0", "\n".join(lineas))
            self.__texto_bitacora.see("end")
            self.__texto_bitacora.config(state="disabled")
            self.__etiqueta_bitacora.config(
                text=(
                    f"Eventos: {resumen['eventos']} | "
                    f"Errores: {resumen['errores']}"
                )
            )
            self.__estado("Bitácora actualizada.")

    # OPERACIÓN GENÉRICA CON MANEJO DE EXCEPCIONES

    def __ejecutar(self, operacion, mensaje_exito):
        """
        Ejecuta una operación protegida por
        try/except/else/finally.
        """

        resultado = None

        try:
            self.__root.config(cursor="watch")
            resultado = operacion()

        except SoftwareFJError as error:
            # El detalle del error ya fue registrado en la bitácora.
            messagebox.showerror(
                "Operación rechazada", str(error), parent=self.__root
            )
            self.__estado(f"Operación rechazada: {error}")
            resultado = None

        except Exception as error:
            registrar_error_detallado(
                "Error inesperado en la interfaz", error
            )
            messagebox.showerror(
                "Error inesperado",
                f"{type(error).__name__}: {error}\n"
                f"La aplicación continúa operando.",
                parent=self.__root,
            )
            self.__estado("Error inesperado registrado en la bitácora.")
            resultado = None

        else:
            messagebox.showinfo(
                "Operación exitosa", mensaje_exito, parent=self.__root
            )
            self.__estado(mensaje_exito)

        finally:
            self.__root.config(cursor="")
            self.__refrescar()

        return resultado

    # ACTUALIZACIÓN DE LISTADOS

    def __refrescar(self):
        """Actualiza listas, combinaciones y barra de estado."""

        try:
            self.__lista_clientes = list(self.__sistema.clientes)
            self.__lista_servicios = list(self.__sistema.servicios)
            self.__lista_reservas = list(self.__sistema.reservas)

            self.__llenar_arbol(
                self.__arbol_clientes,
                [
                    (c.documento, c.nombre, c.correo, c.telefono)
                    for c in self.__lista_clientes
                ],
            )

            self.__llenar_arbol(
                self.__arbol_servicios,
                [
                    (
                        s.codigo,
                        etiqueta_servicio(s),
                        s.nombre,
                        f"${s.precio_base:,.2f}",
                        "Disponible" if s.disponible else "No disponible",
                        s.describir(),
                    )
                    for s in self.__lista_servicios
                ],
            )

            self.__llenar_arbol(
                self.__arbol_reservas,
                [
                    (
                        r.id[:8],
                        r.cliente.nombre,
                        r.servicio.nombre,
                        f"{r.duracion:g}",
                        f"{r.porcentaje_impuesto:g}%",
                        f"{r.porcentaje_descuento:g}%",
                        r.estado,
                        (
                            f"${r.costo_final:,.2f}"
                            if r.costo_final is not None
                            else "-"
                        ),
                    )
                    for r in self.__lista_reservas
                ],
                identificadores=[r.id for r in self.__lista_reservas],
            )

            self.__combo_cliente["values"] = [
                f"{c.documento} - {c.nombre}"
                for c in self.__lista_clientes
            ]
            self.__combo_servicio["values"] = [
                f"{s.codigo} - {s.nombre}"
                for s in self.__lista_servicios
            ]

            if self.__combo_cliente.current() < 0 and self.__lista_clientes:
                self.__combo_cliente.current(0)

            if self.__combo_servicio.current() < 0 and self.__lista_servicios:
                self.__combo_servicio.current(0)

            estadisticas = self.__sistema.estadisticas()
            self.__estado(
                f"Clientes: {estadisticas['clientes']} | "
                f"Servicios: {estadisticas['servicios']} | "
                f"Reservas: {estadisticas['reservas']} "
                f"({estadisticas['confirmadas']} confirmadas, "
                f"{estadisticas['procesadas']} procesadas)"
            )

        except Exception as error:
            registrar_error(
                f"Error refrescando los listados: "
                f"{type(error).__name__}: {error}"
            )

    @staticmethod
    def __llenar_arbol(arbol, filas, identificadores=None):
        """Vuelve a poblar un Treeview con las filas indicadas."""

        arbol.delete(*arbol.get_children())

        for indice, fila in enumerate(filas):
            if identificadores is None:
                arbol.insert("", "end", values=fila)
            else:
                arbol.insert(
                    "", "end", iid=identificadores[indice], values=fila
                )

    @staticmethod
    def __limpiar(entradas, excluir=()):
        """Borra el contenido de las entradas indicadas."""

        for clave, entrada in entradas.items():
            if clave in excluir:
                continue
            entrada.delete(0, "end")

    # OPCIONES DE MENÚ

    def __accion_actualizar(self):
        self.__refrescar()
        self.__accion_bitacora()
        self.__estado("Listados y bitácora actualizados.")

    def __acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "Sistema Integral de Gestión de Clientes, Servicios "
            "y Reservas\n\n"
            "Software FJ\n"
            "Arquitectura orientada a objetos sin bases de datos.\n"
            "Los eventos y errores se registran en logs/sistema.log.",
            parent=self.__root,
        )

    def __cerrar(self):
        registrar_evento("Interfaz gráfica cerrada por el usuario.")
        self.__root.destroy()

# PUNTO DE ENTRADA

def abrir_interfaz(sistema=None):
    """Crea la ventana principal y ejecuta el bucle de eventos."""

    root = tk.Tk()
    AplicacionSoftwareFJ(root, sistema)
    root.mainloop()
    return root


if __name__ == "__main__":
    try:
        abrir_interfaz()

    except tk.TclError as error:
        registrar_error(f"No fue posible abrir la interfaz: {error}")
        print(f"No fue posible abrir la interfaz gráfica: {error}")

    except Exception as error:
        registrar_error(
            f"Error inesperado en la interfaz: "
            f"{type(error).__name__}: {error}"
        )
        print(f"Error inesperado: {type(error).__name__}: {error}")

    finally:
        print("Fin de la interfaz gráfica de Software FJ.")
