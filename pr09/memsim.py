#!/usr/bin/env python3

MEMORY = 1024

class Block:
    def __init__(self, start, size, pid=None):
        self.start = start
        self.size = size
        self.pid = pid

    @property
    def free(self):
        return self.pid is None


class MemoryManager:
    def __init__(self, strategy="first", coalesce=False):
        self.blocks = [Block(0, MEMORY)]
        self.strategy = strategy
        self.coalesce = coalesce
        self.refused = 0

    def candidates(self, size):
        return [b for b in self.blocks if b.free and b.size >= size]

    def choose(self, size):
        valid = self.candidates(size)
        if not valid:
            return None
        if self.strategy == "first":
            return valid[0]
        elif self.strategy == "best":
            return min(valid, key=lambda b: b.size)
        elif self.strategy == "worst":
            return max(valid, key=lambda b: b.size)
        return None

    def alloc(self, pid, size):
        hole = self.choose(size)
        if hole is None:
            self.refused += 1
            return False
        i = self.blocks.index(hole)
        self.blocks[i] = Block(hole.start, size, pid)
        if hole.size > size:
            rest = Block(hole.start + size, hole.size - size)
            self.blocks.insert(i + 1, rest)
        return True

    def free_mem(self, pid):
        for b in self.blocks:
            if b.pid == pid:
                b.pid = None
        if self.coalesce:
            self.merge()

    def merge(self):
        merged = [self.blocks[0]]
        for b in self.blocks[1:]:
            last = merged[-1]
            if last.free and b.free:
                last.size += b.size
            else:
                merged.append(b)
        self.blocks = merged

    def stats(self):
        holes = [b.size for b in self.blocks if b.free]
        return sum(holes), max(holes, default=0), 0

    def show(self):
        parts = [f"[{b.pid or '-'}:{b.size}]" for b in self.blocks]
        return " ".join(parts)
