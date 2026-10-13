#!/usr/bin/env python3

import threading

BUFFER_SIZE = 5
TOTAL_ITEMS = 1000
PRODUCERS = 3
CONSUMERS = 2

buffer = [None] * BUFFER_SIZE
in_index = 0
out_index = 0
count = 0

condition = threading.Condition()
consumed_items = []
errors = []


def producer(producer_id, items):
    global in_index, count

    for item in items:
        with condition:
            # Пока буфер заполнен, ждём освобождения места.
            while count == BUFFER_SIZE:
                condition.wait()

            if buffer[in_index] is not None:
                errors.append(
                    f"Переполнение: ячейка {in_index} занята"
                )

            buffer[in_index] = item
            in_index = (in_index + 1) % BUFFER_SIZE
            count += 1

            condition.notify_all()


def consumer(consumer_id):
    global out_index, count

    while True:
        with condition:
            # Пока буфер пуст, ждём появления элемента.
            while count == 0:
                condition.wait()

            item = buffer[out_index]

            if item is None:
                errors.append(
                    f"Пустая ячейка при извлечении: {out_index}"
                )

            buffer[out_index] = None
            out_index = (out_index + 1) % BUFFER_SIZE
            count -= 1

            condition.notify_all()

        if item == "STOP":
            break

        if item is None:
            errors.append("Получен неожиданный пустой элемент")
            continue

        consumed_items.append(item)


def main():
    global in_index, count

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

    # Останавливаем потребителей специальными маркерами.
    for _ in range(CONSUMERS):
        with condition:
            while count == BUFFER_SIZE:
                condition.wait()

            buffer[in_index] = "STOP"
            in_index = (in_index + 1) % BUFFER_SIZE
            count += 1

            condition.notify_all()

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
    print(f"Элементов в буфере после завершения: {count}")

    if errors:
        for error in errors:
            print("ОШИБКА:", error)

    if (
        len(consumed_items) == TOTAL_ITEMS
        and duplicates == 0
        and not missing
        and not unexpected
        and not errors
        and count == 0
        and all(item is None for item in buffer)
    ):
        print("УСПЕХ: каждый элемент потреблён ровно один раз.")
        print("Буфер не переполнен, после завершения он пуст.")
    else:
        raise AssertionError("Проверка корректности не пройдена!")


if __name__ == "__main__":
    main()
