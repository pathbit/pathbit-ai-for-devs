# 🚀 Guia de Permissões e Autonomia no Google Antigravity

Este guia explica como funciona o sistema unificado de permissões do ecossistema **Google Antigravity** e como configurar o modo de acesso total irrestrito para máxima produtividade agêntica.

---

## 🏛️ As 3 Camadas do Ecossistema

O Google Antigravity é composto por três componentes interligados que compartilham regras de segurança:

1. **Antigravity IDE:** Baseada no núcleo do VSCode, fornece a interface visual de edição e terminal integrado.
2. **Antigravity CLI (`agy`):** Interface de terminal para interação em modo texto.
3. **Antigravity Agent 2.0:** O motor de inteligência e controle de execução compartilhado entre a IDE e a CLI.

---

## ⚖️ Precedência Rigorosa de Permissões

O motor Agent 2.0 avalia as regras de execução seguindo uma ordem de precedência inegociável:

```text
DENY (Bloqueio)  >  ASK (Confirmação)  >  ALLOW (Aprovação Automática)
```

- Se houver qualquer regra de **DENY** correspondente, a operação é rejeitada imediatamente, mesmo que exista uma regra de ALLOW universal.
- Para obter autonomia irrestrita, a lista de `deny` deve permanecer estritamente vazia (`"deny": []`), transferindo o controle total para as diretivas de `allow`.

---

## 🌐 Os 6 Wildcards Universais de Permissão

Para permitir que o agente leia arquivos, salve alterações, execute comandos no terminal e acesse a internet sem abrir popups de confirmação, 6 permissões devem estar ativas no arquivo `config/config.json`:

```json
{
  "allow": [
    "read_file(/)",
    "write_file(/)",
    "command(*)",
    "read_url(*)",
    "execute_url(*)",
    "mcp(*)"
  ],
  "deny": []
}
```

| Permissão | Ação Autorizada |
| :--- | :--- |
| `read_file(/)` | Leitura de qualquer arquivo a partir da raiz do disco |
| `write_file(/)` | Escrita e criação de arquivos sem aprovação de diff |
| `command(*)` | Execução de qualquer comando de shell no terminal |
| `read_url(*)` | Leitura e raspagem de URLs e documentações externas |
| `execute_url(*)` | Disparo de requisições HTTP e chamadas de API externas |
| `mcp(*)` | Uso irrestrito de ferramentas fornecidas por servidores MCP |

---

## ⚡ Configuração Automatizada com Backup

Para aplicar todas essas diretrizes de forma segura e idempotente nos três sistemas operacionais (macOS, Linux e Windows WSL2), utilize o script oficial:

```bash
cd 0001_antigravity_acesso_total_irrestrito
python3 src/setup_permissions.py
```

O script executa os seguintes passos com segurança:
1. Cria um backup automático da sua configuração atual em `~/.gemini/backup-permissoes-YYYYMMDD_HHMM/`.
2. Configura a política `autoExecutionPolicy: "EAGER"` e `artifactReviewMode: "TURBO"`.
3. Desativa o sandbox do terminal para garantir que comandos acessem ferramentas instaladas no host.
4. Concede os 6 wildcards universais no motor Agent 2.0 e em todos os projetos locais.
5. Define `agentMode: "accept-edits"` e `toolPermission: "always-proceed"` na CLI `agy`.
6. Configura `TRUST_PARENT` na raiz do sistema e no diretório home do usuário em `trustedFolders.json`.

---

## 🔍 Como Auditar e Validar as Permissões

A qualquer momento você pode executar o validador para auditar o status das 5 camadas:

```bash
python3 src/verify_permissions.py
```

Se todas as camadas apresentarem marcas verdes (`✅`), seu ambiente está configurado para operar com autonomia máxima e sem travamentos.

---

## ⏪ Como Reverter um Backup

Caso precise retornar ao estado anterior às alterações:

```bash
# Listar os backups existentes
python3 src/restore_permissions.py --list

# Restaurar o backup mais recente imediatamente
python3 src/restore_permissions.py --latest
```
