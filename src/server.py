import argparse
import socket
import threading
from pathlib import Path

from protocol import (
    CLIENT_IDLE_TIMEOUT,
    HOST,
    MAX_FILE_SIZE,
    PORT,
    receive_file_to_path,
    receive_line,
    send_text,
)


RECEIVED_DIR = Path("recebidos")


def handle_message(connection, command_line):
    """Processa o comando MSG, registra a mensagem recebida e envia um ACK ao cliente"""
    message = command_line[4:] if command_line.startswith("MSG ") else ""
    print(f"[SERVIDOR] Mensagem recebida: {message}", flush=True)

    response = f"ACK MSG {len(message.encode('utf-8'))} bytes recebidos\n"
    send_text(connection, response)


def build_destination_path(filename):
    """Cria um caminho dentro da pasta de recebidos sem sobrescrever arquivos ja existentes"""
    destination = RECEIVED_DIR / filename

    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = RECEIVED_DIR / f"{destination.stem}_{counter}{destination.suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def handle_file(connection, command_line):
    """Valida o comando FILE, recebe o arquivo em blocos e confirma a gravacao em disco"""
    payload = command_line[5:] if command_line.startswith("FILE ") else ""

    if " " not in payload:
        send_text(connection, "ERRO formato esperado: FILE nome tamanho\n")
        return

    filename_text, file_size_text = payload.rsplit(" ", 1)
    filename = Path(filename_text).name

    if not filename or filename in {".", ".."}:
        send_text(connection, "ERRO nome de arquivo invalido\n")
        return

    try:
        file_size = int(file_size_text)
    except ValueError:
        send_text(connection, "ERRO tamanho de arquivo invalido\n")
        return

    if file_size < 0:
        send_text(connection, "ERRO tamanho de arquivo nao pode ser negativo\n")
        return

    if file_size > MAX_FILE_SIZE:
        send_text(connection, f"ERRO arquivo excede o limite de {MAX_FILE_SIZE} bytes\n")
        return

    RECEIVED_DIR.mkdir(exist_ok=True)
    destination = build_destination_path(filename)
    bytes_received = receive_file_to_path(connection, destination, file_size)

    print(
        f"[SERVIDOR] Arquivo recebido: {destination} ({bytes_received} bytes)",
        flush=True,
    )
    response = f"ACK FILE {filename} {bytes_received} bytes recebidos\n"
    send_text(connection, response)


def handle_client(connection, address):
    """Atende um cliente conectado, interpreta comandos e encerra quando recebe QUIT ou queda de conexao"""
    print(f"[SERVIDOR] Cliente conectado: {address[0]}:{address[1]}", flush=True)

    with connection:
        connection.settimeout(CLIENT_IDLE_TIMEOUT)
        send_text(connection, "Bem-vindo ao servidor TCP. Use MSG, FILE ou QUIT.\n")

        while True:
            try:
                command_line = receive_line(connection)
            except socket.timeout:
                print(
                    "[SERVIDOR] Cliente ficou inativo por muito tempo.",
                    flush=True,
                )
                break
            except (ConnectionError, ValueError, UnicodeDecodeError) as error:
                print(f"[SERVIDOR] Erro ao receber dados: {error}", flush=True)
                send_text(connection, f"ERRO {error}\n")
                break

            if not command_line:
                print("[SERVIDOR] Cliente encerrou a conexao.", flush=True)
                break

            parts = command_line.split(" ", 2)
            command = parts[0].upper()

            if command == "MSG":
                handle_message(connection, command_line)

            elif command == "FILE":
                try:
                    handle_file(connection, command_line)
                except (ConnectionError, OSError) as error:
                    print(f"[SERVIDOR] Erro ao receber arquivo: {error}", flush=True)
                    send_text(connection, f"ERRO {error}\n")
                    break

            elif command == "QUIT":
                send_text(connection, "ACK QUIT conexao encerrada\n")
                print("[SERVIDOR] Encerrando atendimento ao cliente.", flush=True)
                break

            else:
                send_text(connection, "ERRO comando desconhecido\n")


def start_server(host, port):
    """Inicia o servidor TCP e cria uma thread para cada cliente aceito"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"[SERVIDOR] Aguardando conexoes em {host}:{port}", flush=True)
        print("[SERVIDOR] Pressione Ctrl+C para parar.", flush=True)

        while True:
            connection, address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(connection, address),
                daemon=True,
            )
            client_thread.start()


def parse_args():
    """Le os argumentos de linha de comando usados para configurar o servidor TCP"""
    parser = argparse.ArgumentParser(description="Servidor TCP simples.")
    parser.add_argument("--host", default=HOST, help="Endereco para escutar.")
    parser.add_argument("--port", type=int, default=PORT, help="Porta TCP para escutar.")
    return parser.parse_args()


def main():
    """Executa o servidor e permite encerrar o processo com Ctrl+C"""
    args = parse_args()
    try:
        start_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Finalizado pelo usuario.", flush=True)


if __name__ == "__main__":
    main()
