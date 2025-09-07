import socket
import sqlite3
import threading
from datetime import datetime

HOST = 'localhost'
PORT = 5000

clientes = {}
clientes_lock = threading.Lock()
next_client_id = 1

def inicializar_db():
    """Crea la tabla de mensajes si no existe."""
    conn = sqlite3.connect('mensajes.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mensajes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  contenido TEXT,
                  fecha_envio TIMESTAMP,
                  ip_cliente TEXT,
                  remitente TEXT)''')
    conn.commit()
    conn.close()

def handle_client(conn, addr, client_id):
    """Maneja la conexión con un cliente."""
    print(f"Conectado con {addr} (ID: {client_id})")
    db_conn = sqlite3.connect('mensajes.db', check_same_thread=False)
    c = db_conn.cursor()

    with clientes_lock:
        clientes[client_id] = conn

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            mensaje = data.decode('utf-8')
            if mensaje.lower() == 'salir':
                break

            timestamp = datetime.now()
            print(f"Mensaje de {addr[0]} (ID: {client_id}): {mensaje}")

            try:
                c.execute("INSERT INTO mensajes (contenido, fecha_envio, ip_cliente, remitente) VALUES (?, ?, ?, ?)",
                          (mensaje, timestamp, addr[0], f"Cliente {client_id}"))
                db_conn.commit()
            except sqlite3.Error as e:
                print(f"Error al insertar en la base de datos: {e}")
                db_conn.rollback()

            respuesta = f"Mensaje recibido: '{mensaje}'"
            conn.sendall(respuesta.encode('utf-8'))

    except ConnectionResetError:
        print(f"Conexión con {addr} (ID: {client_id}) cerrada abruptamente.")
    except Exception as e:
        print(f"Error con el cliente {addr} (ID: {client_id}): {e}")
    finally:
        with clientes_lock:
            if client_id in clientes:
                del clientes[client_id]
        
        db_conn.close()
        conn.close()
        print(f"Desconectado de {addr} (ID: {client_id})")

def manage_server_input():
    """Maneja la entrada de la consola del servidor para enviar mensajes."""
    print("Comandos del servidor: 'enviar <ID> <mensaje>', 'listar', 'salir'")
    while True:
        cmd = input()
        if cmd.lower() == 'listar':
            with clientes_lock:
                if not clientes:
                    print("No hay clientes conectados.")
                else:
                    print("Clientes conectados:")
                    for cid in clientes:
                        print(f"  - ID: {cid}")
        elif cmd.lower().startswith('enviar'):
            try:
                parts = cmd.split(' ', 2)
                if len(parts) < 3:
                    print("Uso: enviar <ID_cliente> <mensaje>")
                    continue
                client_id = int(parts[1])
                mensaje = parts[2]
                with clientes_lock:
                    if client_id in clientes:
                        clientes[client_id].sendall(mensaje.encode('utf-8'))
                        print(f"Mensaje enviado al cliente {client_id}.")
                    else:
                        print(f"Error: No se encontró el cliente con ID {client_id}.")
            except ValueError:
                print("Error: El ID debe ser un número.")
            except Exception as e:
                print(f"Error al enviar mensaje: {e}")
        elif cmd.lower() == 'salir':
            print("Cerrando el servidor...")
            with clientes_lock:
                for conn in clientes.values():
                    conn.close()
            break
        else:
            print("Comando no reconocido.")

def main():
    """Función principal del servidor."""
    global next_client_id
    inicializar_db()

    server_input_thread = threading.Thread(target=manage_server_input)
    server_input_thread.daemon = True
    server_input_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen()
            print(f"Servidor escuchando en {HOST}:{PORT}")

            while True:
                conn, addr = s.accept()
                with clientes_lock:
                    client_id = next_client_id
                    next_client_id += 1
                client_thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
                client_thread.start()

        except OSError as e:
            print(f"Error de socket: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()
