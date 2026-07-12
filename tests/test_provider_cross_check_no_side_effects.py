import ast
import copy
import unittest
from pathlib import Path

from observatory_provider_cross_check import build_cross_check_request, build_provider_cross_check
from observatory_provider_cross_check.fixtures import SIDES, SCOPE_A


class ProviderCrossCheckNoSideEffectTests(unittest.TestCase):
    def test_comparison_does_not_mutate_fixtures(self):
        before = copy.deepcopy(SIDES)
        request = build_cross_check_request(request_id="req_no_side_effect", scope_id=SCOPE_A, side_ids=["rank_a", "rank_b"])
        build_provider_cross_check(request, SIDES)
        self.assertEqual(before, SIDES)

    def test_package_has_no_forbidden_imports_or_calls(self):
        package = Path(__file__).parents[1] / "src" / "observatory_provider_cross_check"
        forbidden_imports = {"requests", "httpx", "urllib", "socket", "subprocess", "psycopg", "psycopg2", "sqlalchemy"}
        forbidden_calls = {"open", "exec", "eval", "compile", "system", "popen"}
        for path in package.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = {
                node.names[0].name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom)) and getattr(node, "names", None)
            }
            self.assertFalse(imports & forbidden_imports, path.name)
            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            self.assertFalse(calls & forbidden_calls, path.name)


if __name__ == "__main__":
    unittest.main()
