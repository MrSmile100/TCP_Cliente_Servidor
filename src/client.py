import argparse
import socket
from pathlib import Path


HOST = "127.0.0.1"
PORT = 5000


def receive_line(sock):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data.extend(chunk)
    return data.decode("utf-8").strip()


def send_message(sock, message):
    command = f"MSG {message}\n"
    sock.sendall(command.encode("utf-8"))
    print(f"[CLIENTE] Resposta: {receive_line(sock)}")


def send_file(sock, file_path):
    path = Path(file_path)
    data = path.read_bytes()
    header = f"FILE {path.name} {len(data)}\n"

    sock.sendall(header.encode("utf-8"))
    sock.sendall(data)
    print(f"[CLIENTE] Resposta: {receive_line(sock)}")


def run_client(host, port, message, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"[CLIENTE] Conectando em {host}:{port}")
        sock.connect((host, port))

        greeting = receive_line(sock)
        print(f"[CLIENTE] Servidor: {greeting}")

        send_message(sock, message)

        if file_path:
            send_file(sock, file_path)

        sock.sendall(b"QUIT\n")
        print(f"[CLIENTE] Resposta: {receive_line(sock)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Cliente TCP simples.")
    parser.add_argument("--host", default=HOST, help="Endereco do servidor.")
    parser.add_argument("--port", type=int, default=PORT, help="Porta TCP do servidor.")
    parser.add_argument(
        "--message",
        default="Ola, servidor TCP!",
        help="Mensagem de texto enviada ao servidor.",
    )
    parser.add_argument("--file", help="Caminho de um arquivo para transferir.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_client(args.host, args.port, args.message, args.file)
