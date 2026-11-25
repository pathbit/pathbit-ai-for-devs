# Verificar um checkout candidato

Instale as dependências do módulo 0005 no checkout candidato com `npm ci`. A partir da raiz desta cópia do repositório:

```sh
mkdir -p tmp
python3 0006_gate_de_release_de_contratos/src/verificar_release.py \
  --app /caminho/do/candidato/0005_sdd_do_vibe_coding_a_engenharia_deterministica \
  --relatorio tmp/gate-candidato.json
```

Leia `aprovado` e os resultados em `contratos` no JSON. Se faltar um processo ou uma resposta, o campo `erro` registra a falha de execução quando houver. A decisão da automação usa o código de saída do comando.
