# Chat Cliente-Servidor

Proyecto de chat simple en Python con comunicación cliente-servidor mediante sockets, manejo de múltiples clientes con hilos y almacenamiento de mensajes en una base de datos SQLite.

## Archivos

- `servidor.py`: Maneja múltiples clientes, guarda mensajes en `mensajes.db` y permite la interacción del administrador.
- `cliente.py`: Se conecta al servidor para enviar y recibir mensajes de forma asíncrona.
- `mensajes.db`: Base de datos SQLite donde se almacenan los mensajes.

## Ejecución

1.  **Iniciar Servidor:**
    ```sh
    python servidor.py
    ```

2.  **Iniciar Cliente:**
    ```sh
    python cliente.py
    ```

## Comandos

### Servidor
- `listar`: Muestra los clientes conectados.
- `enviar <ID> <mensaje>`: Envía un mensaje a un cliente específico.
- `salir`: Cierra el servidor.

### Cliente
- `salir`: Cierra la conexión.

## Estructura de la Base de Datos

La base de datos `mensajes.db` contiene una tabla `mensajes` con la siguiente estructura:

| Columna     | Tipo      | Descripción                                     |
|-------------|-----------|-------------------------------------------------|
| `id`        | INTEGER   | Identificador único del mensaje (PK).           |
| `contenido` | TEXT      | El texto del mensaje.                           |
| `fecha_envio`| TIMESTAMP | Fecha y hora en que se recibió el mensaje.      |
| `ip_cliente`| TEXT      | Dirección IP del cliente que envió el mensaje.  |
| `remitente` | TEXT      | Identificador del cliente (ej: "Cliente 1").    |
