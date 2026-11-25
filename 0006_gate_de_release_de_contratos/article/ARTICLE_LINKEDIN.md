# Como transformar critérios de aceite em um gate de release

![Cartões passam por uma estação de verificação antes da entrega](../assets/00_capa_gate_release.png)

O importador RSS devolveu HTTP 200 nas duas chamadas. Quantos artigos ficaram no banco depois das duas respostas?

No artigo 0005 da série Pathbit AI for Devs, construímos um Agregador de Notícias usando Spec-Driven Development. No 0006, rodamos a aplicação e transformamos os critérios de aceite em verificações que decidem se uma versão pode avançar.

## O que o gate observa

O laboratório serve um feed com dois artigos e inicia o Agregador com SQLite descartável. A primeira importação deve criar dois registros. A segunda deve criar zero. O digest precisa confirmar que o banco ficou com dois artigos. A combinação dos três resultados mostra se a aplicação cumpriu o contrato de idempotência.

Os nove contratos também cobrem classificação, busca com acentos, paginação inválida, cache de resumos e favoritos. Por exemplo, “Daily newsletter de autenticação” deve entrar em Segurança. Um classificador que encontra as letras `ai` em qualquer trecho pode interpretar “Daily” como inteligência artificial e atribuir a categoria errada.

## Uma falha observável bloqueia a entrega

Para testar o próprio gate, alteramos uma cópia descartável do Agregador para ignorar o filtro de favoritos. Oito contratos passaram. O de favoritos falhou e o processo encerrou com código 1. Assim, o pipeline tem uma decisão explícita mesmo quando a maior parte do fluxo funciona.

O laboratório usa Express, SQLite e um feed entregue via HTTP local. A etapa de resumo exercita o fallback do Agregador. Qualidade de modelos externos, navegação e recuperação depois de reiniciar a aplicação ficam para verificações próprias.

## Execute o laboratório

O [guia de execução](../README.md) mostra como rodar o gate e salvar um resultado em JSON. Você também pode [testar outro checkout](../examples/README.md) e anexar a evidência ao commit que deseja promover.

Leia o [artigo completo](./ARTICLE.md) para ver a tabela de contratos e o critério de aprovação.
