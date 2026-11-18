
import matplotlib.pyplot as plt

pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3,
         0, 3, 2, 1, 2, 0, 1, 7, 0, 1]

def fifo(seq, n):
    frames = []
    faults = 0
    for p in seq:
        if p not in frames:
            faults += 1
            if len(frames) == n:
                frames.pop(0)
            frames.append(p)
    return faults

def lru(seq, n):
    frames = []
    faults = 0
    for p in seq:
        if p in frames:
            frames.remove(p)
        else:
            faults += 1
            if len(frames) == n:
                frames.pop(0)
        frames.append(p)
    return faults

def optimal(seq, n):
    frames = []
    faults = 0
    for i, p in enumerate(seq):
        if p not in frames:
            faults += 1
            if len(frames) < n:
                frames.append(p)
            else:
                future = []
                for page in frames:
                    try:
                        future.append(seq.index(page, i + 1))
                    except ValueError:
                        future.append(float('inf'))
                frames[future.index(max(future))] = p
    return faults

def clock(seq, n):
    frames = [None] * n
    bits = [0] * n
    hand = 0
    faults = 0

    for p in seq:
        if p in frames:
            bits[frames.index(p)] = 1
        else:
            faults += 1
            while frames[hand] is not None and bits[hand] == 1:
                bits[hand] = 0
                hand = (hand + 1) % n

            frames[hand] = p
            bits[hand] = 1
            hand = (hand + 1) % n

    return faults

algorithms = {
    "FIFO": fifo,
    "LRU": lru,
    "Optimal": optimal,
    "Clock": clock
}

frame_counts = range(1, 9)

for name, algorithm in algorithms.items():
    results = [algorithm(pages, n) for n in frame_counts]
    plt.plot(list(frame_counts), results, marker='o', label=name)

plt.title("Page Replacement Algorithms")
plt.xlabel("Number of frames")
plt.ylabel("Number of page faults")
plt.xticks(list(frame_counts))
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("page_faults.png", dpi=300)
print("Graph saved: page_faults.png")

print("\nBelady anomaly (FIFO):")
belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
print("3 frames:", fifo(belady, 3))
print("4 frames:", fifo(belady, 4))
