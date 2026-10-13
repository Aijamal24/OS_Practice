#!/usr/bin/env python3

import os
import uuid

REQUEST_FIFO = "/tmp/pr07_requests"
RESPONSE_PREFIX = "/tmp/pr07_response_"


def main():
    if not os.path.exists(REQUEST_FIFO):
        print("Сервер не запущен. Сначала запусти fifo_server.py.")
        return

    client_id = uuid.uuid4().hex
    response_fifo = RESPONSE_PREFIX + client_id

    os.mkfifo(response_fifo, 0o600)

    try:
        while True:
            expression = input("Введите выражение (или exit для выхода): ")

            if expression.lower() == "exit":
                break

            # Отправляем запрос серверу.
            with open(REQUEST_FIFO, "w") as requests:
                requests.write(f"{client_id}|{expression}\n")

            # Получаем ответ через отдельный FIFO этого клиента.
            with open(response_fifo, "r") as response:
                print("Ответ сервера:", response.readline().strip())
    finally:
        if os.path.exists(response_fifo):
            os.unlink(response_fifo)


if __name__ == "__main__":
    main()
