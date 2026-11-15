# Software FJ
## Sistema integral de gestión de clientes, servicios y reservas

Software FJ es una aplicación de consola desarrollada en Python para gestionar clientes, servicios y reservas de una empresa que ofrece reservas de salas, alquiler de equipos y asesorías especializadas.

El proyecto utiliza programación orientada a objetos y está enfocado en la validación de datos, el control de operaciones y el manejo de excepciones.

> *Alcance del proyecto:* la información operativa se administra mediante objetos y listas en memoria. La aplicación no utiliza un motor de base de datos ni conserva los registros después de finalizar la ejecución.

## 1. Objetivo del proyecto

Construir una aplicación modular, estable y extensible que permita administrar el ciclo básico de atención de un cliente: registrar sus datos, seleccionar un servicio, crear una reserva y gestionar su estado mediante operaciones controladas.

## 2. Funcionalidades del sistema

El programa principal ofrece un menú interactivo con las siguientes opciones:

| Opción | Funcionalidad |
|---|---|
| 1 | Registrar clientes |
| 2 | Consultar clientes registrados |
| 3 | Registrar servicios |
| 4 | Consultar servicios |
| 5 | Crear reservas |
| 6 | Consultar reservas |
| 7 | Gestionar reservas |
| 0 | Salir del sistema |

### 2.1 Gestión de clientes

- Registro de nombre, documento, correo electrónico y teléfono.
- Validación de los datos ingresados.
- Comprobación de documentos duplicados durante el registro.
- Consulta de los clientes registrados durante la sesión.

### 2.2 Gestión de servicios

El sistema contempla tres tipos de servicios especializados:

1. *Reserva de sala:* representa espacios destinados a reuniones y contempla la capacidad de la sala.
2. *Alquiler de equipo:* representa el alquiler de equipos y registra el tipo de equipo.
3. *Asesoría especializada:* representa servicios de asesoría y registra su especialidad.

Los servicios incluyen código, nombre, descripción, precio base y disponibilidad. El registro comprueba que no se repita el código de un servicio.

### 2.3 Gestión de reservas

Una reserva relaciona un cliente con un servicio e incorpora duración y estado.

El flujo de gestión contempla:

- Creación de reservas para clientes y servicios registrados.
- Confirmación de reservas pendientes.
- Cancelación de reservas pendientes o confirmadas.
- Procesamiento de reservas confirmadas y cálculo del costo.
- Control de operaciones no permitidas y de servicios no disponibles.

## 3. Arquitectura y organización del proyecto

El código está distribuido en módulos para separar responsabilidades:

| Archivo | Responsabilidad |
|---|---|
| software_fj.py | Punto de entrada, menú interactivo y coordinación de las operaciones. |
| entidades.py | Clase abstracta base para las entidades del sistema e identificación única. |
| clientes.py | Clase Cliente, encapsulación y validación de datos. |
| servicios.py | Clase base Servicio y servicios especializados. |
| reservas.py | Clase Reserva, validación y gestión de estados. |
| excepciones.py | Excepciones personalizadas utilizadas por los módulos. |
| README.md | Descripción, alcance e instrucciones del proyecto. |

### 3.1 Principios de programación orientada a objetos

La estructura del proyecto aplica los siguientes conceptos:

- *Abstracción:* clases base que definen características y comportamientos comunes.
- *Herencia:* reutilización de estructuras y comportamientos mediante clases derivadas.
- *Encapsulación:* protección y consulta controlada de los datos de las entidades.
- *Polimorfismo:* implementación de comportamientos específicos en los servicios especializados.
- *Validación:* comprobación de datos y condiciones antes de ejecutar operaciones.

## 4. Manejo de excepciones

El proyecto define una jerarquía de excepciones personalizadas en excepciones.py:

- SoftwareFJError: excepción base del sistema.
- DatosInvalidosError: datos que no cumplen las validaciones.
- ClienteNoEncontradoError: situaciones en las que se requiere un cliente válido y no se encuentra.
- ServicioNoDisponibleError: intentos de operar con servicios no disponibles.
- ReservaInvalidaError: datos o condiciones incorrectas en una reserva.
- OperacionNoPermitidaError: operaciones incompatibles con el estado actual de una reserva.

El programa principal captura las excepciones propias del sistema y contempla errores inesperados para evitar que un error no previsto interrumpa de forma abrupta el menú.

## 5. Requisitos del sistema

- Python 3 instalado.
- Git, si se desea clonar y actualizar el repositorio.
- No se requieren paquetes externos para ejecutar los módulos descritos.

## 6. Instalación y ejecución

### 6.1 Clonar el repositorio

bash
git clone https://github.com/camiloJara0/SoftwareFj.git


### 6.2 Entrar en la carpeta del proyecto

bash
cd SoftwareFj


### 6.3 Ejecutar el programa principal

bash
python software_fj.py


En Windows también puede utilizarse el lanzador:

bash
py software_fj.py


Una vez ejecutado, seguir las opciones que aparecen en el menú de consola.

## 7. Almacenamiento de la información

Los clientes, servicios y reservas se mantienen en listas durante la ejecución del programa.

Al cerrar la aplicación, los datos de la sesión dejan de estar disponibles. Este comportamiento responde al alcance definido para el ejercicio, que no contempla el uso de bases de datos.

## 8. Estado de desarrollo y validación

El proyecto se encuentra en desarrollo colaborativo. La integración final debe verificar de manera conjunta los módulos y los escenarios de operación, incluyendo casos válidos e inválidos de clientes, servicios y reservas.

De acuerdo con los requisitos del Anexo 3, la versión integrada debe contemplar:

- Un archivo de logs para registrar errores y eventos relevantes.
- Manejo de excepciones mediante bloques try/except, try/except/else y try/except/finally.
- Encadenamiento de excepciones.
- Validación de datos, parámetros y operaciones.
- Simulación de al menos diez operaciones completas, incluyendo escenarios exitosos y fallidos.
- Pruebas que demuestren que la aplicación continúa funcionando ante situaciones de error.

Estos elementos deben comprobarse en la versión integrada antes de considerar finalizada la validación del proyecto.

## 9. Trabajo colaborativo

El desarrollo se realiza mediante un repositorio compartido de GitHub. Los integrantes pueden contribuir mediante ramas, commits y solicitudes de integración, procurando revisar y probar los cambios antes de incorporarlos a la rama principal.

*Repositorio:* [Software FJ en GitHub](https://github.com/camiloJara0/SoftwareFj)
---

*Software FJ*  
Proyecto académico del curso Programación 213023  
Ingeniería de Sistemas  
Universidad Nacional Abierta y a Distancia (UNAD)