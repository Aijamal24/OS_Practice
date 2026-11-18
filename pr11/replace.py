from collections import deque

CONTROL = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3,
           0, 3, 2, 1, 2, 0, 1, 7, 0, 1]


def fifo(refs, n_frames):
    frames = []
    queue = deque()
    faults = 0

    for page in refs:
        if page in frames:
            continue
        faults += 1

        if len(frames) < n_frames:
            frames.append(page)
        else:
            victim = queue.popleft()
            frames[frames.index(victim)] = page

        queue.append(page)

    return faults


def lru(refs, n_frames):
    frames = []
    last_used = {}
    faults = 0

    for t, page in enumerate(refs):
        if page not in frames:
            faults += 1

            if len(frames) < n_frames:
                frames.append(page)
            else:
                victim = min(frames, key=lambda p: last_used[p])
                frames.remove(victim)
                frames.append(page)

        last_used[page] = t

    return faults


def optimal(refs, n_frames):
    frames = []
    faults = 0

    for i, page in enumerate(refs):
        if page in frames:
            continue

        faults += 1

        if len(frames) < n_frames:
            frames.append(page)
            continue

        future = refs[i + 1:]

        def next_use(p):
            return future.index(p) if p in future else float('inf')

        victim = max(frames, key=next_use)
        frames.remove(victim)
        frames.append(page)

    return faults


if __name__ == "__main__":
    for n in (3, 4):
        print(f"{n} кадра: FIFO={fifo(CONTROL, n)}  "
              f"LRU={lru(CONTROL, n)}  "
              f"Optimal={optimal(CONTROL, n)}")
