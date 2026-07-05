import argparse
import socket
from pathlib import Path


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096
RECEIVED_DIR = Path("recebidos")


def receive_line(connection):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = connection.recv(1)
        if not chunk:
            break
        data.extend(chunk)
    return data.decode("utf-8").strip()


def receive_exactly(connection, size):
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(min(BUFFER_SIZE, size - len(data)))
        if not chunk:
            raise ConnectionError("Conexao encerrada antes de receber todos os bytes.")
        data.extend(chunk)
    return bytes(data)


def handle_client(connection, address):
    print(f"[SERVIDOR] Cliente conectado: {address[0]}:{address[1]}", flush=True)

    with connection:
        connection.sendall(b"Bem-vindo ao servidor TCP. Use MSG, FILE ou QUIT.\n")

        while True:
            command_line = receive_line(connection)
            if not command_line:
                print("[SERVIDOR] Cliente encerrou a conexao.", flush=True)
                break

            parts = command_line.split(" ", 2)
            command = parts[0].upper()

            if command == "MSG":
                message = command_line[4:] if command_line.startswith("MSG ") else ""
                print(f"[SERVIDOR] Mensagem recebida: {message}")
                response = f"ACK MSG {len(message.encode('utf-8'))} bytes recebidos\n"
                connection.sendall(response.encode("utf-8"))

            elif command == "FILE":
                if len(parts) < 3:
                    connection.sendall(b"ERRO formato esperado: FILE nome tamanho\n")
                    continue

                filename = Path(parts[1]).name
                try:
                    file_size = int(parts[2])
                except ValueError:
                    connection.sendall(b"ERRO tamanho de arquivo invalido\n")
                    continue

                file_data = receive_exactly(connection, file_size)
                RECEIVED_DIR.mkdir(exist_ok=True)
                destination = RECEIVED_DIR / filename
                destination.write_bytes(file_data)

                print(
                    f"[SERVIDOR] Arquivo recebido: {destination} ({file_size} bytes)",
                    flush=True,
                )
                response = f"ACK FILE {filename} {file_size} bytes recebidos\n"
                connection.sendall(response.encode("utf-8"))

            elif command == "QUIT":
                connection.sendall(b"ACK QUIT conexao encerrada\n")
                print("[SERVIDOR] Encerrando atendimento ao cliente.", flush=True)
                break

            else:
                connection.sendall(b"ERRO comando desconhecido\n")


def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)

        print(f"[SERVIDOR] Aguardando conexoes em {host}:{port}", flush=True)
        print("[SERVIDOR] Pressione Ctrl+C para parar.", flush=True)

        while True:
            connection, address = server_socket.accept()
            handle_client(connection, address)


def parse_args():
    parser = argparse.ArgumentParser(description="Servidor TCP simples.")
    parser.add_argument("--host", default=HOST, help="Endereco para escutar.")
    parser.add_argument("--port", type=int, default=PORT, help="Porta TCP para escutar.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        start_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Finalizado pelo usuario.", flush=True)
