#!/usr/bin/env python3

import ast
import os
import signal

REQUEST_FIFO = "/tmp/pr07_requests"
RESPONSE_PREFIX = "/tmp/pr07_response_"

running = True


def stop_server(signum, frame):
    global running
    running = False


def calculate(expression):
    """Вычисляет только безопасные арифметические выражения."""
    tree = ast.parse(expression, mode="eval")

    allowed_binary = (
        ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.FloorDiv, ast.Mod, ast.Pow,
    )
    allowed_unary = (ast.UAdd, ast.USub)

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and isinstance(node.op, allowed_binary):
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Add):
                result = left + right
            elif isinstance(node.op, ast.Sub):
                result = left - right
            elif isinstance(node.op, ast.Mult):
                result = left * right
            elif isinstance(node.op, ast.Div):
                result = left / right
            elif isinstance(node.op, ast.FloorDiv):
                result = left // right
            elif isinstance(node.op, ast.Mod):
                result = left % right
            else:
                if abs(right) > 1000:
                    raise ValueError("Слишком большая степень")
                result = left ** right

            if isinstance(result, (int, float)) and abs(result) > 1e100:
                raise ValueError("Результат слишком большой")
            return result

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, allowed_unary):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value

        raise ValueError("Недопустимое выражение")

    return evaluate(tree)


def main():
    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)

    for path in [REQUEST_FIFO]:
        if os.path.exists(path):
            os.unlink(path)

    os.mkfifo(REQUEST_FIFO, 0o600)
    print(f"FIFO-сервер запущен: {REQUEST_FIFO}", flush=True)
    print("Ожидание запросов. Для остановки нажми Ctrl+C.", flush=True)

    try:
        while running:
            # Открываем FIFO на чтение и ждём клиентов.
            with open(REQUEST_FIFO, "r") as requests:
                for line in requests:
                    if not running:
                        break

                    parts = line.rstrip("\n").split("|", 1)
                    if len(parts) != 2:
                        continue

                    client_id, expression = parts
                    response_path = RESPONSE_PREFIX + client_id

                    try:
                        result = calculate(expression)
                        response = f"OK|{result}\n"
                    except Exception as error:
                        response = f"ERROR|{error}\n"

                    try:
                        with open(response_path, "w") as response_fifo:
                            response_fifo.write(response)
                    except OSError as error:
                        print(f"Не удалось ответить клиенту: {error}", flush=True)
    finally:
        if os.path.exists(REQUEST_FIFO):
            os.unlink(REQUEST_FIFO)
        print("FIFO-сервер остановлен, канал удалён.", flush=True)


if __name__ == "__main__":
    main()
