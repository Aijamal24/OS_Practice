
from collections import OrderedDict
import matplotlib.pyplot as plt

# =====================================
# НАСТРОЙКИ
# =====================================

PAGE_SIZE = 1024
NUM_PAGES = 16
ADDRESS_SPACE_SIZE = PAGE_SIZE * NUM_PAGES

MEMORY_ACCESS_NS = 100
TLB_ACCESS_NS = 10


# =====================================
# ЗАГРУЗКА ФАЙЛОВ
# =====================================

def load_page_table(filename):
    page_table = {}

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split()

            if not parts:
                continue

            page = int(parts[0])

            if parts[1] == "отсутствует":
                page_table[page] = None
            else:
                page_table[page] = int(parts[1])

    return page_table


def load_references(filename):
    with open(filename, "r", encoding="utf-8") as file:
        refs = [int(line.strip()) for line in file if line.strip()]

    for address in refs:
        if not 0 <= address < ADDRESS_SPACE_SIZE:
            raise ValueError(f"Недопустимый адрес: {address}")

    return refs


# =====================================
# ТРАНСЛЯЦИЯ БЕЗ TLB
# =====================================

def translate_address(address, page_table):
    page = address // PAGE_SIZE
    offset = address % PAGE_SIZE

    frame = page_table.get(page)

    if frame is None:
        return None

    physical = frame * PAGE_SIZE + offset

    return {
        "logical": address,
        "page": page,
        "offset": offset,
        "frame": frame,
        "physical": physical
    }


# =====================================
# TLB С ПОЛИТИКОЙ LRU
# =====================================

class TLB:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

        self.hits = 0
        self.misses = 0
        self.valid_misses = 0
        self.page_faults = 0

    def lookup(self, page):
        if page in self.cache:
            frame = self.cache.pop(page)
            self.cache[page] = frame
            self.hits += 1
            return frame

        self.misses += 1
        return None

    def insert(self, page, frame):
        if page in self.cache:
            self.cache.pop(page)

        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)

        self.cache[page] = frame

    @property
    def hit_rate(self):
        total = self.hits + self.valid_misses
        return self.hits / total if total else 0


# =====================================
# ТРАНСЛЯЦИЯ С TLB
# =====================================

def translate_with_tlb(address, page_table, tlb):
    page = address // PAGE_SIZE
    offset = address % PAGE_SIZE

    frame = tlb.lookup(page)

    if frame is not None:
        return {
            "page": page,
            "offset": offset,
            "frame": frame,
            "physical": frame * PAGE_SIZE + offset,
            "status": "HIT"
        }

    frame = page_table.get(page)

    if frame is None:
        tlb.page_faults += 1

        return {
            "page": page,
            "offset": offset,
            "frame": None,
            "physical": None,
            "status": "PAGE FAULT"
        }

    tlb.valid_misses += 1
    tlb.insert(page, frame)

    return {
        "page": page,
        "offset": offset,
        "frame": frame,
        "physical": frame * PAGE_SIZE + offset,
        "status": "MISS"
    }


# =====================================
# ЭФФЕКТИВНОЕ ВРЕМЯ ДОСТУПА
# =====================================

def calculate_eat(hit_rate):
    hit_time = TLB_ACCESS_NS + MEMORY_ACCESS_NS
    miss_time = TLB_ACCESS_NS + 2 * MEMORY_ACCESS_NS

    return hit_rate * hit_time + (1 - hit_rate) * miss_time


# =====================================
# ДВУХУРОВНЕВАЯ ТАБЛИЦА
# =====================================

def two_level_indices(page):
    return page // 4, page % 4


# =====================================
# ГЛАВНАЯ ПРОГРАММА
# =====================================

def main():
    print("=" * 60)
    print("ПРАКТИЧЕСКАЯ РАБОТА №10")
    print("СТРАНИЧНАЯ ОРГАНИЗАЦИЯ")
    print("=" * 60)

    page_table = load_page_table("data/pagetable.txt")
    refs = load_references("data/refs.txt")

    print("\nРазмер страницы:", PAGE_SIZE, "байт")
    print("Адресное пространство:", ADDRESS_SPACE_SIZE, "байт")
    print("Количество страниц:", NUM_PAGES)
    print("Количество обращений:", len(refs))

    # ---------------------------------
    # ТАБЛИЦА СТРАНИЦ
    # ---------------------------------

    print("\nТАБЛИЦА СТРАНИЦ")

    for page in range(NUM_PAGES):
        frame = page_table.get(page)
        print(f"Страница {page}: {frame if frame is not None else 'отсутствует'}")

    # ---------------------------------
    # КОНТРОЛЬНЫЕ АДРЕСА
    # ---------------------------------

    print("\nКОНТРОЛЬНЫЕ АДРЕСА")

    for address in [0, 1023, 1024, 2500, 4096, 6144]:
        result = translate_address(address, page_table)

        if result is None:
            page = address // PAGE_SIZE
            offset = address % PAGE_SIZE
            print(f"LA={address}: PAGE FAULT, page={page}, offset={offset}")
        else:
            print(
                f"LA={address}, page={result['page']}, "
                f"offset={result['offset']}, frame={result['frame']}, "
                f"PA={result['physical']}"
            )

    # ---------------------------------
    # TLB
    # ---------------------------------

    print("\nТРАНСЛЯЦИЯ С TLB")

    tlb = TLB(4)

    for address in refs:
        result = translate_with_tlb(address, page_table, tlb)

        print(
            f"LA={address:5} | "
            f"page={result['page']:2} | "
            f"offset={result['offset']:4} | "
            f"{result['status']:10} | "
            f"PA={result['physical']}"
        )

    # ---------------------------------
    # СТАТИСТИКА
    # ---------------------------------

    print("\nСТАТИСТИКА TLB")
    print("Размер TLB:", tlb.capacity)
    print("Hits:", tlb.hits)
    print("Misses:", tlb.misses)
    print("Page faults:", tlb.page_faults)
    print(f"Hit rate: {tlb.hit_rate:.2%}")

    # ---------------------------------
    # EAT
    # ---------------------------------

    print("\nЭФФЕКТИВНОЕ ВРЕМЯ ДОСТУПА")

    print("Время памяти:", MEMORY_ACCESS_NS, "нс")
    print("Время TLB:", TLB_ACCESS_NS, "нс")

    for rate in [0, 0.25, 0.5, 0.75, 0.9, 1]:
        print(f"Hit rate {rate:.0%}: EAT = {calculate_eat(rate):.2f} нс")

    print(f"\nИзмеренный EAT: {calculate_eat(tlb.hit_rate):.2f} нс")

    # ---------------------------------
    # ГРАФИК ДЛЯ ДЛИННОЙ ПОСЛЕДОВАТЕЛЬНОСТИ
    # ---------------------------------

    print("\nГРАФИК: РАЗМЕР TLB -> HIT RATE")

    # Страницы с локальностью обращений.
    # Страница 0 используется чаще остальных.
    local_pages = [0, 1, 0, 3, 0, 4, 0, 5,
                   0, 7, 0, 8, 0, 9, 0, 10]

    local_refs = []

    for _ in range(100):
        for page in local_pages:
            local_refs.append(page * PAGE_SIZE + 100)

    tlb_sizes = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16]
    hit_rates = []

    for size in tlb_sizes:
        test_tlb = TLB(size)

        for address in local_refs:
            translate_with_tlb(address, page_table, test_tlb)

        hit_rates.append(test_tlb.hit_rate)

        print(f"TLB={size:2}: hit rate={test_tlb.hit_rate:.2%}")

    plt.figure(figsize=(9, 5))
    plt.plot(tlb_sizes, [x * 100 for x in hit_rates], marker="o")

    plt.xlabel("Размер TLB (записей)")
    plt.ylabel("Доля попаданий (%)")
    plt.title("Зависимость hit rate от размера TLB")
    plt.grid(True)

    plt.savefig("tlb_hit_rate.png", dpi=150, bbox_inches="tight")
    plt.show()

    # ---------------------------------
    # ДВУХУРОВНЕВАЯ ТАБЛИЦА
    # ---------------------------------

    print("\nДВУХУРОВНЕВАЯ ТАБЛИЦА")

    for page in range(NUM_PAGES):
        l1, l2 = two_level_indices(page)
        print(f"Page {page:2} -> L1={l1}, L2={l2}")

    print("\nБез TLB:")
    print("L1 -> L2 -> данные")
    print("Всего обращений к памяти: 3")

    print("\nПри TLB HIT:")
    print("TLB -> данные")
    print("Обращений к памяти: 1 (не считая поиск в TLB)")

    # ---------------------------------
    # ИТОГ
    # ---------------------------------

    print("\n" + "=" * 60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)

    print("TLB hits:", tlb.hits)
    print("TLB misses:", tlb.misses)
    print("Page faults:", tlb.page_faults)
    print(f"Hit rate: {tlb.hit_rate:.2%}")
    print(f"EAT: {calculate_eat(tlb.hit_rate):.2f} нс")
    print("Двухуровневая таблица без TLB: 3 обращения")
    print("График сохранён: tlb_hit_rate.png")


if __name__ == "__main__":
    main()
