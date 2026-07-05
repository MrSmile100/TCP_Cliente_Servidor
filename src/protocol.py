from pathlib import Path


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096
MAX_LINE_SIZE = 8192
MAX_FILE_SIZE = 10 * 1024 * 1024
SOCKET_TIMEOUT = 15
CLIENT_IDLE_TIMEOUT = 300


def receive_line(sock, max_size=MAX_LINE_SIZE):
    """Recebe bytes do socket ate encontrar uma quebra de linha e devolve o texto sem o caractere final"""
    data = bytearray()

    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            break

        data.extend(chunk)

        if len(data) > max_size:
            raise ValueError("Linha recebida excedeu o limite permitido.")

    return data.decode("utf-8").strip()


def send_text(sock, text):
    """Envia uma linha de texto codificada em UTF-8 pelo socket"""
    sock.sendall(text.encode("utf-8"))


def build_message_command(message):
    """Monta o comando textual usado pelo cliente para enviar uma mensagem ao servidor"""
    return f"MSG {message}\n"


def build_file_header(filename, file_size):
    """Monta o cabecalho que informa ao servidor o nome e o tamanho do arquivo enviado"""
    return f"FILE {Path(filename).name} {file_size}\n"


def stream_file_to_socket(sock, path, buffer_size=BUFFER_SIZE):
    """Envia o conteudo de um arquivo pelo socket em blocos, sem carregar tudo na memoria"""
    with path.open("rb") as file:
        while True:
            chunk = file.read(buffer_size)
            if not chunk:
                break
            sock.sendall(chunk)


def receive_file_to_path(sock, destination, file_size, buffer_size=BUFFER_SIZE):
    """Recebe exatamente a quantidade esperada de bytes do socket e grava o arquivo em disco"""
    bytes_received = 0

    with destination.open("wb") as file:
        while bytes_received < file_size:
            remaining = file_size - bytes_received
            chunk = sock.recv(min(buffer_size, remaining))

            if not chunk:
                raise ConnectionError("Conexao encerrada antes de receber todos os bytes.")

            file.write(chunk)
            bytes_received += len(chunk)

    return bytes_received
