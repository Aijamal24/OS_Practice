#!/usr/bin/env python3

import sys
import threading
import time


N = 5
MEALS = 3


def run_philosophers(mode):
    forks = [threading.Lock() for _ in range(N)]
    meals = [0] * N
    barrier = threading.Barrier(N) if mode == "deadlock" else None

    def philosopher(i):
        left = i
        right = (i + 1) % N

        for _ in range(MEALS):
            if mode == "ordered":
                first, second = sorted((left, right))
            elif mode == "limited":
                first, second = left, right
            else:
                first, second = left, right

            forks[first].acquire()

            try:
                if barrier:
                    # Все философы держат первую вилку одновременно.
                    barrier.wait(timeout=2)

                forks[second].acquire()
                try:
                    meals[i] += 1
                    print(f"Философ {i}: поел ({meals[i]})")
                    time.sleep(0.02)
                finally:
                    forks[second].release()
            finally:
                forks[first].release()

    if mode == "limited":
        # Одновременно к вилкам допускаются максимум N-1 философов.
        room = threading.Semaphore(N - 1)

        def limited_philosopher(i):
            with room:
                philosopher(i)

        threads = [
            threading.Thread(target=limited_philosopher, args=(i,))
            for i in range(N)
        ]
    else:
        threads = [
            threading.Thread(target=philosopher, args=(i,))
            for i in range(N)
        ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=4)

    if any(thread.is_alive() for thread in threads):
        print("\nОбнаружено зависание (deadlock).")
        return

    print("\nКоличество приёмов пищи:")
    for i, count in enumerate(meals):
        print(f"Философ {i}: {count}")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "ordered"

    if mode not in ("deadlock", "ordered", "limited"):
        print("Использование: python3 philosophers.py deadlock|ordered|limited")
        return

    print(f"Режим: {mode}")
    run_philosophers(mode)


if __name__ == "__main__":
    main()
