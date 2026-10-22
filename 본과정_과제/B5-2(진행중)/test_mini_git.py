"""Mini Git 자동 테스트.   실행:  python -m unittest -v

평가에서 "정말 되는지 보여 달라"고 할 때 한 번에 증명하는 용도다.
테스트 코드도 정렬 내장 함수를 쓰지 않는다(없어도 검증할 수 있다).
"""

import io
import random
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from mini_git.cli import execute, run_repl, tokenize
from mini_git.graph import CommitGraph
from mini_git.index import InvertedIndex
from mini_git.models import Commit, HashGenerator, MiniGitError
from mini_git.repository import Repository
from mini_git.sorting import merge_sort

ROOT = Path(__file__).parent


def fake_clock(step_seconds=60):
    """호출할 때마다 step_seconds씩 흐르는 가짜 시계 (테스트 결과를 고정하기 위해)."""
    state = {"now": datetime(2024, 1, 15, 9, 0, 0) - timedelta(seconds=step_seconds)}

    def tick():
        state["now"] += timedelta(seconds=step_seconds)
        return state["now"]

    return tick


def run(repo, *lines):
    """여러 줄을 차례로 실행하고 마지막 줄의 출력을 돌려준다."""
    output = None
    for line in lines:
        output = execute(repo, line)
    return output


def make_commit(name, parents, when=None):
    return Commit(hash=name, message=f"msg {name}", author="a",
                  timestamp=when or datetime(2024, 1, 1), parents=list(parents))


def random_dag(rng, size, max_parents=3, root_chance=0.15):
    """임의의 DAG. 각 노드의 부모는 '앞에 만든 노드' 중에서만 고른다. 뿌리가 여러 개일 수 있다."""
    graph = CommitGraph()
    names = []
    for i in range(size):
        name = f"n{i:02d}"
        parents = []
        if names and rng.random() > root_chance:
            for candidate in rng.sample(names, min(len(names), rng.randint(1, max_parents))):
                parents.append(candidate)
        graph.add(make_commit(name, parents))
        names.append(name)
    return graph, names


def all_simple_paths(graph, start, end):
    """(검증용) 무방향 그래프에서 start->end 모든 단순 경로를 DFS로 전부 나열한다."""
    results = []

    def walk(current, path):
        if current == end:
            results.append(list(path))
            return
        for neighbor in graph.neighbors(current):
            if neighbor not in path:
                path.append(neighbor)
                walk(neighbor, path)
                path.pop()

    walk(start, [start])
    return results


def expected_shortest(graph, start, end):
    """(검증용) 문제 정의 그대로: 최단 길이 중 'a->b->c' 문자열이 가장 작은 경로."""
    best = None
    for path in all_simple_paths(graph, start, end):
        text = "->".join(path)
        if best is None or len(path) < len(best[1]) or (len(path) == len(best[1]) and text < best[0]):
            best = (text, path)
    return None if best is None else best[1]


def reachable_parents(graph, name):
    """(검증용) 재귀로 구한 모든 조상 집합."""
    seen = set()

    def visit(h):
        for parent in graph.get(h).parents:
            if parent not in seen:
                seen.add(parent)
                visit(parent)

    visit(name)
    return seen


class ScenarioTests(unittest.TestCase):
    """과제 8장 '결과 예시'를 그대로 따라가 본다."""

    def setUp(self):
        self.repo = Repository(clock=fake_clock(15 * 60))
        self.out = lambda *lines: run(self.repo, *lines)

    def build_example(self):
        for line in ['init "Alice"', 'commit "Initial commit"', "branch feature", "switch feature",
                     'commit "Add login feature"', "switch main", 'commit "Add payment feature"']:
            execute(self.repo, line)

    def test_init_branch_switch_commit_messages(self):
        self.assertEqual(execute(self.repo, 'init "Alice"'),
                         ["Initialized repository.", "Current branch: main", "Current user: Alice"])
        self.assertEqual(execute(self.repo, 'commit "Initial commit"'), ["[main c001] Initial commit"])
        self.assertEqual(execute(self.repo, "branch feature"), ["Created branch: feature"])
        self.assertEqual(execute(self.repo, "switch feature"), ["Switched to branch: feature"])
        self.assertEqual(execute(self.repo, 'commit "Add login feature"'), ["[feature c002] Add login feature"])

    def test_log_shows_hash_author_timestamp_message_parents_first(self):
        self.build_example()
        text = "\n".join(execute(self.repo, "log"))
        self.assertIn("commit c001 (Alice, 2024-01-15 09:00:00)", text)
        self.assertIn("commit c002 (Alice, 2024-01-15 09:15:00) [feature]", text)
        self.assertIn("commit c003 (Alice, 2024-01-15 09:30:00) [HEAD -> main]", text)
        self.assertLess(text.index("c001"), text.index("c002"))
        self.assertLess(text.index("c002"), text.index("c003"))
        self.assertIn("Add payment feature", text)

    def test_path_between_branches_goes_through_common_ancestor(self):
        self.build_example()
        self.assertEqual(execute(self.repo, "path c001 c003"), ["Path: c001 -> c003"])
        self.assertEqual(execute(self.repo, "path c002 c003"), ["Path: c002 -> c001 -> c003"])
        self.assertEqual(execute(self.repo, "path c003 c003"), ["Path: c003"])

    def test_ancestors(self):
        self.build_example()
        self.assertEqual(execute(self.repo, "ancestors c003"),
                         ["Ancestors of c003 (1):", "- c001: Initial commit (Alice)"])
        self.assertEqual(execute(self.repo, "ancestors c001"), ["No ancestors"])

    def test_search_keyword_and_author(self):
        self.build_example()
        self.assertEqual(execute(self.repo, 'search "login"'),
                         ["Found 1 commit:", "- c002: Add login feature (Alice)"])
        self.assertEqual(len(execute(self.repo, "search --author=Alice")), 4)  # 헤더 + 3개
        self.assertEqual(execute(self.repo, "search nothing"), ["No commits found"])

    def test_search_is_case_insensitive_and_multiword_is_and(self):
        self.build_example()
        self.assertEqual(execute(self.repo, "search LOGIN")[0], "Found 1 commit:")
        self.assertEqual(execute(self.repo, "search --author=ALICE")[0], "Found 3 commits:")
        self.assertEqual(execute(self.repo, 'search "add login"')[0], "Found 1 commit:")
        self.assertEqual(execute(self.repo, 'search "add nothing"'), ["No commits found"])


class CliRuleTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repository(clock=fake_clock())

    def test_commands_are_case_insensitive(self):
        self.assertEqual(execute(self.repo, 'InIt "Bob"')[0], "Initialized repository.")
        self.assertEqual(execute(self.repo, 'CoMmIt "x y"'), ["[main c001] x y"])
        self.assertEqual(execute(self.repo, "LOG")[0].split()[0], "commit")

    def test_quoted_arguments_keep_spaces(self):
        self.assertEqual(tokenize('COMMIT "Add login feature"'), ["COMMIT", "Add login feature"])
        execute(self.repo, 'init "Alice Kim"')
        self.assertIn("Alice Kim", execute(self.repo, 'commit "a b  c"')[0] + self.repo.author)
        self.assertEqual(self.repo.author, "Alice Kim")

    def test_standard_error_messages(self):
        execute(self.repo, "init a")
        execute(self.repo, "commit one")
        self.assertEqual(execute(self.repo, "switch nope"), ["Unknown branch: nope"])
        self.assertEqual(execute(self.repo, "path c001 zzz"), ["Unknown commit: zzz"])
        self.assertEqual(execute(self.repo, "ancestors zzz"), ["Unknown commit: zzz"])
        for bad in ["init", "init a b", "branch", "switch", "commit", 'commit "unclosed',
                    "commit a b", 'commit ""', "commit '   '", "path c001", "path a b c",
                    "ancestors", "search", "search a b", "search --author=", "search --foo",
                    "log extra", "log --sort-by=name", "log --sort-by", "branch dev extra"]:
            self.assertEqual(execute(self.repo, bad), ["Invalid args"], msg=bad)

    def test_unknown_command_and_blank_line(self):
        self.assertEqual(execute(self.repo, "hello"), ["Unknown command: hello"])
        self.assertEqual(execute(self.repo, "   "), [])

    def test_commands_before_init_are_blocked(self):
        for line in ["branch x", "switch main", "commit m", "log", "path a b", "ancestors a", "search x"]:
            self.assertTrue(execute(self.repo, line)[0].startswith("Repository not initialized"), msg=line)

    def test_user_command_changes_author_but_keeps_repository(self):
        execute(self.repo, "init Alice")
        execute(self.repo, "commit one")
        self.assertEqual(execute(self.repo, 'user "Bob Lee"'), ["Current user: Bob Lee"])
        self.assertEqual(execute(self.repo, "commit two"), ["[main c002] two"])
        self.assertEqual(len(self.repo.graph), 2)  # INIT과 달리 커밋이 사라지지 않는다
        self.assertEqual(execute(self.repo, 'search --author="bob lee"')[0], "Found 1 commit:")
        self.assertEqual(execute(self.repo, "user"), ["Invalid args"])

    def test_duplicate_branch(self):
        execute(self.repo, "init a")
        execute(self.repo, "branch dev")
        self.assertEqual(execute(self.repo, "branch dev"), ["Branch already exists: dev"])

    def test_exit_and_quit_end_the_loop(self):
        for word in ["exit", "QUIT", "Exit"]:
            self.assertIsNone(execute(self.repo, word))

    def test_repl_loop_reads_until_exit(self):
        lines = iter(['init "A"', 'commit "hi"', "log", "exit", 'commit "never runs"'])
        printed = []
        run_repl(Repository(clock=fake_clock()), read=lambda prompt: next(lines), write=printed.append)
        self.assertTrue(any("hi" in row for row in printed))
        self.assertEqual(next(lines), 'commit "never runs"')  # exit 뒤 입력은 소비되지 않았다

    def test_repl_survives_eof(self):
        def eof(prompt):
            raise EOFError
        run_repl(Repository(), read=eof, write=lambda text: None)

    def test_hash_arguments_are_case_insensitive(self):
        execute(self.repo, "init a")
        execute(self.repo, "commit one")
        execute(self.repo, "commit two")
        self.assertEqual(execute(self.repo, "path C001 C002"), ["Path: c001 -> c002"])


class HashAndBranchTests(unittest.TestCase):
    def test_hashes_are_unique_even_across_init(self):
        repo = Repository(clock=fake_clock(0))
        seen = set()
        for _ in range(3):
            execute(repo, "init a")  # INIT을 반복해도
            for i in range(400):
                seen.add(repo.commit(f"m{i}").hash)
        self.assertEqual(len(seen), 1200)

    def test_hash_generator_never_repeats(self):
        gen = HashGenerator()
        values = [gen.next_hash() for _ in range(2500)]
        self.assertEqual(len(set(values)), 2500)

    def test_branch_points_at_same_commit_and_commit_moves_only_current_branch(self):
        repo = Repository(clock=fake_clock())
        repo.init("a")
        repo.commit("one")
        repo.create_branch("dev")
        self.assertEqual(repo.branches["dev"], repo.branches["main"])
        repo.switch("dev")
        repo.commit("two")
        self.assertEqual(repo.branches["main"], "c001")
        self.assertEqual(repo.branches["dev"], "c002")
        self.assertEqual(repo.graph.get("c002").parents, ["c001"])

    def test_first_commit_has_no_parents_and_init_resets(self):
        repo = Repository(clock=fake_clock())
        repo.init("a")
        self.assertEqual(repo.commit("root").parents, [])
        repo.init("b")
        self.assertEqual(len(repo.graph), 0)
        self.assertEqual(repo.commit("again").hash, "c002")  # 번호는 이어서 발급 -> 유일

    def test_no_path_when_two_roots_exist(self):
        """첫 커밋 전에 브랜치를 만들면 뿌리 커밋이 2개가 된다 -> 서로 이어지지 않아 No path."""
        repo = Repository(clock=fake_clock())
        for line in ["init a", "branch other", "commit one", "switch other", "commit two"]:
            execute(repo, line)
        self.assertEqual(repo.graph.get("c002").parents, [])
        self.assertEqual(execute(repo, "path c001 c002"), ["No path"])
        self.assertEqual(execute(repo, "ancestors c002"), ["No ancestors"])


class GraphAlgorithmTests(unittest.TestCase):
    def test_graph_rejects_duplicates_and_unknown_parents(self):
        graph = CommitGraph()
        graph.add(make_commit("a", []))
        with self.assertRaises(ValueError):
            graph.add(make_commit("a", []))
        with self.assertRaises(ValueError):
            graph.add(make_commit("b", ["ghost"]))
        with self.assertRaises(ValueError):
            graph.add(make_commit("c", ["a", "a"]))

    def test_topological_order_puts_every_parent_before_child(self):
        rng = random.Random(7)
        for _ in range(200):
            graph, names = random_dag(rng, rng.randint(1, 25))
            order = graph.topological_order()
            self.assertEqual(len(order), len(names))
            self.assertEqual(len(set(order)), len(names))  # 빠짐/중복 없음
            position = {h: i for i, h in enumerate(order)}
            for h in order:
                for parent in graph.get(h).parents:
                    self.assertLess(position[parent], position[h])

    def test_topological_order_with_merge_commit(self):
        graph = CommitGraph()
        graph.add(make_commit("a", []))
        graph.add(make_commit("b", ["a"]))
        graph.add(make_commit("c", ["a"]))
        graph.add(make_commit("m", ["b", "c"]))  # 부모가 2개인 병합 커밋
        self.assertEqual(graph.topological_order(), ["a", "b", "c", "m"])
        self.assertEqual(graph.ancestors("m"), ["b", "c", "a"])  # a는 한 번만, 가까운 순
        self.assertEqual(graph.shortest_path("b", "c"), ["b", "a", "c"])  # 사전순으로 a 경유가 b->m->c 보다 앞
        self.assertEqual(graph.shortest_path("a", "m"), ["a", "b", "m"])  # 길이 2 경로가 둘 -> b 쪽이 사전순 우선

    def test_ancestors_match_brute_force(self):
        rng = random.Random(11)
        for _ in range(200):
            graph, names = random_dag(rng, rng.randint(1, 25))
            for name in names:
                found = graph.ancestors(name)
                self.assertEqual(len(found), len(set(found)))  # 중복 없음
                self.assertNotIn(name, found)
                self.assertEqual(set(found), reachable_parents(graph, name))  # 빠짐없음

    def test_ancestors_nearest_first(self):
        graph = CommitGraph()
        graph.add(make_commit("a", []))
        graph.add(make_commit("b", ["a"]))
        graph.add(make_commit("c", ["b"]))
        self.assertEqual(graph.ancestors("c"), ["b", "a"])

    def test_shortest_path_matches_brute_force_including_lexicographic_tie_break(self):
        rng = random.Random(23)
        checked_ties = 0
        for _ in range(300):
            graph, names = random_dag(rng, rng.randint(2, 11), max_parents=3)
            for start in names:
                for end in names:
                    expected = expected_shortest(graph, start, end)
                    actual = graph.shortest_path(start, end)
                    self.assertEqual(actual, expected, msg=f"{start}->{end}")
                    if expected is not None:
                        equally_short = [p for p in all_simple_paths(graph, start, end) if len(p) == len(expected)]
                        checked_ties += len(equally_short) > 1
        self.assertGreater(checked_ties, 50)  # 동률 경로 상황이 실제로 충분히 검증됐는지 확인

    def test_path_is_symmetric_in_length(self):
        rng = random.Random(5)
        graph, names = random_dag(rng, 20)
        for start in names:
            for end in names:
                forward, backward = graph.shortest_path(start, end), graph.shortest_path(end, start)
                self.assertEqual(forward is None, backward is None)
                if forward is not None:
                    self.assertEqual(len(forward), len(backward))

    def test_large_linear_history_is_fast_enough(self):
        graph = CommitGraph()
        previous = []
        for i in range(5000):
            graph.add(make_commit(f"c{i}", previous))
            previous = [f"c{i}"]
        self.assertEqual(len(graph.topological_order()), 5000)
        self.assertEqual(len(graph.ancestors("c4999")), 4999)
        self.assertEqual(len(graph.shortest_path("c0", "c4999")), 5000)


class SortingTests(unittest.TestCase):
    def test_sorted_order_permutation_and_original_untouched(self):
        rng = random.Random(3)
        for _ in range(300):
            data = [rng.randint(0, 9) for _ in range(rng.randint(0, 40))]
            original = list(data)
            result = merge_sort(data)
            self.assertEqual(data, original)  # 원본 유지
            for i in range(len(result) - 1):
                self.assertLessEqual(result[i], result[i + 1])
            counts = {}
            for value in data:
                counts[value] = counts.get(value, 0) + 1
            for value in result:
                counts[value] -= 1
            self.assertTrue(all(c == 0 for c in counts.values()))  # 같은 원소들의 재배열

    def test_stable_sort_keeps_original_order_of_ties(self):
        rng = random.Random(9)
        for _ in range(200):
            items = [(rng.randint(0, 4), i) for i in range(rng.randint(0, 50))]  # (키, 원래 순번)
            result = merge_sort(items, key=lambda pair: pair[0])
            for i in range(len(result) - 1):
                (k1, n1), (k2, n2) = result[i], result[i + 1]
                self.assertLessEqual(k1, k2)
                if k1 == k2:
                    self.assertLess(n1, n2)  # 동률이면 원래 순서 유지 = 안정 정렬

    def test_edge_cases(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([1]), [1])
        self.assertEqual(merge_sort([3, 2, 1]), [1, 2, 3])
        self.assertEqual(merge_sort(["b", "a"], key=lambda s: s), ["a", "b"])

    def test_log_sort_by_date_and_author(self):
        repo = Repository(clock=fake_clock())
        repo.init("Zed")
        repo.commit("first by zed")
        repo.set_user("alice")
        repo.commit("first by alice")
        repo.set_user("Bob")
        repo.commit("by bob")
        repo.set_user("alice")
        repo.commit("second by alice")
        by_author = [c.author + ":" + c.message for c in repo.log("author")]
        self.assertEqual(by_author, ["alice:first by alice", "alice:second by alice",
                                     "Bob:by bob", "Zed:first by zed"])  # 대소문자 무시, 동률은 원래 순서
        self.assertEqual([c.message for c in repo.log("date")],
                         ["first by zed", "first by alice", "by bob", "second by alice"])
        self.assertEqual([c.message for c in repo.search_author("ALICE")], ["first by alice", "second by alice"])

    def test_log_sort_by_date_tie_keeps_parent_first(self):
        repo = Repository(clock=lambda: datetime(2024, 1, 1))  # 시각이 전부 같다
        repo.init("a")
        for text in ["one", "two", "three"]:
            repo.commit(text)
        self.assertEqual([c.message for c in repo.log("date")], ["one", "two", "three"])


class InvertedIndexTests(unittest.TestCase):
    def test_keyword_extraction_split_and_lower(self):
        index = InvertedIndex()
        index.add(Commit("c001", "Fix LOGIN Bug  login", "Alice", datetime(2024, 1, 1), []))
        index.add(Commit("c002", "login page", "Bob", datetime(2024, 1, 2), ["c001"]))
        self.assertEqual(index.search_keyword("login"), ["c001", "c002"])  # 한 메시지에 두 번 나와도 1회 등록
        self.assertEqual(index.search_keyword("LOGIN"), ["c001", "c002"])
        self.assertEqual(index.search_keyword("fix login"), ["c001"])
        self.assertEqual(index.search_keyword("missing"), [])
        self.assertEqual(index.search_keyword("   "), [])
        self.assertEqual(index.search_author("alice"), ["c001"])
        self.assertEqual(index.search_author("Bob"), ["c002"])
        self.assertEqual(index.search_author("nobody"), [])

    def test_search_uses_index_not_scan(self):
        """검색 중 그래프의 '전체 커밋'을 훑지 않는다: 결과 개수만큼만 커밋을 꺼낸다."""
        repo = Repository(clock=fake_clock(0))
        repo.init("a")
        for i in range(500):
            repo.commit("common word" if i != 250 else "rare needle")
        calls = []
        original_get = repo.graph.get
        repo.graph.get = lambda h: (calls.append(h), original_get(h))[1]
        found = repo.search_keyword("needle")
        self.assertEqual([c.message for c in found], ["rare needle"])
        self.assertEqual(len(calls), 1)  # 500개를 전부 열어 보지 않았다


class ConstraintTests(unittest.TestCase):
    """제출 코드가 금지 규칙을 지키는지 소스를 직접 검사한다."""

    def source_files(self):
        return [ROOT / "main.py"] + list((ROOT / "mini_git").glob("*.py"))

    def test_no_builtin_sorting_api(self):
        for path in self.source_files():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"\bsorted\s*\(", text), msg=f"sorted() in {path.name}")
            self.assertIsNone(re.search(r"\.sort\s*\(", text), msg=f".sort() in {path.name}")
            self.assertIsNone(re.search(r"\bheapq\b|\bbisect\b", text), msg=f"heapq/bisect in {path.name}")

    def test_no_graph_library_or_network(self):
        banned = ("networkx", "igraph", "graphlib", "socket", "requests", "urllib", "http.client")
        for path in self.source_files():
            text = path.read_text(encoding="utf-8")
            for name in banned:
                self.assertNotRegex(text, rf"^\s*(import|from)\s+{re.escape(name)}\b", msg=f"{name} in {path.name}")

    def test_docstrings_exist_for_public_classes_and_functions(self):
        import ast
        for path in self.source_files()[1:]:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                    self.assertIsNotNone(ast.get_docstring(node), msg=f"{path.name}:{node.name}")


class EndToEndTests(unittest.TestCase):
    def test_python_main_runs_with_piped_stdin(self):
        import os
        import subprocess
        import sys
        script = 'init "Alice"\ncommit "Initial commit"\nlog\nexit\n'
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
        done = subprocess.run([sys.executable, str(ROOT / "main.py")], input=script, text=True,
                              capture_output=True, encoding="utf-8", env=env, timeout=20, cwd=str(ROOT))
        self.assertEqual(done.returncode, 0)
        self.assertIn("[main c001] Initial commit", done.stdout)
        self.assertIn("commit c001 (Alice,", done.stdout)


if __name__ == "__main__":
    unittest.main()
