#!/usr/bin/env python3
"""Check the reproducible artefacts shared by the article series."""

import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from prepare_aggregator_lab import APP, ROOT, prepare


class SeriesLabsTests(unittest.TestCase):
    def test_copy_contains_the_original_app_and_excludes_local_state(self):
        with TemporaryDirectory() as workspace:
            lab = Path(workspace) / "app"
            prepare(lab)
            for original in sorted((APP / "src").rglob("*")):
                if original.is_file():
                    self.assertEqual(original.read_bytes(), (lab / original.relative_to(APP)).read_bytes())
            self.assertTrue((lab / ".pathbit-aggregator-lab").is_file())
            for name in (".env", "data", ".git", "node_modules"):
                self.assertFalse((lab / name).exists(), name)

    def test_copy_leaves_a_nonempty_directory_intact(self):
        with TemporaryDirectory() as workspace:
            lab = Path(workspace)
            sentinel = lab / "notes.md"
            sentinel.write_text("existing work", encoding="utf-8")
            with self.assertRaises(ValueError):
                prepare(lab)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "existing work")

    def test_reference_patches_apply_to_separate_files(self):
        patches = ROOT / "0008_claude_code_worktrees" / "examples"
        with TemporaryDirectory() as workspace:
            lab = Path(workspace) / "app"
            prepare(lab)
            for patch in ("health.patch", "dashboard.patch"):
                subprocess.run(["git", "apply", "--check", str(patches / patch)], cwd=lab, check=True)
                subprocess.run(["git", "apply", str(patches / patch)], cwd=lab, check=True)
            self.assertIn("app.get('/health'", (lab / "src/server.js").read_text(encoding="utf-8"))
            self.assertIn("Meu Agregador de Notícias", (lab / "src/public/index.html").read_text(encoding="utf-8"))

    def test_configuration_keeps_router_secret_out_of_the_file(self):
        config = ROOT / "0009_opencode_9router_ollama" / "examples/opencode.json.example"
        providers = json.loads(config.read_text(encoding="utf-8"))["providers"]
        self.assertEqual(providers["router"]["settings"]["apiKey"], "{env:PATHBIT_ROUTER_KEY}")
        self.assertEqual(set(providers["router"]["models"]), {"pathbit-code"})
        self.assertEqual(set(providers["local"]["models"]), {"qwen2.5-coder:7b"})


if __name__ == "__main__":
    unittest.main()
