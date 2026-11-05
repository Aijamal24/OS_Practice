#!/usr/bin/env python3

MEMORY = 1024

class Buddy:
    def __init__(self, log=False):
        self.free = {MEMORY: [0]}  # размер -> адреса свободных блоков
        self.owned = {}            # pid -> (адрес, блок, запрошено)
        self.refused = 0
        self.log = log

    def alloc(self, pid, size):
        need = 1
        while need < size:
            need *= 2
        s = need
        while s <= MEMORY and not self.free.get(s):
            s *= 2
        if s > MEMORY:
            self.refused += 1
            return False
        addr = self.free[s].pop(0)
        while s > need:
            s //= 2
            self.free.setdefault(s, []).append(addr + s)
            if self.log:
                print(f" делим -> {s}+{s}")
        self.owned[pid] = (addr, need, size)
        return True

    def release(self, pid):
        if pid not in self.owned:  # alloc был отклонен
            return
        addr, s, _ = self.owned.pop(pid)
        while s < MEMORY:
            buddy = addr ^ s
            if buddy in self.free.get(s, []):
                self.free[s].remove(buddy)
                addr = min(addr, buddy)
                s *= 2
                if self.log:
                    print(f" слияние -> {s}")
            else:
                break
        self.free.setdefault(s, []).append(addr)
        self.free[s].sort()

    def stats(self):
        holes = [s for s, lst in self.free.items() for _ in lst]
        internal = sum(b - r for _, b, r in self.owned.values())
        return sum(holes), max(holes, default=0), internal

    def show(self):
        """Вспомогательный метод вывода карты занятости памяти для логов"""
        status = ["-"] * MEMORY
        for pid, (addr, need, _) in self.owned.items():
            for i in range(addr, addr + need):
                status[i] = pid
        parts = []
        curr_pid = status[0]
        curr_start = 0
        for i in range(1, MEMORY):
            if status[i] != curr_pid:
                parts.append(f"[{curr_pid if curr_pid != '-' else ''}:{i - curr_start}]")
                curr_pid = status[i]
                curr_start = i
        parts.append(f"[{curr_pid if curr_pid != '-' else ''}:{MEMORY - curr_start}]")
        return " ".join(parts).replace("[:", "[-:")
