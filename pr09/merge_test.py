
from memsim import MemoryManager

ops = []

with open("ops2.txt", "r") as file:
    for line in file:
        parts = line.split()

        if not parts:
            continue

        if parts[0] == "alloc":
            ops.append(("alloc", parts[1], int(parts[2])))
        else:
            ops.append(("free", parts[1]))

for merge in [False, True]:

    mm = MemoryManager("first", coalesce=merge)
    fragmentation = []

    for operation in ops:

        if operation[0] == "alloc":
            mm.alloc(operation[1], operation[2])
        else:
            mm.free_mem(operation[1])

        total, largest, internal = mm.stats()

        if total > 0:
            fragmentation.append(1 - largest / total)
        else:
            fragmentation.append(0)

    average = sum(fragmentation) / len(fragmentation)

    print("Слияние:", merge)
    print("Отказы:", mm.refused)
    print("Средняя внешняя фрагментация:", round(average, 2))
    print()
