
from collections import defaultdict


class DisjointSet:

    def __init__(self, elements=()):
        self._parent = {}
        self._rank = {}
        self._size = {}

        self._count = 0
        self.hops = 0
        for x in elements:
            self.make_set(x)

    # ------------------------------------------------------------------ make_set
    def make_set(self, x):

        if x in self._parent:
            return False
        self._parent[x] = x      # сам себе родитель => корень
        self._rank[x] = 0        # дерево из одной вершины имеет высоту 0
        self._size[x] = 1
        self._count += 1
        return True

    # ---------------------------------------------------------------------- find
    def find(self, x):

        if x not in self._parent:
            raise KeyError(f"элемент {x!r} не добавлен (сначала make_set)")

        # Проход 1: поднимаемся по ссылкам до корня.
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
            self.hops += 1

        # Проход 2: сжатие пути. Каждую вершину на пути x -> root делаем
        # непосредственным ребёнком корня.
        while x != root:
            nxt = self._parent[x]    # запоминаем старого родителя
            self._parent[x] = root   # перевешиваем прямо на корень
            x = nxt
        return root

    # --------------------------------------------------------------------- union
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx


        self._parent[ry] = rx
        self._size[rx] += self._size[ry]

        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1

        self._count -= 1
        return True

    # ---------------------------------------------------------------- запросы
    def is_connected(self, x, y):

        return self.find(x) == self.find(y)

    def get_component_size(self, x):

        return self._size[self.find(x)]

    @property
    def component_count(self):

        return self._count

    def components(self):

        groups = defaultdict(list)
        for x in self._parent:
            groups[self.find(x)].append(x)
        return dict(groups)

    def __len__(self):
        return len(self._parent)

    def __contains__(self, x):
        return x in self._parent


# ----------------------------------------------------- компоненты связности графа
def connected_components(n, edges):

    ds = DisjointSet(range(n))
    for u, v in edges:
        ds.union(u, v)
    return sorted(sorted(c) for c in ds.components().values())


# ------------------------------------------------- эксперимент по сложности
def experiment_complexity():
    import random
    import time

    print(f"{'n':>9} {'операций':>10} {'шагов/find':>11} {'мкс/операцию':>13}")
    for n in (10**3, 10**4, 10**5, 10**6):
        rnd = random.Random(42)
        ds = DisjointSet(range(n))
        pairs = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(2 * n)]
        t0 = time.perf_counter()
        for a, b in pairs:
            ds.union(a, b)
        for a, b in pairs:
            ds.is_connected(a, b)
        dt = time.perf_counter() - t0
        # union делает 2 find, is_connected тоже 2 find: всего 8n вызовов find
        finds = 2 * (2 * n) + 2 * (2 * n)
        print(f"{n:>9} {4 * n:>10} {ds.hops / finds:>11.3f} {dt / (4 * n) * 1e6:>13.2f}")


if __name__ == "__main__":
    ds = DisjointSet("abcdefg")
    for u, v in [("a", "b"), ("b", "c"), ("d", "e")]:
        ds.union(u, v)
    print("a~c:", ds.is_connected("a", "c"), "| a~d:", ds.is_connected("a", "d"))
    print("размер компоненты a:", ds.get_component_size("a"))
    print("компонент:", ds.component_count, "->", sorted(map(sorted, ds.components().values())))
    print("\nГраф из 8 вершин:", connected_components(8, [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7), (7, 5)]))
    print("\nЭксперимент по сложности:")
    experiment_complexity()
