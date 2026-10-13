#!/usr/bin/env python3

import ast
import os
import socket
import multiprocessing

SOCKET_PATH = "/tmp/pr07_unix.sock"


def calculate(expression):
    tree = ast.parse(expression, mode="eval")

    binary_ops = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
    }

    unary_ops = {
        ast.UAdd: lambda a: a,
        ast.USub: lambda a: -a,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in binary_ops:
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Слишком большая степень")
            result = binary_ops[type(node.op)](left, right)
            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Результат слишком большой")
            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
            return unary_ops[type(node.op)](evaluate(node.operand))

        raise ValueError("Недопустимое выражение")

    return evaluate(tree)


def handle_client(connection, address):
    try:
        with connection:
            data = connection.recv(4096).decode("utf-8").strip()
            if not data:
                return

            try:
                result = calculate(data)
                response = f"OK|{result}\n"
            except Exception as error:
                response = f"ERROR|{error}\n"

            connection.sendall(response.encode("utf-8"))
            print(f"Клиент PID={os.getpid()}: {data} -> {response.strip()}", flush=True)
    finally:
        pass


def main():
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        server.bind(SOCKET_PATH)
        server.listen(10)
        print(f"Unix-сервер запущен: {SOCKET_PATH}", flush=True)
        print("Ожидание клиентов. Для остановки нажми Ctrl+C.", flush=True)

        while True:
            connection, address = server.accept()
            process = multiprocessing.Process(
                target=handle_client,
                args=(connection, address),
            )
            process.start()
            connection.close()
    except KeyboardInterrupt:
        print("\nОстановка сервера...", flush=True)
    finally:
        server.close()
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        print("Сокет удалён.", flush=True)


if __name__ == "__main__":
    main()
