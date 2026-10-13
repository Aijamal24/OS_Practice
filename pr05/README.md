# Practical Work 5 — CPU Scheduling Simulator

## 1. Objective

Implement and compare CPU scheduling algorithms using Python.

## 2. Implemented algorithms

- **FCFS** — processes execute in arrival order.
- **SJF** — the available process with the shortest burst executes first.
- **SRTF** — the process with the shortest remaining time executes; preemption is allowed.
- **Priority** — the ready process with the highest priority executes; smaller numeric values mean higher priority.
- **Round Robin (RR)** — each process receives a time quantum in cyclic order.

The simulator returns execution intervals in the form `(start, end, pid)`.

## 3. Metrics

- **Waiting time:** turnaround time minus burst time.
- **Turnaround time:** completion time minus arrival time.
- **Response time:** first start time minus arrival time.
- **CPU utilization:** busy CPU time divided by total elapsed time, multiplied by 100%.
- **Switches:** number of transitions between execution intervals in the displayed schedule.

## 4. Input format

Each line contains:

`PID arrival_time burst_time priority`

Example:

```text
P1 0 8 2
P2 1 4 1
P3 2 9 3
P4 3 5 2
```

## 5. How to run

```bash
python3 sched.py --algo fcfs set1.txt
python3 sched.py --algo sjf set1.txt
python3 sched.py --algo srtf set1.txt
python3 sched.py --algo priority set1.txt
python3 sched.py --algo priority --aging set3.txt
python3 sched.py --algo rr --quantum 3 set1.txt
```

## 6. Validation on set1

Expected results verified for the supplied input:

| Algorithm | Average waiting | Average turnaround |
|---|---:|---:|
| SRTF | 6.50 | 13.00 |
| RR, quantum = 3 | 13.50 | 20.00 |
| FCFS, calculated from set1.txt | 8.75 | 15.25 |

The assignment lists FCFS values of 9.25 and 15.75. For the process data in this repository, standard FCFS scheduling produces 8.75 and 15.25. The discrepancy may be due to different reference input data.

## 7. Round Robin experiment

The script `plot_rr.py` runs Round Robin for quantum values from 1 to 10 using `set2.txt`.

Run:

```bash
python3 plot_rr.py
```

The script prints the average waiting time and the number of execution intervals for each quantum, and saves the plot as `rr_plot.png`.

The experiment shows that larger quanta generally reduce scheduling overhead and the number of execution intervals. Average waiting time does not have to change monotonically because it depends on the workload and the scheduling order.

## 8. Priority aging

Aging gradually improves the effective priority of waiting processes. This helps prevent indefinite postponement when higher-priority processes continue to arrive.

Run with aging:

```bash
python3 sched.py --algo priority --aging set3.txt
```

Compare with the same command without `--aging`.

## 9. Control questions

### 1. Why can't SJF be directly applied in a real operating system?

SJF requires knowing or accurately predicting the next CPU burst length before scheduling. A real operating system generally cannot know this value in advance. It can only estimate it from previous behavior. Also, long jobs may wait for a very long time when short jobs keep arriving.

### 2. What happens when the Round Robin quantum tends to infinity?

Round Robin approaches FCFS behavior: a process can run until it finishes before the next ready process gets the CPU. Responsiveness decreases, and the fairness benefit of short time slices is lost.

## 10. Conclusion

The simulator implements several CPU scheduling policies and calculates waiting, turnaround, response, and CPU utilization metrics. The Round Robin experiment illustrates the trade-off between time quantum size and scheduling overhead. Priority aging is intended to reduce starvation of low-priority processes.
