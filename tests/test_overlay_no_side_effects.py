from __future__ import annotations

import ast
import inspect
import unittest

import observatory_overlay_proof.align as align_module
import observatory_overlay_proof.fixtures as fixtures_module
from observatory_overlay_proof import build_overlay_alignment_response, build_overlay_request


class OverlayNoSideEffectsTests(unittest.TestCase):
    def test_package_has_no_forbidden_imports(self) -> None:
        forbidden = {"os", "pathlib", "subprocess", "socket", "sqlite3", "psycopg", "requests", "httpx", "logging"}
        for module in (align_module, fixtures_module):
            tree = ast.parse(inspect.getsource(module))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            self.assertFalse(imported & forbidden)

    def test_no_mutable_cache_or_registry(self) -> None:
        project_globals = {
            name: value
            for name, value in vars(align_module).items()
            if not name.startswith("__")
        }
        suspicious_mutable_globals = {
            name
            for name, value in project_globals.items()
            if ("cache" in name.lower() or "registry" in name.lower())
            and isinstance(value, (dict, list, set, bytearray))
        }
        self.assertEqual(suspicious_mutable_globals, set())

    def test_response_build_has_no_external_side_effect_contract(self) -> None:
        response = build_overlay_alignment_response(build_overlay_request("owned_aligned"))
        self.assertFalse(response["overlay_persisted"])
        self.assertFalse(response["overlay_cached"])
        self.assertFalse(response["overlay_logged"])
        self.assertFalse(response["overlay_evidence_promoted"])


if __name__ == "__main__":
    unittest.main()
