#!/usr/bin/env python3
"""
test_permissions.py
Suíte de testes do configurador de permissões do Google Antigravity.

Roda inteiramente sobre um diretório temporário apontado por HOME: nenhuma
configuração real do usuário é lida, gravada ou apagada.

Execução:
    python3 src/test_permissions.py
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import setup_permissions as sp


class TempHomeTestCase(unittest.TestCase):
    """Base que isola cada teste em um HOME descartável."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._original_home = os.environ.get("HOME")
        os.environ["HOME"] = self._tmp.name
        # O git ignora HOME: sem estas duas, apply_git_hooks escreveria no gitconfig real.
        os.environ["GIT_CONFIG_GLOBAL"] = os.path.join(self._tmp.name, ".gitconfig")
        os.environ["XDG_CONFIG_HOME"] = os.path.join(self._tmp.name, ".config")
        self.home = self._tmp.name
        self.paths = sp.get_system_paths()
        # Os utilitários são conversacionais por natureza; o relatório de
        # testes fica ilegível se cada etapa imprimir seu progresso.
        self._silenciador = contextlib.redirect_stdout(io.StringIO())
        self._silenciador.__enter__()

    def tearDown(self):
        self._silenciador.__exit__(None, None, None)
        if self._original_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self._original_home
        self._tmp.cleanup()

    def read(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


class TestMergeAllowList(unittest.TestCase):
    """Regras de composição da lista allow."""

    def test_insere_os_seis_wildcards_em_lista_vazia(self):
        result = sp.merge_allow_list([])
        self.assertEqual(sorted(result), sorted(sp.WILDCARDS))

    def test_preserva_entrada_de_escopo_nao_coberto(self):
        result = sp.merge_allow_list(["custom_tool(x)"])
        self.assertIn("custom_tool(x)", result)

    def test_poda_entradas_cobertas_por_wildcard(self):
        existing = [
            "command(curl -H 'Authorization: Bearer segredo' http://localhost)",
            "command(git status)",
            "read_file(/etc/hosts)",
            "write_file(/tmp/a.txt)",
            "mcp(postgres)",
        ]
        result = sp.merge_allow_list(existing)
        for entry in existing:
            self.assertNotIn(entry, result)
        self.assertEqual(sorted(result), sorted(sp.WILDCARDS))

    def test_idempotente(self):
        primeira = sp.merge_allow_list(["command(ls)", "outro(1)"])
        segunda = sp.merge_allow_list(primeira)
        self.assertEqual(primeira, segunda)

    def test_nao_duplica_wildcard_ja_presente(self):
        result = sp.merge_allow_list(["command(*)"])
        self.assertEqual(result.count("command(*)"), 1)


class TestLoadJson(TempHomeTestCase):
    """Leitura tolerante sem corromper conteúdo válido."""

    def test_recupera_virgula_sobrando(self):
        path = os.path.join(self.home, "trailing.json")
        self.write(path, '{"a": 1, "b": 2,}')
        self.assertEqual(sp.load_json(path), {"a": 1, "b": 2})

    def test_preserva_virgula_dentro_de_string(self):
        path = os.path.join(self.home, "valido.json")
        self.write(path, '{"cmd": "echo a,}"}')
        self.assertEqual(sp.load_json(path), {"cmd": "echo a,}"})

    def test_arquivo_inexistente_vira_dicionario_vazio(self):
        self.assertEqual(sp.load_json(os.path.join(self.home, "nao-existe.json")), {})

    def test_arquivo_vazio_vira_dicionario_vazio(self):
        path = os.path.join(self.home, "vazio.json")
        self.write(path, "   ")
        self.assertEqual(sp.load_json(path), {})


class TestSaveJson(TempHomeTestCase):
    """Gravação com releitura de verificação."""

    def test_grava_e_revalida(self):
        path = os.path.join(self.home, "sub", "dir", "out.json")
        sp.save_json(path, {"x": 1})
        self.assertEqual(self.read(path), {"x": 1})

    def test_dry_run_nao_cria_arquivo(self):
        path = os.path.join(self.home, "nao-deve-existir.json")
        sp.save_json(path, {"x": 1}, dry_run=True)
        self.assertFalse(os.path.exists(path))


class TestAplicacaoCompleta(TempHomeTestCase):
    """Comportamento das etapas de configuração sobre um HOME limpo."""

    def aplicar(self, dry_run=False):
        sp.apply_agent_engine(self.paths, dry_run=dry_run)
        sp.apply_projects(self.paths, dry_run=dry_run)
        sp.apply_cli_and_trust(self.paths, dry_run=dry_run)
        sp.apply_ide_settings(self.paths, dry_run=dry_run)

    def test_dry_run_nao_escreve_nada(self):
        self.aplicar(dry_run=True)
        self.assertFalse(os.path.exists(self.paths["config_json"]))
        self.assertFalse(os.path.exists(self.paths["cli_settings"]))
        self.assertFalse(os.path.exists(self.paths["trusted_folders"]))

    def test_aplicacao_grava_politicas_e_wildcards(self):
        self.aplicar()
        us = self.read(self.paths["config_json"])["userSettings"]
        self.assertEqual(us["autoExecutionPolicy"], "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER")
        self.assertEqual(us["artifactReviewMode"], "ARTIFACT_REVIEW_MODE_TURBO")
        self.assertEqual(us["browserJsExecutionPolicy"], "BROWSER_JS_EXECUTION_POLICY_TURBO")
        self.assertEqual(us["nonWorkspaceFileAccessPolicy"], "AGENT_SETTING_POLICY_ALLOW")
        self.assertFalse(us["enableTerminalSandbox"])
        self.assertEqual(sorted(us["globalPermissionGrants"]["allow"]), sorted(sp.WILDCARDS))
        self.assertEqual(us["globalPermissionGrants"]["deny"], [])

    def test_idempotencia_duas_execucoes(self):
        self.aplicar()
        primeira = self.read(self.paths["config_json"])
        self.aplicar()
        self.assertEqual(primeira, self.read(self.paths["config_json"]))

    def test_preserva_chaves_alheias_do_usuario(self):
        self.write(
            self.paths["config_json"],
            json.dumps({"userSettings": {"tema": "escuro"}, "outraSecao": {"a": 1}}),
        )
        self.aplicar()
        d = self.read(self.paths["config_json"])
        self.assertEqual(d["userSettings"]["tema"], "escuro")
        self.assertEqual(d["outraSecao"], {"a": 1})

    def test_projetos_recebem_wildcards_e_workspace_liberado(self):
        projeto = os.path.join(self.paths["projects_dir"], "demo.json")
        self.write(projeto, json.dumps({"settings": {"tema": "claro"}}))
        self.aplicar()
        d = self.read(projeto)
        self.assertFalse(d["isWorkspaceOnly"])
        self.assertEqual(d["settings"]["tema"], "claro")
        self.assertEqual(d["settings"]["fileAccessPolicy"], "AGENT_SETTING_POLICY_ALLOW")
        pg = d["permissionGrants"]["permissionGrants"]
        self.assertEqual(sorted(pg["allow"]), sorted(sp.WILDCARDS))

    def test_raiz_confiavel_do_sistema(self):
        self.aplicar()
        trust = self.read(self.paths["trusted_folders"])
        self.assertEqual(trust[sp.get_root_key(self.paths)], "TRUST_PARENT")
        self.assertEqual(trust[self.home], "TRUST_PARENT")

    def test_backup_copia_config_existente(self):
        self.aplicar()
        backup_dir = sp.create_backup(self.paths)
        self.assertTrue(os.path.exists(os.path.join(backup_dir, "config.json")))

    def test_git_hook_instalado_com_permissao_execucao(self):
        sp.apply_git_hooks(self.paths)
        hook_path = os.path.join(self.home, ".git-hooks", "commit-msg")
        self.assertTrue(os.path.exists(hook_path))
        self.assertTrue(os.access(hook_path, os.X_OK))
        with open(hook_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Co-Authored-By", content)
        self.assertIn("Claude-Session", content)

    def test_git_hook_dry_run_nao_cria_arquivo(self):
        sp.apply_git_hooks(self.paths, dry_run=True)
        hook_path = os.path.join(self.home, ".git-hooks", "commit-msg")
        self.assertFalse(os.path.exists(hook_path))


class PlataformaSimuladaTestCase(unittest.TestCase):
    """Base para verificar a resolução de caminhos das três plataformas.

    O sistema operacional é simulado, não exigido: assim a promessa de suporte
    a macOS, Linux e Windows fica verificável rodando em qualquer máquina.
    """

    sistema = None

    def resolver(self, home, **variaveis):
        """Devolve o dicionário de caminhos como se o script rodasse em `sistema`."""
        ambiente = {k: v for k, v in variaveis.items() if v is not None}
        removidas = [k for k, v in variaveis.items() if v is None]
        with mock.patch.object(sp.platform, "system", return_value=self.sistema), \
             mock.patch.object(sp.os.path, "expanduser", return_value=home), \
             mock.patch.dict(os.environ, ambiente, clear=False):
            for chave in removidas:
                os.environ.pop(chave, None)
            return sp.get_system_paths()

    def caminhos_ide(self, paths):
        return [
            os.path.join(paths["appdata"], variante, "User", "settings.json")
            for variante in paths["ide_variants"]
        ]

    def todos_os_destinos(self, paths):
        return [
            paths["config_json"],
            paths["projects_dir"],
            paths["cli_settings"],
            paths["trusted_folders"],
        ] + self.caminhos_ide(paths)

    def assertNenhumDestinoContem(self, paths, fragmentos):
        for destino in self.todos_os_destinos(paths):
            for fragmento in fragmentos:
                self.assertNotIn(
                    fragmento, destino,
                    f"caminho de outra plataforma vazou em {self.sistema}: {destino}",
                )


class TestPlataformaMacos(PlataformaSimuladaTestCase):
    sistema = "Darwin"

    def test_ide_em_application_support(self):
        paths = self.resolver("/Users/teste")
        esperado = os.path.join("/Users/teste", "Library", "Application Support")
        self.assertEqual(paths["appdata"], esperado)
        ide, ide_variante = self.caminhos_ide(paths)
        self.assertEqual(ide, os.path.join(esperado, "Antigravity", "User", "settings.json"))
        self.assertEqual(ide_variante, os.path.join(esperado, "Antigravity IDE", "User", "settings.json"))

    def test_motor_e_raiz_confiavel(self):
        paths = self.resolver("/Users/teste")
        self.assertEqual(
            paths["config_json"],
            os.path.join("/Users/teste", ".gemini", "config", "config.json"),
        )
        self.assertEqual(sp.get_root_key(paths), "/")

    def test_nao_usa_caminho_de_outra_plataforma(self):
        paths = self.resolver("/Users/teste")
        self.assertNenhumDestinoContem(paths, ["AppData", ".config"])


class TestPlataformaLinux(PlataformaSimuladaTestCase):
    sistema = "Linux"

    def test_ide_em_config_por_padrao(self):
        paths = self.resolver("/home/teste", XDG_CONFIG_HOME=None)
        esperado = os.path.join("/home/teste", ".config")
        self.assertEqual(paths["appdata"], esperado)
        ide, ide_variante = self.caminhos_ide(paths)
        self.assertEqual(ide, os.path.join(esperado, "Antigravity", "User", "settings.json"))
        self.assertEqual(ide_variante, os.path.join(esperado, "Antigravity IDE", "User", "settings.json"))

    def test_respeita_xdg_config_home(self):
        paths = self.resolver("/home/teste", XDG_CONFIG_HOME="/home/teste/.custom-config")
        self.assertEqual(paths["appdata"], "/home/teste/.custom-config")

    def test_motor_e_raiz_confiavel(self):
        paths = self.resolver("/home/teste", XDG_CONFIG_HOME=None)
        self.assertEqual(
            paths["config_json"],
            os.path.join("/home/teste", ".gemini", "config", "config.json"),
        )
        self.assertEqual(sp.get_root_key(paths), "/")

    def test_nao_usa_caminho_de_outra_plataforma(self):
        paths = self.resolver("/home/teste", XDG_CONFIG_HOME=None)
        self.assertNenhumDestinoContem(paths, ["Library/Application Support", "AppData"])


class TestPlataformaWindows(PlataformaSimuladaTestCase):
    sistema = "Windows"

    def test_ide_em_appdata_roaming(self):
        appdata = "C:\\Users\\teste\\AppData\\Roaming"
        paths = self.resolver("C:\\Users\\teste", APPDATA=appdata, USERPROFILE="C:\\Users\\teste")
        self.assertEqual(paths["appdata"], appdata)
        ide, ide_variante = self.caminhos_ide(paths)
        self.assertTrue(ide.startswith(appdata), ide)
        self.assertIn("Antigravity", ide)
        self.assertIn("Antigravity IDE", ide_variante)

    def test_appdata_ausente_cai_no_padrao_roaming(self):
        paths = self.resolver("C:\\Users\\teste", APPDATA=None, USERPROFILE="C:\\Users\\teste")
        self.assertEqual(
            paths["appdata"],
            os.path.join("C:\\Users\\teste", "AppData", "Roaming"),
        )

    def test_motor_no_perfil_do_usuario(self):
        paths = self.resolver("C:\\Users\\teste", APPDATA="C:\\Users\\teste\\AppData\\Roaming")
        self.assertEqual(
            paths["config_json"],
            os.path.join("C:\\Users\\teste", ".gemini", "config", "config.json"),
        )

    def test_raiz_confiavel_deriva_do_drive_do_perfil(self):
        # Perfil em D: não pode marcar C: como confiável.
        paths = self.resolver("D:\\Perfis\\teste", APPDATA="D:\\Perfis\\teste\\AppData\\Roaming")
        self.assertEqual(sp.get_root_key(paths), "D:\\")

    def test_raiz_confiavel_no_drive_padrao(self):
        paths = self.resolver("C:\\Users\\teste", APPDATA="C:\\Users\\teste\\AppData\\Roaming")
        self.assertEqual(sp.get_root_key(paths), "C:\\")

    def test_perfil_em_rede_confia_no_share_unc(self):
        # Perfil hospedado em share de rede: a raiz do perfil é o próprio share,
        # e não C:, que nem contém os arquivos do usuário.
        paths = self.resolver("\\\\servidor\\perfis\\teste", APPDATA="\\\\servidor\\perfis\\teste\\AppData")
        self.assertEqual(sp.get_root_key(paths), "\\\\servidor\\perfis\\")

    def test_perfil_sem_drive_cai_no_padrao(self):
        # Sem drive nem share identificável, resta o padrão do Windows.
        paths = self.resolver("perfil-relativo", APPDATA="perfil-relativo\\AppData")
        self.assertEqual(sp.get_root_key(paths), "C:\\")

    def test_nao_usa_caminho_de_outra_plataforma(self):
        paths = self.resolver("C:\\Users\\teste", APPDATA="C:\\Users\\teste\\AppData\\Roaming")
        self.assertNenhumDestinoContem(paths, ["Library/Application Support", "/.config"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
