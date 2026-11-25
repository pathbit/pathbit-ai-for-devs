# Gate de release com critérios de aceite executáveis

O laboratório inicia o [Agregador de Notícias do artigo 0005](../0005_sdd_do_vibe_coding_a_engenharia_deterministica/README.md) e verifica seus contratos HTTP. O feed RSS, a porta e o banco SQLite são temporários e locais. A sumarização usa o fallback do próprio Agregador.

Na raiz do repositório, com Python 3 e Node.js disponíveis:

```sh
npm ci --prefix 0005_sdd_do_vibe_coding_a_engenharia_deterministica
python3 0006_gate_de_release_de_contratos/src/verificar_release.py
```

Para guardar a evidência usada pelo gate:

```sh
mkdir -p tmp
python3 0006_gate_de_release_de_contratos/src/verificar_release.py --relatorio tmp/gate-release.json
```

Uma execução aprovada imprime nove resultados `OK` e termina com código 0. Se um contrato falhar ou a aplicação ficar indisponível, o processo termina com código 1. Use `--app <pasta>` para indicar outro checkout do Agregador com suas dependências já instaladas.

[Artigo completo](./article/ARTICLE.md) · [Exemplo de uso](./examples/README.md) · [Artigo para LinkedIn](./article/ARTICLE_LINKEDIN.md) · [Post de divulgação](./article/POST_LINKEDIN.md)
