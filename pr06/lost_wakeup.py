#!/usr/bin/env python3

import threading
import time

condition = threading.Condition()
items = []

def consumer():
    with condition:
        print("Потребитель: проверяет буфер.")

        # ОШИБКА: здесь if вместо while.
        if not items:
            print("Потребитель: буфер пуст, засыпаю.")
            condition.wait()

        # После пробуждения условие повторно НЕ проверяется.
        if not items:
            print("ОШИБКА: потребитель проснулся, но буфер всё ещё пуст!")
            return

        item = items.pop(0)
        print(f"Потребитель получил: {item}")


def producer():
    # Ждём, чтобы потребитель успел вызвать wait().
    time.sleep(0.5)

    with condition:
        items.append("A")
        print("Производитель: добавил A и отправляет уведомление.")
        condition.notify()

        # Имитируем другого потребителя, который забрал элемент
        # до того, как первый поток снова получил блокировку.
        items.clear()
        print("Другой потребитель: забрал A.")


def main():
    consumer_thread = threading.Thread(target=consumer)
    producer_thread = threading.Thread(target=producer)

    consumer_thread.start()
    producer_thread.start()

    consumer_thread.join()
    producer_thread.join()

    print("Эксперимент завершён.")


if __name__ == "__main__":
    main()
