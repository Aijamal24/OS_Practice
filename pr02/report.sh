#!/bin/bash

usage() {
    echo "Usage: $0 <каталог> <ERROR|WARN> [--top N]" >&2
}

if [ "$#" -lt 2 ]; then
    usage
    exit 1
fi

DIR="$1"
LEVEL="$2"
TOP=""

if [ ! -d "$DIR" ]; then
    echo "Ошибка: каталог '$DIR' не существует." >&2
    usage
    exit 1
fi

if [ "$LEVEL" != "ERROR" ] && [ "$LEVEL" != "WARN" ]; then
    echo "Ошибка: уровень должен быть ERROR или WARN." >&2
    usage
    exit 1
fi

if [ "$#" -gt 2 ]; then
    if [ "$3" != "--top" ] || [ "$#" -ne 4 ]; then
        usage
        exit 1
    fi

    if ! [[ "$4" =~ ^[0-9]+$ ]]; then
        echo "Ошибка: N должно быть числом." >&2
        usage
        exit 1
    fi

    TOP="$4"
fi

echo "module | count"
echo "--------------"

result=$(
    grep -h -E "^[^ ]+ $LEVEL " "$DIR"/*.log 2>/dev/null |
    awk -v level="$LEVEL" '$2 == level {count[$1]++} END {
        for (module in count)
            print module, count[module]
    }' |
    sort -k2,2nr -k1,1
)

if [ -n "$TOP" ]; then
    echo "$result" | head -n "$TOP"
else
    echo "$result"
fi

