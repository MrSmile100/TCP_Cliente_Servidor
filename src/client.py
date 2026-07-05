import argparse
import socket
from pathlib import Path

from protocol import (
    HOST,
    MAX_FILE_SIZE,
    PORT,
    SOCKET_TIMEOUT,
    build_file_header,
    build_message_command,
    receive_line,
    send_text,
    stream_file_to_socket,
)


def connect_to_server(host, port):
    """Cria o socket TCP, conecta ao servidor e imprime a mensagem inicial recebida."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.settimeout(SOCKET_TIMEOUT)
        print(f"[CLIENTE] Conectando em {host}:{port}")
        sock.connect((host, port))

        greeting = receive_line(sock)
        print(f"[CLIENTE] Servidor: {greeting}")
        return sock
    except Exception:
        sock.close()
        raise


def send_message(sock, message):
    """Envia uma mensagem de texto ao servidor e imprime a confirmacao recebida"""
    send_text(sock, build_message_command(message))
    print(f"[CLIENTE] Resposta: {receive_line(sock)}")


def send_file(sock, file_path):
    """Valida e envia um arquivo ao servidor usando cabecalho com nome e tamanho em bytes"""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")

    if not path.is_file():
        raise ValueError(f"O caminho informado nao e um arquivo: {path}")

    file_size = path.stat().st_size

    if file_size > MAX_FILE_SIZE:
        raise ValueError(
            f"Arquivo maior que o limite de {MAX_FILE_SIZE} bytes: {file_size} bytes"
        )

    send_text(sock, build_file_header(path.name, file_size))
    stream_file_to_socket(sock, path)
    print(f"[CLIENTE] Resposta: {receive_line(sock)}")


def send_quit(sock):
    """Envia o comando QUIT ao servidor e imprime a confirmacao de encerramento."""
    send_text(sock, "QUIT\n")
    print(f"[CLIENTE] Resposta: {receive_line(sock)}")


def print_interactive_help():
    """Mostra os comandos disponiveis no modo interativo do cliente."""
    print("[CLIENTE] Modo interativo iniciado.")
    print("[CLIENTE] Digite uma mensagem e pressione Enter para enviar.")
    print("[CLIENTE] Use /file caminho/do/arquivo para transferir um arquivo.")
    print("[CLIENTE] Use /quit para encerrar a conexao.")


def handle_interactive_input(sock, user_input):
    """Interpreta uma entrada do usuario no modo interativo e retorna se o cliente deve continuar."""
    command = user_input.strip()

    if not command:
        return True

    if command.lower() in {"/quit", "quit"}:
        send_quit(sock)
        return False

    if command.lower().startswith("/file "):
        file_path = command[6:].strip().strip('"')
        send_file(sock, file_path)
        return True

    send_message(sock, user_input)
    return True


def run_client(host, port, message, file_path):
    """Cria a conexao TCP, envia mensagem e arquivo opcional, depois encerra com QUIT"""
    with connect_to_server(host, port) as sock:
        send_message(sock, message)

        if file_path:
            send_file(sock, file_path)

        send_quit(sock)


def run_interactive_client(host, port):
    """Mantem uma conexao TCP aberta para enviar varias mensagens ou arquivos em sequencia."""
    with connect_to_server(host, port) as sock:
        print_interactive_help()

        while True:
            try:
                user_input = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                send_quit(sock)
                break

            try:
                should_continue = handle_interactive_input(sock, user_input)
            except (OSError, ValueError) as error:
                print(f"[CLIENTE] Erro: {error}")
                if isinstance(error, OSError):
                    print("[CLIENTE] A conexao foi encerrada. Inicie o cliente novamente.")
                    break
                continue

            if not should_continue:
                break


def parse_args():
    """Le os argumentos de linha de comando usados para configurar o cliente TCP"""
    parser = argparse.ArgumentParser(description="Cliente TCP simples.")
    parser.add_argument("--host", default=HOST, help="Endereco do servidor.")
    parser.add_argument("--port", type=int, default=PORT, help="Porta TCP do servidor.")
    parser.add_argument(
        "--message",
        default="Ola, servidor TCP!",
        help="Mensagem de texto enviada ao servidor.",
    )
    parser.add_argument("--file", help="Caminho de um arquivo para transferir.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Mantem a conexao aberta para enviar varias mensagens.",
    )
    return parser.parse_args()


def main():
    """Executa o cliente e mostra mensagens amigaveis caso ocorram erros de rede ou arquivo"""
    args = parse_args()
    try:
        if args.interactive:
            run_interactive_client(args.host, args.port)
        else:
            run_client(args.host, args.port, args.message, args.file)
    except (ConnectionRefusedError, TimeoutError, socket.timeout) as error:
        print(f"[CLIENTE] Erro de conexao: {error}")
    except (OSError, ValueError) as error:
        print(f"[CLIENTE] Erro: {error}")


if __name__ == "__main__":
    main()
