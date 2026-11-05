
#!/usr/bin/env python3

import sys
from memsim import MemoryManager

ops = [
    ("alloc", "P1", 200),
    ("alloc", "P2", 300),
    ("alloc", "P3", 150),
    ("alloc", "P4", 250),
    ("free", "P2"),
    ("free", "P4"),
    ("alloc", "P5", 120),
    ("alloc", "P6", 280),
    ("free", "P1"),
    ("alloc", "P7", 400),
    ("free", "P3"),
    ("alloc", "P8", 350)
]

strategy = sys.argv[1] if len(sys.argv) > 1 else "first"

mm = MemoryManager(strategy=strategy, coalesce=False)

print("Стратегия:", strategy.upper())
print("Начальный размер памяти: 1024")
print("--------------------------------")

for i, operation in enumerate(ops, 1):

    command = operation[0]
    pid = operation[1]

    if command == "alloc":

        size = operation[2]
        success = mm.alloc(pid, size)

        result = "" if success else " - ОТКАЗ"

        print(i, command, pid, size, mm.show(), result)

    else:

        mm.free_mem(pid)

        print(i, command, pid, mm.show())

print("--------------------------------")

total_free, largest_free, internal = mm.stats()

print("Количество отказов:", mm.refused)
print("Всего свободной памяти:", total_free)
print("Наибольший свободный блок:", largest_free)
print("Внешняя фрагментация:", total_free - largest_free)
print("Внутренняя фрагментация:", internal)
print(
    f"свободно={total_free} "
    f"макс. дыра={largest_free} "
    f"дыр={sum(1 for b in mm.blocks if b.free)} "
    f"отказов={mm.refused}"
)
