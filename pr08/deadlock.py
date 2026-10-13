#!/usr/bin/env python3

import threading


class DeadlockError(RuntimeError):
    pass


class TrackedLock:
    graph = {}
    graph_lock = threading.Lock()

    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()
        self.owner = None

    @classmethod
    def find_cycle(cls, graph, start, target):
        stack = [(start, [start])]
        visited = set()

        while stack:
            node, path = stack.pop()

            if node == target:
                return path

            if node in visited:
                continue

            visited.add(node)

            for neighbor in graph.get(node, set()):
                stack.append((neighbor, path + [neighbor]))

        return None

    def acquire(self):
        current = threading.current_thread()

        with TrackedLock.graph_lock:
            if self.owner == current:
                raise RuntimeError(
                    f"{current.name} повторно запрашивает свою блокировку"
                )

            if self.owner is not None:
                owner = self.owner

                cycle = self.find_cycle(
                    TrackedLock.graph,
                    owner.name,
                    current.name,
                )

                if cycle is not None:
                    path = [current.name] + cycle
                    raise DeadlockError(
                        "Обнаружен deadlock: " + " -> ".join(path)
                    )

                TrackedLock.graph.setdefault(current.name, set()).add(
                    owner.name
                )

        self.lock.acquire()

        with TrackedLock.graph_lock:
            TrackedLock.graph.pop(current.name, None)
            self.owner = current

    def release(self):
        current = threading.current_thread()

        with TrackedLock.graph_lock:
            if self.owner != current:
                raise RuntimeError(
                    f"{current.name} не владеет блокировкой {self.name}"
                )

            self.owner = None

        self.lock.release()


def worker(first, second):
    try:
        first.acquire()
        print(f"{threading.current_thread().name}: захвачена {first.name}")

        second.acquire()
        print(f"{threading.current_thread().name}: захвачена {second.name}")

        second.release()
        first.release()

    except DeadlockError as error:
        print(error)

    finally:
        # Освобождаем первую блокировку, если этот поток её удерживает.
        current = threading.current_thread()

        if first.owner == current:
            first.release()

        if second.owner == current:
            second.release()


def main():
    lock_a = TrackedLock("A")
    lock_b = TrackedLock("B")

    barrier = threading.Barrier(2)

    def task(first, second):
        first.acquire()
        print(f"{threading.current_thread().name}: захвачена {first.name}")

        try:
            barrier.wait(timeout=3)
            second.acquire()
            print(f"{threading.current_thread().name}: захвачена {second.name}")
            second.release()
        except DeadlockError as error:
            print(error)
        except threading.BrokenBarrierError:
            print("Барьер прерван.")
        finally:
            if first.owner == threading.current_thread():
                first.release()
            if second.owner == threading.current_thread():
                second.release()

    t1 = threading.Thread(target=task, args=(lock_a, lock_b), name="P0")
    t2 = threading.Thread(target=task, args=(lock_b, lock_a), name="P1")

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("Проверка завершена.")


if __name__ == "__main__":
    main()
