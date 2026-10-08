#!/usr/bin/env python3

import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


URL_FILE = "urls.txt"
WORKERS = 4


def load_urls():
    with open(URL_FILE, "r") as file:
        return [line.strip() for line in file if line.strip()]


def download(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read()


def sequential(urls):
    return [download(url) for url in urls]


def threads(urls):
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        return list(executor.map(download, urls))


def processes(urls):
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        return list(executor.map(download, urls))


def measure(name, function, urls):
    times = []

    for run in range(1, 4):
        start = time.perf_counter()

        results = function(urls)

        elapsed = time.perf_counter() - start

        total_bytes = sum(len(data) for data in results)

        times.append(elapsed)

        print(
            f"{name}: run {run}: "
            f"{elapsed:.6f} s, "
            f"bytes={total_bytes}"
        )

    med = sorted(times)[1]

    print(
        f"{name}: median={med:.6f} s"
    )

    print()

    return med


def main():
    urls = load_urls()

    print(f"URLs loaded: {len(urls)}")
    print()

    measure(
        "Sequential",
        sequential,
        urls,
    )

    measure(
        "4 threads",
        threads,
        urls,
    )

    measure(
        "4 processes",
        processes,
        urls,
    )


if __name__ == "__main__":
    main()
