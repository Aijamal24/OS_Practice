#!/usr/bin/env python3

import threading

BUFFER_SIZE = 5
TOTAL_ITEMS = 1000
PRODUCERS = 3
CONSUMERS = 2

buffer = [None] * BUFFER_SIZE
in_index = 0
out_index = 0

# Сколько свободных мест и сколько готовых элементов.
empty = threading.Semaphore(BUFFER_SIZE)
full = threading.Semaphore(0)

# Защищает буфер и индексы от одновременного изменения.
mutex = threading.Lock()

consumed_items = []
consumed_lock = threading.Lock()
errors = []


def producer(producer_id, items):
    global in_index

    for item in items:
        empty.acquire()

        with mutex:
            if buffer[in_index] is not None:
                errors.append(
                    f"Переполнение: ячейка {in_index} уже занята"
                )

            buffer[in_index] = item
            in_index = (in_index + 1) % BUFFER_SIZE

        full.release()


def consumer(consumer_id):
    global out_index

    while True:
        full.acquire()

        with mutex:
            item = buffer[out_index]

            if item is None:
                errors.append(
                    f"Пустая ячейка при извлечении: {out_index}"
                )

            buffer[out_index] = None
            out_index = (out_index + 1) % BUFFER_SIZE

        empty.release()

        # Специальный маркер означает завершение работы.
        if item is None:
            errors.append("Получен неожиданный пустой элемент")
            continue

        if item == "STOP":
            break

        with consumed_lock:
            consumed_items.append(item)


def main():
    # Распределяем 1000 уникальных чисел между 3 производителями.
    producer_items = [
        list(range(i, TOTAL_ITEMS, PRODUCERS))
        for i in range(PRODUCERS)
    ]

    consumers = [
        threading.Thread(target=consumer, args=(i,))
        for i in range(CONSUMERS)
    ]

    producers = [
        threading.Thread(target=producer, args=(i, producer_items[i]))
        for i in range(PRODUCERS)
    ]

    for thread in consumers:
        thread.start()

    for thread in producers:
        thread.start()

    for thread in producers:
        thread.join()

    # После завершения производства отправляем потребителям
    # по одному маркеру остановки.
    for _ in range(CONSUMERS):
        empty.acquire()

        global in_index
        with mutex:
            buffer[in_index] = "STOP"
            in_index = (in_index + 1) % BUFFER_SIZE

        full.release()

    for thread in consumers:
        thread.join()

    expected = set(range(TOTAL_ITEMS))
    actual = set(consumed_items)

    duplicates = len(consumed_items) - len(actual)
    missing = expected - actual
    unexpected = actual - expected

    print(f"Произведено элементов: {TOTAL_ITEMS}")
    print(f"Потреблено элементов: {len(consumed_items)}")
    print(f"Размер буфера: {BUFFER_SIZE}")
    print(f"Дубликатов: {duplicates}")
    print(f"Отсутствующих элементов: {len(missing)}")
    print(f"Неожиданных элементов: {len(unexpected)}")
    print(f"Ошибок буфера: {len(errors)}")

    if errors:
        for error in errors:
            print("ОШИБКА:", error)

    if (
        len(consumed_items) == TOTAL_ITEMS
        and duplicates == 0
        and not missing
        and not unexpected
        and not errors
        and all(item is None for item in buffer)
    ):
        print("УСПЕХ: каждый элемент потреблён ровно один раз.")
        print("Буфер не переполнен, после завершения он пуст.")
    else:
        raise AssertionError("Проверка корректности не пройдена!")


if __name__ == "__main__":
    main()
