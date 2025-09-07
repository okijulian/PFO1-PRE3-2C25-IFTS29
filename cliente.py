import socket
import threading

HOST = 'localhost'
PORT = 5000

shutdown_event = threading.Event()

def receive_messages(s):
    """Recibe mensajes del servidor de forma continua."""
    while not shutdown_event.is_set():
        try:
            s.settimeout(1.0)
            data = s.recv(1024)
            if not data:
                if not shutdown_event.is_set():
                    print("\nEl servidor cerró la conexión.")
                break
            
            print(f"\nMensaje recibido: {data.decode('utf-8')}")
            print("> ", end="", flush=True)

        except socket.timeout:
            continue
        except (ConnectionAbortedError, ConnectionResetError):
            if not shutdown_event.is_set():
                print("\nLa conexión fue terminada.")
            break
        except Exception as e:
            if not shutdown_event.is_set():
                print(f"\nError en el hilo de recepción: {e}")
            break

def main():
    """Función principal del cliente."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Conectado al servidor en {HOST}:{PORT}")
            print("Escribe 'salir' para terminar.")

            recv_thread = threading.Thread(target=receive_messages, args=(s,))
            recv_thread.start()

            while True:
                try:
                    mensaje = input("> ")
                    if not mensaje:
                        continue

                    if mensaje.lower() == 'salir':
                        print("Cerrando conexión...")
                        break

                    s.sendall(mensaje.encode('utf-8'))

                except (BrokenPipeError, ConnectionResetError):
                    print("\nError: La conexión se ha roto. No se pudo enviar el mensaje.")
                    break
                except KeyboardInterrupt:
                    print("\nCerrando cliente por interrupción.")
                    break

    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar al servidor en {HOST}:{PORT}. ¿Está el servidor en ejecución?")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        shutdown_event.set()        
        if 'recv_thread' in locals() and recv_thread.is_alive():
            recv_thread.join()
        print("Cliente desconectado.")

if __name__ == "__main__":
    main()
