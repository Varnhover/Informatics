
import math
import random
import unittest
from collections import deque

from union_find import DisjointSet, connected_components


class TestBasics(unittest.TestCase):
    def test_make_set_and_find(self):
        ds = DisjointSet()
        self.assertTrue(ds.make_set(1))
        self.assertFalse(ds.make_set(1))          # повторное создание игнорируется
        self.assertEqual(ds.find(1), 1)           # одиночка - сам себе представитель
        self.assertEqual(ds.component_count, 1)

    def test_unknown_element(self):
        with self.assertRaises(KeyError):
            DisjointSet().find("нет такого")

    def test_union_and_connected(self):
        ds = DisjointSet(range(6))
        self.assertFalse(ds.is_connected(0, 1))
        self.assertTrue(ds.union(0, 1))
        self.assertTrue(ds.union(1, 2))
        self.assertTrue(ds.is_connected(0, 2))    # транзитивность
        self.assertFalse(ds.is_connected(0, 3))
        self.assertFalse(ds.union(0, 2))          # уже вместе -> слияния нет
        self.assertEqual(ds.component_count, 4)   # {0,1,2},{3},{4},{5}

    def test_component_size(self):
        ds = DisjointSet(range(7))
        for a, b in [(0, 1), (2, 3), (1, 3), (5, 6)]:
            ds.union(a, b)
        self.assertEqual(ds.get_component_size(0), 4)   # {0,1,2,3}
        self.assertEqual(ds.get_component_size(3), 4)
        self.assertEqual(ds.get_component_size(4), 1)
        self.assertEqual(ds.get_component_size(6), 2)

    def test_any_hashable_elements(self):
        ds = DisjointSet(["a", ("x", 1), 3.5])
        ds.union("a", ("x", 1))
        self.assertTrue(ds.is_connected(("x", 1), "a"))
        self.assertFalse(ds.is_connected(3.5, "a"))


class TestOptimizations(unittest.TestCase):
    def test_path_compression(self):
        # Вручную строим цепочку 0 <- 1 <- 2 <- ... <- 9 (нарушая инварианты
        # ранга специально: нужно проверить именно сжатие).
        ds = DisjointSet(range(10))
        for i in range(1, 10):
            ds._parent[i] = i - 1
        self.assertEqual(ds.find(9), 0)
        # После одного find все вершины пути смотрят прямо на корень.
        self.assertTrue(all(ds._parent[i] == 0 for i in range(10)))

    def test_union_by_rank_keeps_trees_low(self):
        # Слияние парами 2^k одиночек даёт дерево ранга ровно k.
        k = 8
        ds = DisjointSet(range(2 ** k))
        step = 1
        while step < 2 ** k:
            for i in range(0, 2 ** k, 2 * step):
                ds.union(i, i + step)
            step *= 2
        root = ds.find(0)
        self.assertEqual(ds._rank[root], k)
        self.assertEqual(ds.get_component_size(0), 2 ** k)

    def test_rank_bound_random(self):
        # Для любых слияний ранг корня <= log2(размер множества).
        rnd = random.Random(1)
        n = 2000
        ds = DisjointSet(range(n))
        for _ in range(3000):
            ds.union(rnd.randrange(n), rnd.randrange(n))
        for root, members in ds.components().items():
            self.assertLessEqual(ds._rank[root], math.log2(len(members)) + 1e-9)

    def test_long_chain_no_recursion_error(self):
        n = 300_000                       # намного больше лимита рекурсии
        ds = DisjointSet(range(n))
        for i in range(1, n):
            ds._parent[i] = i - 1
        self.assertEqual(ds.find(n - 1), 0)


def bfs_components(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen, result = [False] * n, []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        comp, queue = [], deque([s])
        while queue:
            u = queue.popleft()
            comp.append(u)
            for w in adj[u]:
                if not seen[w]:
                    seen[w] = True
                    queue.append(w)
        result.append(sorted(comp))
    return sorted(result)


class TestConnectedComponents(unittest.TestCase):
    def test_small_graph(self):
        edges = [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7), (7, 5)]
        self.assertEqual(connected_components(9, edges),
                         [[0, 1, 2], [3, 4], [5, 6, 7], [8]])

    def test_no_edges_and_empty(self):
        self.assertEqual(connected_components(3, []), [[0], [1], [2]])
        self.assertEqual(connected_components(0, []), [])

    def test_self_loops_and_duplicates(self):
        self.assertEqual(connected_components(3, [(0, 0), (1, 2), (2, 1), (1, 2)]),
                         [[0], [1, 2]])

    def test_random_graphs_against_bfs(self):
        rnd = random.Random(7)
        for _ in range(300):
            n = rnd.randint(1, 40)
            m = rnd.randint(0, 2 * n)
            edges = [(rnd.randrange(n), rnd.randrange(n)) for _ in range(m)]
            self.assertEqual(connected_components(n, edges), bfs_components(n, edges))

    def test_online_queries_against_bfs(self):
        # Рёбра добавляются по одному; после каждого сверяем is_connected и размер.
        rnd = random.Random(11)
        n = 60
        ds, edges = DisjointSet(range(n)), []
        for _ in range(120):
            u, v = rnd.randrange(n), rnd.randrange(n)
            ds.union(u, v)
            edges.append((u, v))
            comps = bfs_components(n, edges)
            where = {x: c for c in comps for x in c}
            a, b = rnd.randrange(n), rnd.randrange(n)
            self.assertEqual(ds.is_connected(a, b), where[a] is where[b])
            self.assertEqual(ds.get_component_size(a), len(where[a]))
            self.assertEqual(ds.component_count, len(comps))


if __name__ == "__main__":
    unittest.main(verbosity=2)
