#!/usr/bin/env python3
import os
from memsim import MemoryManager
from buddy import Buddy

# Функция чтения файла операций (ops1.txt или ops2.txt)
def load_ops(filename):
    ops = []
    if not os.path.exists(filename):
        # Если файла нет, создаем тестовый ops1 прямо на лету
        return [
            ("alloc", "P1", 200), ("alloc", "P2", 300), ("alloc", "P3", 150),
            ("alloc", "P4", 250), ("free", "P2"), ("free", "P4"),
            ("alloc", "P5", 120), ("alloc", "P6", 280), ("free", "P1"),
            ("alloc", "P7", 400), ("free", "P3"), ("alloc", "P8", 350)
        ]
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            if parts[0] == "alloc":
                ops.append((parts[0], parts[1], int(parts[2])))
            elif parts[0] == "free":
                ops.append((parts[0], parts[1]))
    return ops

def simulate(make, alloc, free, stats):
    ops = load_ops("ops2.txt")  # Прогон на ops2.txt согласно слайду 9.8
    m = make()
    ext, internal = [], []
    for cmd, pid, *rest in ops:
        if cmd == "alloc":
            alloc(m, pid, rest[0])
        else:
            free(m, pid)
        tot, mx, extra = stats(m)
        ext.append(1 - mx / tot if tot else 0)
        internal.append(extra)
    return m.refused, sum(ext) / len(ext), sum(internal) / len(internal)

# Сборка и вывод результатов в таблицу как на слайде 9.8
print(f"{'Подход':<15} | {'Отказов':<7} | {'Внешняя':<7} | {'Внутр., ср.'}")
print("-" * 50)

# 1. first + merge
res = simulate(lambda: MemoryManager("first", True), lambda m, p, s: m.alloc(p, s), lambda m, p: m.free_mem(p), lambda m: m.stats())
print(f"{'first + merge':<15} | {res[0]:<7} | {res[1]:.2f}  | {res[2]:.0f}")

# 2. best + merge
res = simulate(lambda: MemoryManager("best", True), lambda m, p, s: m.alloc(p, s), lambda m, p: m.free_mem(p), lambda m: m.stats())
print(f"{'best + merge':<15} | {res[0]:<7} | {res[1]:.2f}  | {res[2]:.0f}")

# 3. worst + merge
res = simulate(lambda: MemoryManager("worst", True), lambda m, p, s: m.alloc(p, s), lambda m, p: m.free_mem(p), lambda m: m.stats())
print(f"{'worst + merge':<15} | {res[0]:<7} | {res[1]:.2f}  | {res[2]:.0f}")

# 4. buddy
res = simulate(lambda: Buddy(), lambda m, p, s: m.alloc(p, s), lambda m, p: m.release(p), lambda m: m.stats())
print(f"{'buddy':<15} | {res[0]:<7} | {res[1]:.2f}  | {res[2]:.0f}")
