# Duas tarefas no mesmo Agregador

## Worktree API

> Planeje e implemente GET /health no src/server.js. Deve responder status 200, JSON {"status":"ok"} e preservar GET / e GET /artigos. Compare com os testes existentes. Limite o diff à rota e aos testes do contrato. Rode npm test.

## Worktree Dashboard

> Planeje e ajuste apenas o h1 em src/public/index.html para "Meu Agregador de Notícias". Preserve os botões, filtros e ações existentes. Rode npm test e confirme a alteração no HTML servido.

## Expectativas ao integrar

As duas branches partem do mesmo commit. A primeira altera o servidor e seus testes. A segunda altera o HTML. Rode npm test após integrar os dois commits e valide os dois endpoints no mesmo processo.
