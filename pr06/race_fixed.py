#!/usr/bin/env python3

import threading

THREADS = 4
INCREMENTS = 100_000

counter = 0
mutex = threading.Lock()


def worker():
    global counter

    for _ in range(INCREMENTS):
        with mutex:
            counter += 1


def main():
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

    assert counter == expected, "Ошибка: счётчик имеет неверное значение!"
    print("Успех: мьютекс защитил общий счётчик.")


if __name__ == "__main__":
    main()
