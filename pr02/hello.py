import os
import sys

if len(sys.argv) != 2:
    print(f"Использование: {sys.argv[0]} <файл>", file=sys.stderr)
    sys.exit(1)

filename = sys.argv[1]

try:
    with open(filename, "rb") as file:
        data = file.read()

    print(f"Размер файла: {len(data)} байт")

except FileNotFoundError:
    print(f"Ошибка: файл '{filename}' не найден.", file=sys.stderr)
    sys.exit(1)
