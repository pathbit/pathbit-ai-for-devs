# Post LinkedIn sobre critérios de aceite executáveis

O servidor devolveu HTTP 200 duas vezes. O segundo pedido importou alguma notícia em duplicidade?

No artigo 0006 da série Pathbit AI for Devs, usamos o Agregador de Notícias do módulo anterior para transformar critérios de aceite em um gate de release. O laboratório inicia Express e SQLite, importa o mesmo feed duas vezes e verifica os efeitos pela API.

- A primeira chamada cria dois artigos.
- A segunda cria zero.
- O digest confirma que o banco ficou com dois registros.

O gate cobre nove contratos, incluindo busca, resumo e favoritos. Alteramos uma cópia descartável da aplicação para ignorar o filtro de favoritos. Oito contratos passaram e a entrega ficou bloqueada pelo único que falhou.

O [laboratório completo](./ARTICLE.md) inclui o código e o passo a passo para gerar a evidência em JSON. Que critério de aceite seu pipeline já consegue comprovar com a aplicação rodando?

#EngenhariaDeSoftware #SpecDrivenDevelopment #TestesDeSoftware #IntegraçãoContínua #Pathbit
