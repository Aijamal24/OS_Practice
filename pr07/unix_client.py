#!/usr/bin/env python3

import socket
import sys

SOCKET_PATH = "/tmp/pr07_unix.sock"


def main():
    expression = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input(
        "Введите выражение: "
    )

    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(SOCKET_PATH)
            client.sendall(expression.encode("utf-8"))
            response = client.recv(4096).decode("utf-8").strip()
            print("Ответ сервера:", response)
    except FileNotFoundError:
        print("Сервер не запущен. Сначала запусти unix_server.py.")
    except ConnectionRefusedError:
        print("Сервер не принимает подключения. Проверь, запущен ли он.")


if __name__ == "__main__":
    main()
