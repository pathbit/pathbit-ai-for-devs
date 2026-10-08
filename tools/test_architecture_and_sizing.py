#!/usr/bin/env python3
"""Suite de testes unitarios de arquitetura, dimensionamento e combos do pathbit-ai-for-devs.

Valida regras deterministicas sem dependencia de containers ou redes externas:
1. Calculos de dimensionamento de licencas e capacidade em 0002 (sizing.py).
2. Integridade dos combos de fallback e modelos em 0003 (setup_combos.py).
3. Verificacao estatica dos templates DeepClaude em 0004 (verify_deepclaude.py).
"""

import importlib.util
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, rel_path: str):
    full_path = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestArchitectureAndSizing(unittest.TestCase):
    def test_sizing_br_formatting(self):
        sizing = load_module("sizing_mod", "0002_claude_gravity_utilizando_9router/src/sizing.py")
        self.assertEqual(sizing.br(1234.56, decimals=2), "1.234,56")
        self.assertEqual(sizing.br(1000000, decimals=0), "1.000.000")
        self.assertEqual(sizing.br(0.5, decimals=1), "0,5")

    def test_sizing_constants_and_profiles(self):
        sizing = load_module("sizing_mod", "0002_claude_gravity_utilizando_9router/src/sizing.py")
        self.assertIn("mediana", sizing.PROFILES)
        self.assertIn("p90", sizing.PROFILES)

        for profile_name in ["mediana", "p90"]:
            p = sizing.PROFILES[profile_name]
            self.assertGreater(p["rate_per_hour"], 0)
            self.assertGreater(p["billable_input"], 0)
            self.assertGreater(p["output"], 0)
            self.assertGreater(p["total_input"], p["billable_input"])

        for tier in ["Start", "Build", "Scale"]:
            self.assertIn(tier, sizing.API_TIERS)
            t = sizing.API_TIERS[tier]
            self.assertGreater(t["rpm"], 0)
            self.assertGreater(t["itpm"], 0)
            self.assertGreater(t["otpm"], 0)

        self.assertEqual(sizing.WINDOW_HOURS, 5)
        self.assertEqual(sizing.ANTIGRAVITY_WINDOW_HOURS, 2)

    def test_combos_structure_and_ordering(self):
        combos_mod = load_module("combos_mod", "0003_fallback_modelos_gratuitos_9router/src/setup_combos.py")
        combos = combos_mod.COMBOS
        self.assertIsInstance(combos, list)
        self.assertGreaterEqual(len(combos), 3)

        combo_names = {c["name"] for c in combos}
        self.assertIn("claudegravity-fallback", combo_names)
        self.assertIn("arsenal-supremo", combo_names)
        self.assertIn("arsenal-rapido", combo_names)

        for c in combos:
            self.assertIn("id", c)
            self.assertIn("name", c)
            self.assertIn("kind", c)
            self.assertIn("models", c)
            self.assertIsInstance(c["models"], list)
            self.assertGreater(len(c["models"]), 0)
            for m in c["models"]:
                self.assertIsInstance(m, str)
                self.assertTrue(len(m.strip()) > 0)
                self.assertTrue("/" in m or ":" in m)

    def test_deepclaude_verify_templates(self):
        verify_mod = load_module("deepclaude_mod", "0004_deepclaude_alternativa_ao_claudegravity/src/verify_deepclaude.py")
        deepseek_example = ROOT / "0004_deepclaude_alternativa_ao_claudegravity/examples/.claude/settings.local.json.deepseek.example"
        orcarouter_example = ROOT / "0004_deepclaude_alternativa_ao_claudegravity/examples/.claude/settings.local.json.orcarouter.example"

        self.assertTrue(deepseek_example.exists())
        self.assertTrue(orcarouter_example.exists())

        cfg_ds = verify_mod.carregar(deepseek_example)
        self.assertIsNotNone(cfg_ds)
        verify_mod.falhas.clear()
        verify_mod.validar(deepseek_example, cfg_ds, exige_token_real=False)
        self.assertEqual(len(verify_mod.falhas), 0, f"Erros no deepseek: {verify_mod.falhas}")

        cfg_orca = verify_mod.carregar(orcarouter_example)
        self.assertIsNotNone(cfg_orca)
        verify_mod.falhas.clear()
        verify_mod.validar(orcarouter_example, cfg_orca, exige_token_real=False)
        self.assertEqual(len(verify_mod.falhas), 0, f"Erros no orcarouter: {verify_mod.falhas}")


if __name__ == "__main__":
    unittest.main()
