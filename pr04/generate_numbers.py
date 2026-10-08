#!/usr/bin/env python3

N = 10_000_000

with open("numbers.txt", "w") as file:
    for i in range(1, N + 1):
        file.write(f"{i}\n")

print(f"Generated {N} numbers.")
