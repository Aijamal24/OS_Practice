#!/usr/bin/env python3

import threading

THREADS = 4
INCREMENTS = 100_000

counter = 0


def worker():
    global counter

    for _ in range(INCREMENTS):
        # Намеренно отсутствует блокировка:
        # чтение, увеличение и запись не защищены.
        value = counter
        value += 1
        counter = value


def main():
    global counter

    threads = [
        threading.Thread(target=worker)
        for _ in range(THREADS)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    expected = THREADS * INCREMENTS

    print(f"Ожидаемое значение: {expected}")
    print(f"Фактическое значение: {counter}")

    if counter != expected:
        print("Обнаружена гонка данных: результат неверный.")
    else:
        print(
            "В этом запуске значения совпали. "
            "Это не доказывает отсутствие гонки."
        )


if __name__ == "__main__":
    main()
