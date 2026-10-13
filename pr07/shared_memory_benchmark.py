#!/usr/bin/env python3

import multiprocessing as mp
from multiprocessing import shared_memory
import time
import struct

N = 10**7


def shared_memory_reader(name, size, conn):
    shm = shared_memory.SharedMemory(name=name)
    try:
        # Ждём, пока родитель заполнит массив.
        conn.recv()
        start = time.perf_counter()

        view = shm.buf[:size]
        total = 0
        for i in range(0, size, 8):
            total += struct.unpack_from("d", view, i)[0]

        elapsed = time.perf_counter() - start
        conn.send((total, elapsed))
    finally:
        shm.close()
        conn.close()


def pipe_reader(conn):
    try:
        data = conn.recv_bytes()
        start = time.perf_counter()

        count = len(data) // 8
        total = 0
        for i in range(count):
            total += struct.unpack_from("d", data, i * 8)[0]

        elapsed = time.perf_counter() - start
        conn.send((total, elapsed))
    finally:
        conn.close()


def main():
    size = N * 8
    print(f"Количество чисел: {N:,}".replace(",", " "))
    print(f"Размер массива: {size / (1024 * 1024):.2f} MiB")

    shm = shared_memory.SharedMemory(create=True, size=size)
    parent_conn, child_conn = mp.Pipe()

    try:
        process = mp.Process(
            target=shared_memory_reader,
            args=(shm.name, size, child_conn),
        )
        process.start()
        child_conn.close()

        start = time.perf_counter()
        for i in range(N):
            struct.pack_into("d", shm.buf, i * 8, float(i))
        fill_time = time.perf_counter() - start

        parent_conn.send("ready")
        total, read_time = parent_conn.recv()
        process.join()

        print("\n--- Shared memory ---")
        print(f"Время заполнения: {fill_time:.3f} с")
        print(f"Время чтения и суммирования: {read_time:.3f} с")
        print(f"Сумма: {total:.0f}")

        # Сравнение передачи тех же данных через Pipe.
        data = bytearray(size)
        for i in range(N):
            struct.pack_into("d", data, i * 8, float(i))

        receiver, sender = mp.Pipe(duplex=True)
        process2 = mp.Process(target=pipe_reader, args=(receiver,))
        process2.start()
        receiver.close()

        start = time.perf_counter()
        sender.send_bytes(data)
        transfer_time = time.perf_counter() - start

        total2, pipe_read_time = sender.recv()
        process2.join()

        print("\n--- Pipe ---")
        print(f"Время отправки данных: {transfer_time:.3f} с")
        print(f"Время чтения и суммирования: {pipe_read_time:.3f} с")
        print(f"Сумма: {total2:.0f}")

    finally:
        parent_conn.close()
        shm.close()
        shm.unlink()


if __name__ == "__main__":
    mp.freeze_support()
    main()
