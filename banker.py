#!/usr/bin/env python3

import sys


def load_state(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = [
            list(map(int, line.split()))
            for line in file
            if line.strip()
        ]

    n, m = lines[0]
    available = lines[1]
    allocation = lines[2:2 + n]
    maximum = lines[2 + n:2 + 2 * n]

    if len(available) != m:
        raise ValueError("Неверная длина Available")
    if len(allocation) != n or len(maximum) != n:
        raise ValueError("В файле должны быть данные всех процессов")
    if any(len(row) != m for row in allocation + maximum):
        raise ValueError("Неверное число ресурсов в строке")
    if any(
        allocation[i][j] > maximum[i][j]
        for i in range(n)
        for j in range(m)
    ):
        raise ValueError("Allocation не может превышать Max")

    need = [
        [maximum[i][j] - allocation[i][j] for j in range(m)]
        for i in range(n)
    ]

    return available, allocation, maximum, need


def safe_sequence(available, allocation, need):
    work = available[:]
    finished = [False] * len(allocation)
    sequence = []

    while len(sequence) < len(allocation):
        found = False

        for i in range(len(allocation)):
            if finished[i]:
                continue

            if all(need[i][j] <= work[j] for j in range(len(work))):
                work = [
                    work[j] + allocation[i][j]
                    for j in range(len(work))
                ]
                finished[i] = True
                sequence.append(i)
                found = True

        if not found:
            return False, sequence

    return True, sequence


def request_resources(pid, request, available, allocation, maximum, need):
    n = len(allocation)
    m = len(available)

    if not 0 <= pid < n:
        print("Ошибка: такого процесса нет.")
        return

    if len(request) != m or any(value < 0 for value in request):
        print("Ошибка: неверный вектор запроса.")
        return

    if any(request[j] > need[pid][j] for j in range(m)):
        print("Отказ: запрос превышает Need процесса.")
        return

    if any(request[j] > available[j] for j in range(m)):
        print("Ожидание: сейчас недостаточно доступных ресурсов.")
        return

    # Временно выделяем ресурсы.
    for j in range(m):
        available[j] -= request[j]
        allocation[pid][j] += request[j]
        need[pid][j] -= request[j]

    safe, sequence = safe_sequence(available, allocation, need)

    if safe:
        print("Запрос разрешён.")
        print("Безопасная последовательность:",
              " -> ".join(f"P{i}" for i in sequence))
    else:
        # Откат: восстанавливаем прежнее состояние.
        for j in range(m):
            available[j] += request[j]
            allocation[pid][j] -= request[j]
            need[pid][j] += request[j]

        print("Запрос отклонён: состояние небезопасно.")
        print("Изменения отменены.")


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "bank1.txt"

    try:
        available, allocation, maximum, need = load_state(filename)
    except (OSError, ValueError, IndexError) as error:
        print(f"Ошибка чтения состояния: {error}")
        return

    print(f"Файл: {filename}")
    print("Available:", available)

    safe, sequence = safe_sequence(available, allocation, need)
    if safe:
        print("Состояние безопасное.")
        print("Безопасная последовательность:",
              " -> ".join(f"P{i}" for i in sequence))
    else:
        print("Состояние небезопасное.")
        print("Не удалось завершить все процессы.")
        print("Частичная последовательность:",
              " -> ".join(f"P{i}" for i in sequence) or "(нет)")

    print("\nВвод запроса: PID R1 R2 R3")
    print("Пример: 1 1 0 2")
    print("Введите q для выхода.")

    while True:
        try:
            line = input("request> ").strip()
        except EOFError:
            break

        if line.lower() in ("q", "quit", "exit"):
            break

        try:
            values = list(map(int, line.split()))
            if len(values) != len(available) + 1:
                raise ValueError
            pid, *request = values
            request_resources(
                pid, request, available, allocation, maximum, need
            )
        except ValueError:
            print("Неверный ввод. Пример: 1 1 0 2")


if __name__ == "__main__":
    main()
