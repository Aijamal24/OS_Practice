#!/usr/bin/env python3

import multiprocessing
import threading
import time


FILENAME = "numbers.txt"
WORKERS = 4


def read_numbers():
    with open(FILENAME, "r") as file:
        return [int(line) for line in file]


def single_thread(numbers):
    return sum(numbers)


def thread_worker(numbers, start, end, results, index):
    results[index] = sum(numbers[start:end])


def four_threads(numbers):
    results = [0] * WORKERS
    threads = []

    chunk = len(numbers) // WORKERS

    for i in range(WORKERS):
        start = i * chunk
        end = len(numbers) if i == WORKERS - 1 else (i + 1) * chunk

        thread = threading.Thread(
            target=thread_worker,
            args=(numbers, start, end, results, i),
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)


def process_worker(numbers, start, end, queue):
    result = sum(numbers[start:end])
    queue.put(result)


def four_processes(numbers):
    processes = []
    queue = multiprocessing.Queue()

    chunk = len(numbers) // WORKERS

    for i in range(WORKERS):
        start = i * chunk
        end = len(numbers) if i == WORKERS - 1 else (i + 1) * chunk

        process = multiprocessing.Process(
            target=process_worker,
            args=(numbers, start, end, queue),
        )

        processes.append(process)
        process.start()

    results = []

    for _ in processes:
        results.append(queue.get())

    for process in processes:
        process.join()

    return sum(results)


def measure(function, numbers):
    start = time.perf_counter()

    result = function(numbers)

    elapsed = time.perf_counter() - start

    return result, elapsed


def median(values):
    return sorted(values)[len(values) // 2]


def run_test(name, function, numbers):
    times = []
    result = None

    for run in range(1, 4):
        result, elapsed = measure(function, numbers)

        times.append(elapsed)

        print(
            f"{name}: run {run}: "
            f"{elapsed:.6f} s, sum={result}"
        )

    med = median(times)

    print(
        f"{name}: median={med:.6f} s, "
        f"sum={result}"
    )

    print()

    return result, med


def main():
    print("Loading numbers...")

    numbers = read_numbers()

    print(f"Numbers loaded: {len(numbers)}")
    print()

    run_test(
        "1 thread",
        single_thread,
        numbers,
    )

    run_test(
        "4 threads",
        four_threads,
        numbers,
    )

    run_test(
        "4 processes",
        four_processes,
        numbers,
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
