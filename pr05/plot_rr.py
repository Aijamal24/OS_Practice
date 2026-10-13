#!/usr/bin/env python3

import matplotlib.pyplot as plt

from sched import load_processes, simulate, calculate_metrics


def main():
    processes = load_processes("set2.txt")

    quanta = list(range(1, 11))
    waiting_times = []
    switches = []

    for quantum in quanta:
        intervals = simulate(
            processes,
            "rr",
            quantum=quantum,
        )

        metrics = calculate_metrics(processes, intervals)
        waiting_times.append(metrics["avg_waiting"])
        switches.append(metrics["switches"])

        print(
            f"Quantum={quantum:2d}: "
            f"avg_waiting={metrics['avg_waiting']:.2f}, "
            f"switches={metrics['switches']}"
        )

    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.plot(
        quanta,
        waiting_times,
        marker="o",
        label="Average waiting time",
    )
    ax1.set_xlabel("RR quantum")
    ax1.set_ylabel("Average waiting time")
    ax1.set_xticks(quanta)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(
        quanta,
        switches,
        marker="s",
        linestyle="--",
        label="Context-switch intervals",
    )
    ax2.set_ylabel("Context-switch intervals")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

    plt.title("Round Robin: quantum vs waiting time and switches")
    fig.tight_layout()
    fig.savefig("rr_plot.png", dpi=150)
    print("\nГрафик сохранён в rr_plot.png")


if __name__ == "__main__":
    main()
