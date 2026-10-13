#!/usr/bin/env python3

import argparse
from collections import deque


def load_processes(filename):
    processes = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            pid, arrival, burst, priority = line.split()

            processes.append({
                "pid": pid,
                "arrival": int(arrival),
                "burst": int(burst),
                "priority": int(priority),
            })

    return processes


def simulate(processes, algorithm, **params):
    """Возвращает интервалы выполнения в формате (start, end, pid)."""
    if not processes:
        return []

    jobs = [p.copy() for p in processes]

    for p in jobs:
        if p["arrival"] < 0 or p["burst"] <= 0:
            raise ValueError("arrival должен быть >= 0, burst должен быть > 0")

    algorithm = algorithm.lower()

    if algorithm == "fcfs":
        return simulate_fcfs(jobs)

    if algorithm == "sjf":
        return simulate_sjf(jobs)

    if algorithm == "srtf":
        return simulate_srtf(jobs)

    if algorithm in ("priority", "prio"):
        return simulate_priority(jobs, aging=params.get("aging", False))

    if algorithm == "rr":
        quantum = int(params.get("quantum", 3))
        if quantum <= 0:
            raise ValueError("Квант RR должен быть положительным")
        return simulate_rr(jobs, quantum)

    raise ValueError(f"Неизвестный алгоритм: {algorithm}")


def simulate_fcfs(jobs):
    jobs.sort(key=lambda p: (p["arrival"], p["pid"]))
    time = 0
    intervals = []

    for p in jobs:
        start = max(time, p["arrival"])
        end = start + p["burst"]
        intervals.append((start, end, p["pid"]))
        time = end

    return intervals


def simulate_sjf(jobs):
    remaining = {p["pid"]: p["burst"] for p in jobs}
    by_pid = {p["pid"]: p for p in jobs}
    done = set()
    intervals = []
    time = 0

    while len(done) < len(jobs):
        ready = [
            p for p in jobs
            if p["pid"] not in done and p["arrival"] <= time
        ]

        if not ready:
            time = min(
                p["arrival"] for p in jobs
                if p["pid"] not in done
            )
            continue

        p = min(ready, key=lambda x: (x["burst"], x["arrival"], x["pid"]))
        start = time
        end = time + remaining[p["pid"]]
        intervals.append((start, end, p["pid"]))
        time = end
        done.add(p["pid"])

    return intervals


def simulate_srtf(jobs):
    remaining = {p["pid"]: p["burst"] for p in jobs}
    intervals = []
    time = 0
    completed = set()
    current_pid = None
    segment_start = None

    while len(completed) < len(jobs):
        ready = [
            p for p in jobs
            if p["arrival"] <= time
            and p["pid"] not in completed
            and remaining[p["pid"]] > 0
        ]

        if not ready:
            if current_pid is not None:
                intervals.append((segment_start, time, current_pid))
                current_pid = None
                segment_start = None
            time += 1
            continue

        p = min(
            ready,
            key=lambda x: (remaining[x["pid"]], x["arrival"], x["pid"]),
        )

        if current_pid != p["pid"]:
            if current_pid is not None:
                intervals.append((segment_start, time, current_pid))
            current_pid = p["pid"]
            segment_start = time

        remaining[current_pid] -= 1
        time += 1

        if remaining[current_pid] == 0:
            intervals.append((segment_start, time, current_pid))
            completed.add(current_pid)
            current_pid = None
            segment_start = None

    return merge_intervals(intervals)


def simulate_priority(jobs, aging=False):
    remaining = {p["pid"]: p["burst"] for p in jobs}
    first_start = {}
    intervals = []
    time = 0
    completed = set()
    current_pid = None
    segment_start = None
    waiting_since = {p["pid"]: p["arrival"] for p in jobs}

    while len(completed) < len(jobs):
        ready = [
            p for p in jobs
            if p["arrival"] <= time
            and p["pid"] not in completed
            and remaining[p["pid"]] > 0
        ]

        if not ready:
            if current_pid is not None:
                intervals.append((segment_start, time, current_pid))
                current_pid = None
                segment_start = None
            time += 1
            continue

        def priority_key(p):
            effective = p["priority"]
            if aging:
                waited = max(0, time - waiting_since[p["pid"]])
                effective = max(0, effective - waited // 5)
            return (effective, p["arrival"], p["pid"])

        p = min(ready, key=priority_key)

        if current_pid != p["pid"]:
            if current_pid is not None:
                intervals.append((segment_start, time, current_pid))
                waiting_since[current_pid] = time
            current_pid = p["pid"]
            segment_start = time
            first_start.setdefault(current_pid, time)

        remaining[current_pid] -= 1
        time += 1

        if remaining[current_pid] == 0:
            intervals.append((segment_start, time, current_pid))
            completed.add(current_pid)
            current_pid = None
            segment_start = None

    return merge_intervals(intervals)


def simulate_rr(jobs, quantum):
    jobs = sorted(jobs, key=lambda p: (p["arrival"], p["pid"]))
    remaining = {p["pid"]: p["burst"] for p in jobs}
    by_pid = {p["pid"]: p for p in jobs}
    ready = deque()
    intervals = []
    time = 0
    index = 0

    while index < len(jobs) or ready:
        if not ready:
            time = max(time, jobs[index]["arrival"])
            while index < len(jobs) and jobs[index]["arrival"] <= time:
                ready.append(jobs[index]["pid"])
                index += 1

        pid = ready.popleft()
        start = time
        run_for = min(quantum, remaining[pid])
        end = start + run_for

        # Сначала добавляем процессы, прибывшие до или в момент конца кванта.
        while index < len(jobs) and jobs[index]["arrival"] <= end:
            ready.append(jobs[index]["pid"])
            index += 1

        remaining[pid] -= run_for
        time = end
        intervals.append((start, end, pid))

        if remaining[pid] > 0:
            ready.append(pid)

    return merge_intervals(intervals)


def merge_intervals(intervals):
    merged = []

    for start, end, pid in sorted(intervals, key=lambda x: (x[0], x[1])):
        if merged and merged[-1][1] == start and merged[-1][2] == pid:
            old_start, _, old_pid = merged[-1]
            merged[-1] = (old_start, end, old_pid)
        else:
            merged.append((start, end, pid))

    return merged


def calculate_metrics(processes, intervals):
    if not processes:
        return {
            "avg_waiting": 0.0,
            "avg_turnaround": 0.0,
            "avg_response": 0.0,
            "cpu_utilization": 0.0,
            "switches": 0,
        }

    first_start = {}
    completion = {}

    for start, end, pid in intervals:
        first_start.setdefault(pid, start)
        completion[pid] = end

    waiting = []
    turnaround = []
    response = []

    for p in processes:
        pid = p["pid"]
        turn = completion[pid] - p["arrival"]
        turnaround.append(turn)
        waiting.append(turn - p["burst"])
        response.append(first_start[pid] - p["arrival"])

    total_burst = sum(p["burst"] for p in processes)
    start_time = min(p["arrival"] for p in processes)
    end_time = max(completion.values())
    span = end_time - start_time
    busy_time = sum(end - start for start, end, _ in intervals)

    switches = max(0, len(intervals) - 1)

    return {
        "avg_waiting": sum(waiting) / len(waiting),
        "avg_turnaround": sum(turnaround) / len(turnaround),
        "avg_response": sum(response) / len(response),
        "cpu_utilization": 100 * busy_time / span if span else 0.0,
        "switches": switches,
    }


def print_gantt(intervals):
    print("Интервалы выполнения:")
    for start, end, pid in intervals:
        print(f"{start:>4}–{end:<4} {pid}")


def main():
    parser = argparse.ArgumentParser(description="CPU Scheduling Simulator")
    parser.add_argument("--algo", required=True,
                        choices=["fcfs", "sjf", "srtf", "priority", "rr"])
    parser.add_argument("--quantum", type=int, default=3)
    parser.add_argument("--aging", action="store_true",
                        help="Включить старение для priority")
    parser.add_argument("file")
    args = parser.parse_args()

    processes = load_processes(args.file)
    intervals = simulate(
        processes,
        args.algo,
        quantum=args.quantum,
        aging=args.aging,
    )
    metrics = calculate_metrics(processes, intervals)

    print(f"Алгоритм: {args.algo}")
    if args.algo == "rr":
        print(f"Квант: {args.quantum}")
    if args.algo == "priority":
        print(f"Старение: {'включено' if args.aging else 'выключено'}")

    print_gantt(intervals)
    print()
    print("Среднее ожидание:       {:.2f}".format(metrics["avg_waiting"]))
    print("Средний оборот:         {:.2f}".format(metrics["avg_turnaround"]))
    print("Средний отклик:         {:.2f}".format(metrics["avg_response"]))
    print("Загрузка CPU:           {:.2f}%".format(metrics["cpu_utilization"]))
    print("Переключения интервалов:", metrics["switches"])


if __name__ == "__main__":
    main()
