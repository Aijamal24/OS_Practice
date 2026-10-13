#!/usr/bin/env python3

import threading
import time

THREADS = 4
PHASES = 3

condition = threading.Condition()
waiting = 0
generation = 0


def barrier():
    global waiting, generation

    with condition:
        current_generation = generation
        waiting += 1

        if waiting == THREADS:
            # Последний прибывший поток открывает барьер.
            waiting = 0
            generation += 1
            condition.notify_all()
        else:
            # Остальные ждут, пока сменится поколение барьера.
            while generation == current_generation:
                condition.wait()


def worker(thread_id):
    for phase in range(1, PHASES + 1):
        print(f"Поток {thread_id}: начал фазу {phase}")

        # Имитируем работу, которая занимает разное время.
        time.sleep(0.1 * (thread_id + 1))

        print(f"Поток {thread_id}: завершил работу в фазе {phase}")

        barrier()

        print(f"Поток {thread_id}: перешёл к фазе {phase + 1}"
              if phase < PHASES
              else f"Поток {thread_id}: все фазы завершены")


def main():
    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(THREADS)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("Все 4 потока завершили 3 фазы.")


if __name__ == "__main__":
    main()
