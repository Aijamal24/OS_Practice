#!/usr/bin/env python3

import sys


def read_events(filename):
    events = []

    with open(filename, "r", encoding="utf-8") as file:
        for number, line in enumerate(file, 1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) != 3:
                raise ValueError(
                    f"Строка {number}: ожидается EVENT PROCESS RESOURCE"
                )

            action, process, resource = parts
            if action not in ("acquire", "wait", "release"):
                raise ValueError(
                    f"Строка {number}: неизвестное событие {action}"
                )

            events.append((action, process, resource))

    return events


def build_graph(events):
    # Ресурс -> процесс, который им владеет
    owners = {}

    # Процесс -> ресурс, которого он ожидает
    waiting = {}

    for action, process, resource in events:
        if action == "acquire":
            if resource not in owners:
                owners[resource] = process
            elif owners[resource] != process:
                waiting[process] = resource

        elif action == "wait":
            waiting[process] = resource

        elif action == "release":
            if owners.get(resource) == process:
                del owners[resource]

    # Граф ожидания: ожидающий процесс -> владелец ресурса
    graph = {}

    for process, resource in waiting.items():
        owner = owners.get(resource)
        if owner is not None and owner != process:
            graph.setdefault(process, set()).add(owner)
            graph.setdefault(owner, set())

    return graph


def find_cycle(graph):
    visited = set()
    active = set()
    path = []

    def dfs(process):
        visited.add(process)
        active.add(process)
        path.append(process)

        for neighbor in graph.get(process, set()):
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
            elif neighbor in active:
                start = path.index(neighbor)
                return path[start:] + [neighbor]

        path.pop()
        active.remove(process)
        return None

    for process in graph:
        if process not in visited:
            cycle = dfs(process)
            if cycle:
                return cycle

    return None


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "events.txt"

    try:
        events = read_events(filename)
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}")
        return

    graph = build_graph(events)
    cycle = find_cycle(graph)

    if cycle:
        print("Обнаружен deadlock!")
        print("Цикл ожидания:", " -> ".join(cycle))
        print("Участники:", ", ".join(sorted(set(cycle[:-1]))))
    else:
        print("Цикл не обнаружен.")
        print("Deadlock не найден в текущем графе ожидания.")


if __name__ == "__main__":
    main()
