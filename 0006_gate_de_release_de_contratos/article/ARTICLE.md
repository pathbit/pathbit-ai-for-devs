# Gate de release com critérios de aceite executáveis

![Cartões passam por uma estação de verificação antes da entrega](../assets/00_capa_gate_release.png)

No [artigo 0005](../../0005_sdd_do_vibe_coding_a_engenharia_deterministica/article/ARTICLE.md) construímos um agregador de notícias a partir de especificações. O próximo passo é decidir se a aplicação que acabou de ser construída está pronta para entrega. Para isso, transformamos os critérios de aceite em requisições e verificamos os efeitos observáveis na própria aplicação em execução.

## Do critério de aceite à verificação

O critério “a segunda importação não duplica artigos” vale mais que um teste que observa apenas HTTP 200. O cenário manda o mesmo feed duas vezes, confere dois artigos novos na primeira resposta e zero na segunda. O digest confirma o total persistido depois. Se a API responder sucesso e gravar duplicatas, o gate rejeita a versão.

| Contrato | Verificação |
| --- | --- |
| Isolamento da execução | Um banco novo começa vazio. |
| Importação e idempotência | O mesmo RSS produz dois artigos na primeira chamada e zero na segunda. |
| Busca e classificação | O filtro de Segurança e a busca acentuada retornam o artigo esperado. |
| Paginação | Um limite inválido recebe HTTP 422. |
| Resumo | A primeira chamada gera o texto. A segunda devolve o mesmo texto com indicação de cache. |
| Favoritos | Um artigo aparece no filtro depois de ser marcado e desaparece após a remoção. |
| Digest | A API contabiliza dois artigos, um resumo e zero favoritos. |

O feed usa um caso de classificação que parece trivial. “Daily newsletter de autenticação” contém as letras `ai` dentro de outra palavra. Um classificador que procura apenas a sequência `ai` escolhe IA antes de avaliar autenticação. O critério exige a categoria Segurança e transforma esse erro em um bloqueio reproduzível.

## Ambiente de execução

A aplicação usa Express, o parser RSS e o SQLite reais. O script serve dois itens de exemplo via HTTP em loopback e inicia o Agregador em uma porta livre com uma base temporária. O runner também executa o fallback de resumo da aplicação com as chaves externas vazias. Isso confere cache e persistência sem depender de catálogo, cotas ou disponibilidade de provedores.

A interface do navegador, a qualidade das saídas de um modelo contratado e a persistência depois de reiniciar o servidor exigem cenários próprios. O resultado do gate tem o escopo dos nove contratos acima.

## Show-Me-The-Code

### Opção 1. Rodar pelo guia do módulo

O [README do módulo](../README.md) traz o comando para instalar as dependências do Agregador e executar os nove contratos com Python.

### Opção 2. Rodar contra um checkout candidato

O [exemplo de uso](../examples/README.md) mostra como executar o gate contra outro checkout e guardar a evidência em JSON. No pipeline, execute o mesmo comando depois da instalação das dependências. O código de saída decide a promoção da versão.

## Critério de publicação

Uma versão avança se a aplicação iniciar, todos os nove contratos forem observados e cada um passar. Uma verificação que não chegou a rodar deixa a versão bloqueada. Guarde o JSON junto ao identificador do commit quando executar o gate em CI. A evidência permite responder qual revisão passou e qual comportamento foi observado.
