#!/usr/bin/env python3

import multiprocessing
import threading


data = [0]


def thread_worker():
    data[0] = 100


def process_worker():
    data[0] = 200
    print(f"Process: data={data[0]}")


def main():
    print("Initial:")
    print(f"Parent: data={data[0]}")

    thread = threading.Thread(target=thread_worker)

    thread.start()
    thread.join()

    print()
    print("After thread:")
    print(f"Parent: data={data[0]}")

    process = multiprocessing.Process(
        target=process_worker
    )

    process.start()
    process.join()

    print()
    print("After process:")
    print(f"Parent: data={data[0]}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
