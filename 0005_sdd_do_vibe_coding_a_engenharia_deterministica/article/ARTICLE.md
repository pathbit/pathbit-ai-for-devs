# Do Vibe Coding à Engenharia Determinística usando Spec-Driven Development (SDD) no Claude Code

![Capa do Artigo - SDD](../assets/00_cover_sdd.png)

Nos quatro primeiros artigos desta série, construímos toda a infraestrutura computacional para operar inteligência artificial com autonomia no terminal. No [Artigo 0001](../../0001_antigravity_acesso_total_irrestrito/article/ARTICLE.md), liberamos o acesso irrestrito ao sistema com o motor Agent 2.0 no Google Antigravity. No [Artigo 0002](../../0002_claude_gravity_utilizando_9router/article/ARTICLE.md), criamos o ClaudeGravity para utilizar modelos Gemini no Claude Code via 9Router sem custos de API. No [Artigo 0003](../../0003_fallback_modelos_gratuitos_9router/article/ARTICLE.md), montamos a malha de fallback automático com provedores gratuitos. E no [Artigo 0004](../../0004_deep_claude_alternativa_claudegravity/article/ARTICLE.md), conectamos modelos DeepSeek diretamente ao harness oficial da Anthropic.

Com essa malha técnica estabilizada, o desenvolvedor dispõe de uma máquina de altíssima vazão: um agente autônomo plugado no shell, com acesso de leitura e escrita ao disco, execução de comandos e janelas de contexto que alcançam até um milhão de tokens.

É exatamente quando a infraestrutura deixa de ser um obstáculo que surge a principal questão da engenharia de software contemporânea: **o que você entrega para esse agente construir?**

A resposta mais comum no mercado tem sido o improviso (`_eu chamo de freestyle hehehe_`) conhecido como *vibe coding*. O desenvolvedor abre o terminal, digita um comando de uma frase em linguagem natural e espera que o modelo adivinhe as decisões de arquitetura e produto por telepatia. Em poucos segundos, o agente gera centenas de linhas de código funcional, os testes preliminares passam e a entrega sobe para homologação. Semanas mais tarde, a equipe descobre que o agente adotou premissas silenciosas que contrariam o modelo de negócio, forçando dias de depuração arqueológica para reconstruir qual alvo o modelo imaginou.

Este artigo apresenta o **Spec Driven Development (SDD)**, a disciplina que substitui a loteria dos prompts soltos por especificações executáveis e verificáveis. Mostramos como inverter a relação tradicional entre documentação e código, colocando a especificação escrita como a fonte primária da verdade. Exploramos a anatomia técnica de uma especificação precisa, as armadilhas comuns de ambiguidade, o ciclo iterativo em seis fases, o funcionamento cognitivo da janela de contexto e como os recursos nativos do Claude Code removem o atrito operacional desse método em sistemas de produção.

---

## A economia invertida do software e o fim do "codar no chute"

A ascensão dos agentes de inteligência artificial alterou radicalmente o custo de digitação de código, mas não alterou a economia das decisões de produto e arquitetura.

![Do codar no chute à especificação como alvo](../assets/01_diagrama_chute_vs_spec.png)

> **Figura 1.** O fluxo sem especificação gera retrabalho cíclico e resultado incerto, enquanto o fluxo com SDD conduz a implementação a um destino verificável.

No modelo do improviso, também chamado de "codar no chute", o custo da primeira versão caiu para quase zero. No entanto, o custo de construir a versão errada continua o mesmo de sempre. Na prática, ele se tornou ainda mais perigoso: o software equivocado chega instantaneamente, com tipagem elegante, boa estrutura sintática e testes artificiais que comprovam as premissas inventadas pelo próprio agente.

Considere a dinâmica real de um pedido genérico enviado ao terminal:

```bash
claude "faz um sistema de login com autenticacao pra mim"
```

Diante dessa instrução de uma linha, o agente precisa preencher dezenas de lacunas críticas sem qualquer orientação do desenvolvedor:

- O login deve usar e-mail e senha, OAuth social ou link mágico por e-mail?
- Onde esses dados serão persistidos e qual é a política de hash de senhas?
- A sessão deve ser gerenciada por cookies HTTP-only seguros ou tokens JWT em headers?
- Existe fluxo de recuperação de senha com expiração temporária?
- Qual é o critério exato para afirmar que a tarefa está concluída?

Como os modelos de linguagem são sistemas treinados para minimizar o erro na previsão do próximo token, o agente não interrompe a sessão para pedir uma tese sobre o produto. Ele escolhe a resposta estatisticamente mais comum em seus dados de treino, assume essas premissas em silêncio e escreve quatrocentas linhas de código perfeitamente alinhadas com o seu palpite.

Quando o desenvolvedor finalmente analisa o resultado, surge o veredito inevitável: "não era bem isso". O código construído usou JWT em local storage quando a equipe precisava de cookies de sessão, ou gerou tabelas no MongoDB quando a stack corporativa era PostgreSQL.

O desenvolvedor tenta corrigir a rota com um novo prompt: "não use JWT, mude para cookies e adicione recuperação de senha". O agente adiciona novas camadas de código sobre as anteriores, incha o histórico da conversa com tentativas conflitantes e introduz efeitos colaterais. Uma tarefa simples consome horas em um ciclo desgastante de retrabalho.

Por que o SDD faz sentido econômico hoje, quando métodos formais do passado eram tachados de lentos e burocráticos? No modelo tradicional de software, o mesmo engenheiro humano precisava redigir a documentação detalhada e, depois, digitar manualmente cada linha de código, testes e migrações. Especificar parecia fazer o mesmo trabalho duas vezes.

Com agentes autônomos, essa equação se inverteu por completo. Um engenheiro experiente investe dez minutos para estruturar trinta linhas de especificação cirúrgica com critérios de aceite binários. Em seguida, o agente consome esse documento e gera quinhentas linhas de código, schemas e testes unitários em menos de um minuto. A alavancagem de especificar é ordens de grandeza superior à alavancagem de digitar código.

### O Paradoxo da Velocidade: A Ilusão do Minuto Zero vs. o Muro do Minuto 20

Um dos maiores equívocos de quem migra do *vibe coding* para o Spec-Driven Development é a expectativa ingênua de que o SDD será "mais rápido" logo no primeiro segundo de interação. Ele não é. E compreender essa dinâmica é a chave para não abandonar o método precocemente.

- **No Minuto 0 (A Ilusão do Freestyle):** O *vibe coding* entrega uma gratificação instantânea imbatível. O desenvolvedor dispara um prompt solto de uma frase (`"cria uma API de feed de notícias"`) e, em dez segundos, o terminal cospe trezentas linhas de código colorido com rotas e funções. O cérebro recebe uma descarga imediata de dopamina com a sensação de que a tarefa está quase pronta. Enquanto isso, o engenheiro que adota o SDD ainda está na linha 20 do seu arquivo Markdown em `specs/`, ponderando requisitos não-funcionais de latência e delimitando os itens formalmente fora de escopo. Para um observador desatento, o vibe coder parece estar mil quilômetros à frente.
- **No Minuto 20 (O Muro de Tijolos):** É aqui que a realidade da engenharia se impõe. O código gerado no freestyle não persiste dados corretamente ou falha na primeira requisição real. Ao tentar corrigir com novos prompts soltos, o agente altera silenciosamente contratos de API existentes, quebra rotas que já funcionavam e inventa dependências incompatíveis. O desenvolvedor passa os próximos quarenta minutos em sessões frenéticas de tentativa e erro, poluindo a janela de contexto até que o agente entre em looping alucinatório. A velocidade líquida de entrega despenca para zero.
- **No SDD (A Velocidade Determinística Sustentada):** Os primeiros sete minutos foram consumidos em pensamento disciplinado, estruturando um contrato sólido com critérios de aceite binários e restrições técnicas. Mas quando o comando de implementação é disparado, o agente opera com foco absoluto: entra em *Plan Mode*, quebra a tarefa nas disciplinas certas (banco, rotas, interface e testes) e materializa o código correto na primeira tentativa. Aos quinze minutos, a suíte inteira de testes passa com louvor e a funcionalidade está pronta para homologação sem nenhum débito técnico oculto.

O SDD não compete com o vibe coding pela rapidez de digitar o primeiro caractere; ele domina o ciclo completo ao garantir que o trabalho feito não precise ser jogado no lixo vinte minutos depois.

---

## A virada hierárquica da documentação morta para a especificação executável

No desenvolvimento clássico, o código-fonte sempre foi considerado a única verdade incontestável do repositório. A documentação técnica corria atrás do código, escrita com atraso quando sobrava tempo na sprint e rapidamente abandonada em wikis internas. Se o código discordava da documentação, assumia-se que a documentação estava desatualizada.

O Spec Driven Development inverte deliberadamente essa ordem de autoridade.

![A especificação como fonte da verdade](../assets/02_diagrama_spec_fonte_da_verdade.png)

> **Figura 2.** A inversão de autoridade do SDD: a especificação passa a ser o artefato primário da verdade, e o código se torna um subproduto derivado.

No SDD, a especificação escrita é a fonte primária da verdade do sistema. O código-fonte, os schemas de migração e as suítes de teste são apenas artefatos secundários, derivados mecanicamente a partir dos requisitos definidos.

Quando surge uma divergência entre o código e a especificação, essa discrepância não é tratada como um desvio silencioso, mas como uma decisão consciente de engenharia. Existem apenas duas alternativas: ou o código está errado e o agente deve corrigi-lo imediatamente, ou os requisitos de produto mudaram e a especificação deve ser atualizada e versionada no Git antes de qualquer alteração na implementação.

Essa inversão resolve um problema histórico dos times de tecnologia: o fenômeno da documentação morta.

| Dimensão | Documentação Morta Tradicional | Especificação Executável (SDD) |
| :--- | :--- | :--- |
| Momento de Criação | Escrita depois do código, se houver tempo | Escrita antes do código, orientando o incremento |
| Papel no Sistema | Ninguém consome para gerar trabalho ativo | É o input obrigatório para o agente e para a equipe |
| Efeito da Desatualização | Desatualiza em silêncio sem ser notada | Quebra o ciclo seguinte; o erro surge de imediato |
| Propósito Principal | Prestar contas e registrar histórico passivo | Construir o software e verificar sua conformidade |
| Equação Econômica | Custo contínuo com benefício intangível | Paga seu investimento no primeiro retrabalho evitado |

O termo "executável" não significa que a especificação seja um arquivo binário ou um script que rode na CPU. Significa que existe um agente autônomo com capacidade de interpretá-la literalmente e produzir software a partir dela. Para um modelo de linguagem, uma especificação bem estruturada é combustível de produção de altíssima densidade.

### A fronteira entre o "o quê/por quê" e o "como"

A regra estrutural do SDD reside na separação estrita entre o domínio do problema e os detalhes da implementação:

- **Pertence à especificação (o "o quê" e o "por quê"):** regras de negócio, comportamentos observáveis de fora, contratos de interface, limites de validação, tratamento de erros e critérios de conclusão.
- **Pertence ao código (o "como"):** nomes de variáveis locais, laços de repetição, estruturas de dados transitórias e detalhes internos que nenhum consumidor externo do sistema consegue observar.

A prova de fogo dessa separação é simples: se você decidir trocar a linguagem de programação de Python para Node.js ou Go, o "como" inteiro será reescrito, mas a especificação funcional do "o quê" deve permanecer exatamente idêntica, sem a alteração de uma única linha.

A única exceção admitida ocorre quando o "como" é, na verdade, uma restrição técnica inegociável da infraestrutura com justificativa arquitetural sólida, como exigir o driver `better-sqlite3` por compatibilidade de plataforma ou PostgreSQL por exigência de transações distribuídas já operadas pela organização.

### A curva exponencial do custo do erro

A justificativa financeira para adotar o SDD fundamenta-se na curva clássica de custo de resolução de defeitos.

![O custo do erro por momento de descoberta](../assets/03_diagrama_custo_do_erro.png)

> **Figura 3.** O custo exponencial da correção: alterar uma frase na especificação consome segundos; consertar a mesma falha em produção custa semanas.

Corrigir uma premissa errada enquanto ela é apenas uma linha de texto no arquivo de especificação leva trinta segundos. Corrigir essa mesma premissa depois que ela virou tabelas no banco de dados, regras distribuídas em microsserviços, chamadas de front-end e comportamento assumido por usuários finais custa sprints inteiras de trabalho e gera incidentes graves. O SDD desloca a detecção de inconsistências para o ponto mais barato do ciclo de desenvolvimento: antes de existir código.

---

## Anatomia técnica de uma especificação executável

Uma boa especificação para agentes de inteligência artificial não é um manual volumoso e enfadonho. É um documento conciso, enxuto e orientado a comportamentos verificáveis. Documentos prolixos dispersam a atenção do modelo e aumentam a probabilidade de alucinações.

![Anatomia de uma especificação](../assets/04_diagrama_anatomia_spec.png)

> **Figura 4.** A anatomia de uma especificação funcional com os critérios de aceite operando como núcleo de verificação.

Uma especificação sólida no SDD estrutura-se em sete blocos fundamentais:

### 1. O Quê (Definição do Incremento)
A descrição concisa e objetiva do incremento que será construído. Deve responder sem rodeios: o que é essa entrega em termos de funcionalidade concreta?
- Exemplo: "Construção de um agregador de feeds RSS com persistência relacional em SQLite e dashboard web responsivo."

### 2. Por Quê (Problema de Negócio & Valor Entregue)
O propósito econômico do incremento e quem é o usuário beneficiado, sintetizados em duas ou três linhas diretas. Esta seção ancora a intenção do incremento e impede que o agente resolva uma tarefa sem contexto de negócio.
- Exemplo: "Permitir que desenvolvedores centralizem atualizações tecnológicas de múltiplos portais sem distração de anúncios, viabilizando leitura offline e busca rápida."

### 3. Requisitos Funcionais
Comportamentos observáveis descritos em frases diretas no formato de ação e resultado. Cada requisito deve ocupar uma linha própria, evitando conjunções aditivas ("e") que agrupem duas ações diferentes na mesma sentença.
- O usuário pode filtrar transações por categoria com correspondência exata.
- O usuário pode definir uma data inicial e uma data final para delimitar o período.
- O sistema combina múltiplos filtros ativos por meio de conjunção lógica (AND).

### 4. Requisitos Não-Funcionais
Restrições de performance, segurança, durabilidade e concorrência expressas numericamente. Sempre que uma qualidade for desejada, ela deve ser quantificada objetivamente.
- A rota de listagem deve responder em menos de 300 ms com uma massa de 10.000 registros no banco.
- Todas as credenciais de provedores externos devem ser consumidas estritamente via variáveis de ambiente, sem nenhuma chave exposta no código.
- O estado das transações deve sobreviver ao reinício da aplicação por meio de persistência durável no SQLite com modo WAL.

### 5. Escopo e Fora de Escopo
Duas listas complementares que delimitam rigidamente o que faz e o que não faz parte daquele ciclo de trabalho. A lista de itens fora de escopo é frequentemente mais valiosa do que a de escopo, pois ela atua como um escudo protetor contra o crescimento descontrolado da tarefa (*scope creep*).
- Sem uma seção explícita de fora de escopo, o agente identifica uma lacuna adjacente e decide resolvê-la por iniciativa própria, implementando paginação complexa, autenticação JWT ou busca textual quando a meta era apenas uma listagem básica em memória.

### 6. Restrições Técnicas Fundamentais
Decisões de engenharia que já foram tomadas por motivos de infraestrutura e governança do time, acompanhadas da respectiva justificativa:
- Node.js versão 20+ utilizando módulos ESM nativos para manter conformidade com os demais serviços da Pathbit.
- Persistência em SQLite via biblioteca `better-sqlite3` operando em modo WAL (`journal_mode = WAL`) para permitir execução local determinística sem dependências de containers externos nos testes de CI.

### 7. Critérios de Aceite Binários (O Núcleo de Verificação)
O componente mais importante de toda a especificação. Um critério de aceite é uma afirmação que qualquer pessoa ou subagente consegue testar e responder com sim ou não, sem margem para subjetividade.
- Se dois revisores independentes puderem discordar sobre se um critério foi atendido, ele não é um critério de aceite válido, mas uma opinião disfarçada de requisito.
- Exemplo correto: "POST /transacoes com valor menor ou igual a zero retorna status HTTP 422 com mensagem detalhando o campo inválido."
- Exemplo incorreto: "A validação da API deve ser robusta e tratar erros adequadamente."

---

## Comparativo entre especificação vaga e especificação precisa

Para compreender a diferença prática entre um pedido superficial e uma especificação funcional, compare as duas abordagens para a mesma funcionalidade de filtro de transações:

### A abordagem vaga (armadilha do improviso)

```markdown
# Funcionalidade
Filtro de transações financeiras.

# Descrição
O usuário precisa conseguir filtrar suas transações de forma prática na API.
O endpoint deve ser rápido e seguro. Tratar os erros adequadamente.
```

À primeira vista, o texto soa razoável. No entanto, ele terceiriza cinco decisões críticas de produto para o modelo:

- O que significa "filtrar"? Quais campos são pesquisáveis?
- O que significa "de forma prática"? Os filtros podem ser combinados ou operam de forma isolada?
- O que significa "rápido"? Qual é o teto aceitável de latência e sob qual volume de dados?
- O que significa "tratar os erros"? Consultar uma categoria que não existe no banco é um erro HTTP 404 ou uma listagem vazia com HTTP 200?
- O que acontece se a data inicial informada for posterior à data final?

### A abordagem precisa (padrão SDD)

```markdown
# Objetivo
Permitir que o usuário localize transações financeiras específicas por categoria e data sem percorrer a lista completa.

# Requisitos Funcionais
- Filtrar por categoria através de valor exato em query param.
- Filtrar por período através de data inicial e data final inclusivas no formato YYYY-MM-DD.
- Permitir a combinação simultânea de filtros de categoria e período com conjunção lógica (AND).

# Requisitos Não-Funcionais
- Tempo de resposta inferior a 300 ms em consultas contendo até 10.000 registros indexados.

# Fora de Escopo
- Busca por texto livre em descrições de transações.
- Persistência de filtros favoritos salvos pelo usuário.

# Critérios de Aceite
- GET /transacoes?categoria=alimentacao retorna apenas registros com essa categoria.
- Consultar categoria sem lançamentos cadastrados retorna array vazio [] com status HTTP 200.
- GET /transacoes com data_inicio posterior a data_fim retorna status HTTP 422 com payload de erro explicativo.
- Requisição sem parâmetros de query retorna a listagem completa preservando a ordenação decrescente por data.
```

Na versão precisa, cada linha adicional existe para fechar uma pergunta que o agente teria que adivinhar por conta própria. Não resta nenhuma decisão de produto aberta para ser preenchida estatisticamente.

---

## As seis armadilhas mais comuns de especificação e seus antídotos

Ao redigir especificações para agentes de inteligência artificial, desenvolvedores frequentemente caem em armadilhas de linguagem que parecem inofensivas, mas desestabilizam o comportamento do modelo:

1. **Adjetivos no lugar de números:** Termos como "rápido", "escalável", "amigável" ou "leve" não são verificáveis. O antídoto é quantificar ou descartar. "Rápido" deve ser transformado em "latência p95 abaixo de 200 ms sob 50 requisições simultâneas".
2. **Descrever apenas o caminho feliz:** A especificação detalha o fluxo perfeito, mas esquece o comportamento diante de falhas. O antídoto consiste em incluir obrigatoriamente a pergunta "o que acontece se der errado?" para cada requisito, definindo códigos de status HTTP e mensagens para parâmetros inválidos ou dados ausentes.
3. **Especificação monolítica:** Documentar um sistema complexo inteiro em um único documento extenso esgota a janela de contexto e introduz contradições internas. O antídoto é redigir uma especificação atômica por incremento funcional, cobrindo apenas o próximo ciclo de entrega.
4. **Especificação que é código disfarçado:** Descrever nomes de métodos internos, assinaturas de funções privadas ou estruturas de laços de repetição retira a flexibilidade do agente e confunde a revisão. O antídoto é focar exclusivamente nos efeitos observáveis a partir da interface externa do módulo.
5. **Ambiguidade silenciosa de pronomes:** Expressões como "listar as transações dele", "no mês corrente" ou "quando apropriado" escondem premissas perigosas. O antídoto é caçar termos relativos e substituí-los por regras explícitas de fuso horário, limites de calendário e papéis de usuário.
6. **Requisitos agregados com conjunção "e":** Frases que contêm "o sistema valida a entrada, grava no banco e dispara um e-mail" impedem a verificação atômica. O antídoto é fatiar o comportamento em sentenças independentes, permitindo que cada ação seja testada isoladamente.

### A regra de ouro do SDD

Para validar a qualidade de uma especificação antes de submetê-la ao Claude Code, aplique o teste definitivo:

> **Regra de Ouro:** Se um desenvolvedor novo na equipe conseguisse implementar a funcionalidade lendo apenas a especificação, sem fazer nenhuma pergunta adicional aos colegas, então o agente autônomo também conseguirá.

Toda vez que você reler a sua especificação e pensar "aqui um desenvolvedor júnior precisaria me perguntar qual formato de data utilizar", você acabou de identificar uma decisão em aberto que o modelo completará por adivinhação estatística.

### O Tamanho Ideal de uma Especificação: O Sweet Spot de 100 a 300 Linhas

Uma das dúvidas mais frequentes de equipes que adotam o SDD é: *"qual deve ser o tamanho de um arquivo de especificação?"*. A resposta técnica é direta: **o tamanho ideal de uma especificação executável fica entre 100 e 300 linhas de Markdown**.

Essa métrica não é arbitrária; ela reflete a física da janela de contexto e a ergonomia de engenharia:

- **Abaixo de 50 linhas (Subespecificação ou Overkill):** Documentos excessivamente curtos quase sempre sofrem de dois problemas opostos: ou são vagos demais (terceirizando comportamentos fundamentais para o modelo), ou tratam de tarefas mecânicas triviais (como corrigir um typo ou renomear uma variável), nas quais escrever uma spec formal é puro desperdício burocrático.
- **Entre 100 e 300 linhas (O Ponto Ótimo):** Essa extensão é suficiente para documentar uma fatia vertical completa de valor: o objetivo de negócio, 4 a 8 requisitos funcionais, métricas numéricas não-funcionais, listas rigorosas de escopo e fora-de-escopo, restrições técnicas do projeto e entre 5 e 8 critérios binários de aceite. Cabe integralmente na atenção primária da rede neural, sem cansar a janela de contexto.
- **Acima de 400 linhas (A Regra dos 400 Linhas):** Quando uma especificação ultrapassa 400 linhas, ela invariavelmente tenta abraçar múltiplos domínios ao mesmo tempo (ex.: autenticação, faturamento e notificações em um único arquivo). Modelos de linguagem começam a apresentar o efeito de diluição de atenção (*attention drift*), priorizando instruções do topo ou do rodapé e esquecendo regras cruciais no meio do documento.

> **A Regra de Decomposição:** Se a sua especificação ultrapassar 400 linhas, **pare imediatamente e decomponha**. Divida o incremento em sub-especificações por valor observável entregue (por exemplo: `specs/01-feed-artigos.md`, `specs/02-busca-filtros.md`, `specs/03-dashboard-analytics.md`). Cada sub-spec mantém seu próprio ciclo de validação, testes e commit, permitindo que a aplicação evolua de forma modular e 100% determinística.

---

## O ciclo iterativo em seis fases e a mecânica do loopback

O Spec Driven Development não é um evento estático de início de projeto, mas um motor de entrega contínua que opera em ciclos atômicos.

![O ciclo iterativo em seis fases](../assets/05_diagrama_ciclo_sdd.png)

> **Figura 5.** O ciclo em seis fases do SDD. A seta de retorno evidencia que voltar à especificação faz parte da operação normal do método.

O fluxo de cada incremento atravessa seis fases encadeadas:

### Fase 0 - Princípios globais: A Constituição Viva (`CLAUDE.md` e `AGENTS.md`)
Definição dos padrões duradouros do repositório que se aplicam a todos os incrementos futuros: convenções de formatação, suítes de teste, políticas de branches, stack tecnológica e regras inegociáveis de governança.

No ecossistema moderno de agentes de código, essa constituição se materializa em dois padrões complementares:
- **`AGENTS.md` (Padrão Aberto da Indústria):** Documento agnóstico adotado pela comunidade para instruir qualquer agente de inteligência artificial que opere no repositório — seja o Claude Code, Codex, Devin, Cursor, Windsurf, Copilot, Cline ou Antigravity.
- **`CLAUDE.md` (Harness Nativo do Claude Code):** Arquivo lido prioritariamente pela CLI do Claude Code na inicialização de cada sessão. Quando ambos os arquivos coexistem, o Claude Code carrega o `CLAUDE.md`, que pode apontar para o `AGENTS.md` e reforçar as regras locais imediatas.

> **Regra Inegociável de Governança (Autoria Humana Sempre):** Tanto no `CLAUDE.md` quanto no `AGENTS.md`, uma das regras mais críticas é a proibição absoluta de assinaturas sintéticas de IA em mensagens de commit (como `Co-Authored-By: Claude...` ou `🤖 Generated with...`). Essa diretriz é vital porque plataformas como o GitHub montam a lista pública de *Contributors* a partir desses metadados de commit, podendo incluir contas de bots como colaboradoras oficiais do projeto e corromper o índice histórico. No SDD da Pathbit, todo commit carrega estritamente a identidade humana do engenheiro responsável.

### Fase 1 - Especificar
Redação da especificação do próximo incremento atômico de funcionalidade, versionada no diretório `specs/` (por exemplo, `specs/01-feed-artigos.md`). O desenvolvedor documenta apenas o próximo bloco de entrega, nunca a aplicação inteira de uma vez.

### Fase 2 - Planejar
O agente de inteligência artificial inspeciona a árvore de arquivos existente, lê a especificação do incremento e gera uma proposta técnica detalhada em modo somente leitura (plan mode). O engenheiro revisa a rota proposta, aponta ajustes arquiteturais e alinha decisões antes que qualquer modificação seja gravada no disco.

### Fase 3 - Tarefas
O plano técnico aprovado é quebrado em uma sequência ordenada de tarefas atômicas e rastreáveis, funcionando como um checklist executável para a sessão de trabalho.

### Fase 4 - Implementar
Com o plano e os critérios blindados, o agente escreve o código-fonte, atualiza migrações e conecta os componentes necessários.

### Fase 5 - Verificar
A entrega é submetida a uma bateria rigorosa de validação contra cada um dos critérios de aceite previamente estabelecidos na especificação.

### A mecânica do laço de retorno consciente (loopback)

O aspecto que afasta definitivamente o SDD do modelo tradicional em cascata (waterfall) é o laço de retorno evidenciado no diagrama. Voltar atrás no SDD não representa uma falha de planejamento, mas sim o método funcionando com maturidade.

Se durante a fase de implementação o agente ou o desenvolvedor identificam que uma restrição técnica é inviável, que uma biblioteca externa mudou sua interface pública ou que uma regra de negócio se mostrou incoerente, a implementação é pausada imediatamente. O desenvolvedor não remenda o código no improviso: ele retorna à especificação, atualiza o texto com a nova decisão consciente, commita a alteração e reinicia o fluxo a partir de uma base transparente.

---

## Sob o capô da rede neural e como um agente interpreta uma especificação

Para extrair resultados de nível profissional de ferramentas agênticas, o engenheiro precisa dominar a física da janela de contexto.

Um modelo de linguagem não tem consciência dos acordos verbais firmados na reunião da equipe, não lê mensagens trocadas no Slack e não sabe o que o desenvolvedor "quis dizer". A totalidade da capacidade cognitiva do agente em cada turno depende exclusivamente do texto presente na sua janela de contexto.

![A janela de contexto do agente](../assets/06_diagrama_janela_contexto.png)

> **Figura 6.** A janela de contexto como fronteira finita do agente, ilustrando o sinal visível contra o conhecimento implícito que fica de fora.

Fazem parte do sinal visível: a mensagem digitada pelo usuário, os arquivos lidos do repositório, o arquivo de configuração `CLAUDE.md`, as saídas de comandos bash e o histórico da conversa recente.

Ficam irremediavelmente de fora: os padrões implícitos que "todo mundo na empresa sabe", premissas de produto não escritas e decisões informais de arquitetura.

Quando um modelo de linguagem encontra uma instrução ambígua ou incompleta, sua resposta é governada pela mecânica estatística da rede neural: o modelo não trava por indecisão e raramente pede esclarecimentos adicionais. Ele completa o texto com a sequência de tokens estatisticamente mais provável com base em trilhões de palavras absorvidas no seu treinamento.

Plausível, no entanto, é o oposto de correto para a regra de negócio específica do seu produto. Pior ainda: o modelo gera centenas de linhas de código que mantêm uma consistência interna absoluta com o palpite equivocado. O código compila sem erros, os testes sintéticos passam com louvor e a aplicação parece impecável, enquanto resolve com perfeição o problema errado.

A engenharia de contexto no SDD não consiste em entupir a conversa com prompts descomunais ou colar cinquenta arquivos desnecessários na tela. Alimentar a janela com excesso de informação gera diluição de atenção e alucinações de dependências cruzadas. A verdadeira disciplina de contexto reside na curadoria enxuta: uma especificação concisa por ciclo, convenções globais salvas no `CLAUDE.md` e a renovação periódica de sessões limpas para evitar contaminação por históricos antigos.

---

## Matriz metodológica entre SDD, TDD, Vibe Coding e Waterfall

Nenhuma abordagem técnica é uma bala de prata universal para todos os cenários de software. O discernimento de um engenheiro sênior reside em posicionar o método correto no quadrante adequado de risco e incerteza.

![Mapa de métodos por ambiguidade e custo do erro](../assets/07_diagrama_mapa_metodos.png)

> **Figura 7.** Posicionamento das metodologias avaliando o grau de ambiguidade do requisito versus o custo de erros em produção.

O *vibe coding* possui utilidade real e produtiva no seu quadrante legítimo: scripts de automação pessoal, protótipos descartáveis de prova de conceito e correções cosméticas simples onde a falha tem custo irrelevante. Tentar aplicar um fluxo formal de especificação para alterar o texto de um botão em uma página interna é mero desperdício operacional.

O modelo em cascata (waterfall) clássico fracassa na ponta oposta: tenta redigir as especificações de um sistema massivo inteiro com meses de antecedência, tratando qualquer mudança posterior como um desvio custoso em um mercado onde as necessidades de produto mudam semanalmente.

O Spec Driven Development ocupa com precisão a região de alto valor: código corporativo de produção, onde há ambiguidade nos requisitos, trabalho colaborativo entre múltiplos engenheiros, regras sensíveis de negócio e necessidade de sustentação do software por anos.

### A sinergia arquitetural entre SDD e TDD

Uma dúvida recorrente entre desenvolvedores é se a adoção do SDD torna o Test-Driven Development (TDD) redundante. Na realidade, os dois métodos atuam em camadas complementares da engenharia:

| Dimensão de Análise | Spec Driven Development (SDD) | Test-Driven Development (TDD) |
| :--- | :--- | :--- |
| Pergunta Fundamental | O que devemos construir e quais são os limites do negócio? | O código implementado executa a lógica conforme o esperado? |
| Nível de Abstração | Comportamento observável do produto e fronteiras de domínio | Funções, classes, contratos de métodos e integração técnica |
| Artefato Primário | Especificação em Markdown com critérios de aceite binários | Suítes de testes unitários e de integração em código |
| Destinatários | Engenheiros, time de produto e agentes autônomos de IA | Compiladores, esteiras de CI/CD e desenvolvedores |

O critério de aceite da especificação é a matéria-prima exata que origina os testes do TDD. Um critério de aceite formulado como "POST /transacoes com valor negativo retorna HTTP 422" é a descrição literal do caso de teste automatizado que será escrito na suíte.

Uma bateria inteira de testes verdes comprova que a aplicação opera estritamente conforme o código foi escrito, mas não garante que o sistema atende à necessidade real da organização. A especificação assegura o rumo correto do produto, enquanto o TDD garante a solidez da implementação.

---

## Governança de engenharia e SDD em equipe: Por que o SDD não é apenas para desenvolvedores

Quando múltiplos profissionais colaboram em um ecossistema acelerado por agentes autônomos de inteligência artificial, o SDD transcende a função de método de codificação individual e se torna o **sistema operacional de alinhamento de toda a organização de tecnologia e produto**.

Historicamente, o desenvolvimento de software sofreu com o clássico "jogo do telefone sem fio": a visão estratégica do negócio era convertida em documentos de requisitos comerciais (PRDs), fatiada em cartões no Jira por gerentes de produto, reinterpretada por engenheiros de software durante a implementação e testada tardiamente pela equipe de qualidade contra critérios desatualizados. Com o advento de agentes de IA capazes de gerar milhares de linhas de código em segundos, qualquer desalinhamento inicial nessa cadeia é amplificado exponencialmente, transformando pequenas ambiguidades em avalanches de retrabalho técnico.

O Spec-Driven Development resolve essa fratura estrutural ao estabelecer a **especificação em Markdown no repositório Git como o contrato único, vivo e executável compartilhado por todos os papéis da equipe**.

### A Matriz Multidisciplinar do SDD

A tabela a seguir consolida como o SDD revoluciona a rotina e as entregas de cada integrante do ciclo de desenvolvimento de software:

| Papel na Equipe | O Gargalo Histórico (Sem SDD / Vibe Coding) | O Superpoder com Spec-Driven Development | Artefato Prático no Ciclo SDD |
| :--- | :--- | :--- | :--- |
| **Product Manager (PM / PO)** | Descolamento crônico entre os cartões de tarefas e o código real em produção; incapacidade de auditar o que o agente de fato construiu sem ler código técnico. | Autoria e validação direta das regras de negócio em Markdown. O PM aprova o comportamento observável antes da escrita de uma única linha de código. | `specs/NN-nome.md` (seções Objetivo, Requisitos Funcionais e Escopo). |
| **QA / Engenheiro de Testes** | Elaboração de planos de teste reativos no fim da sprint; necessidade de adivinhar casos de borda e comportamentos esperados por falta de critérios objetivos. | Critérios de aceite binários já nascem como a suíte de testes. Zero adivinhação: o QA audita a spec antes da implementação e automatiza testes diretamente dos critérios. | Matriz de Critérios de Aceite Binários (`specs/NN-nome.md`) e testes automatizados (`tests/*.test.js`). |
| **Tech Lead / Arquiteto** | Dívida técnica gerada pelo agente de IA importando bibliotecas arbitrárias, ignorando padrões de persistência e criando complexidade desnecessária. | Blindagem arquitetural absoluta. As decisões de persistência, segurança, performance e convenções ficam travadas nas restrições da spec e no `CLAUDE.md`. | Seções de *Restrições Técnicas*, *Requisitos Não-Funcionais* e o arquivo `CLAUDE.md`. |
| **Desenvolvedor / Engenheiro** | Sobrecarga cognitiva ao ter que "adivinhar por telepatia" a regra de negócio enquanto orquestra o agente de IA; loops infinitos de refatoração para corrigir alucinações. | Foco total na arquitetura e na orquestração. O agente de IA opera com mais de 95% de assertividade na primeira tentativa, eliminando a fadiga de contexto. | Plano de execução (`plan mode`), comandos do harness (`/implementar-spec`) e código derivado. |
| **Stakeholders / Negócio / C-Level** | Imprevisibilidade de prazos, alto custo de retrabalho e dependência da memória tácita de desenvolvedores veteranos para entender o sistema. | Rastreabilidade histórica impecável via `git log`. Previsibilidade de entrega, redução drástica do ciclo de feedback e documentação viva que nunca envelhece. | Histórico de commits das especificações versionadas e relatórios de verificação de critérios de aceite. |

### Os 4 Pilares da Governança em Equipe com SDD

1. **A Especificação como Pull Request Pré-Código:**
   No fluxo maduro de engenharia, a especificação passa por Pull Request e revisão formal de pares *antes* de qualquer código ser gerado. PMs, Tech Leads e QAs comentam diretamente no diff do Markdown. Ajustar um requisito na spec nessa fase consome 30 segundos; corrigir o mesmo requisito após o agente ter gerado 500 linhas de código com dependências cruzadas consome dias.

2. **Fim da Arqueologia Técnica e Documentação Viva:**
   Diferente de wikis corporativas esquecidas e páginas obsoletas no Confluence, as specs residem no mesmo repositório do código sob controle de versão. Quando um engenheiro precisa entender por que uma regra de expiração de token foi adotada há dois anos, o histórico do Git da pasta `specs/` revela a motivação de negócio, os critérios de aceite da época e o contexto original sem ambiguidades.

3. **Democratização da Automação de Testes:**
   Como os critérios de aceite de uma spec bem elaborada são binários (passam ou falham com sim/não inequívoco), eles formam uma especificação executável. O QA pode espelhar a spec diretamente em asserções de teste automatizado (usando Vitest, Jest, Playwright ou Cypress) enquanto o agente implementa a lógica do serviço, habilitando verdadeira paralelização entre desenvolvimento e validação.

4. **Redução Radical do Custo de Inferência e Tokens:**
   No modelo caótico de Vibe Coding, desenvolvedores gastam dezenas de milhares de tokens em prompts confusos, loops de depuração e tentativas sucessivas de corrigir erros de escopo. Com uma spec executável e enxuta, o agente de IA recebe exatamente o contexto necessário na janela de atenção, reduzindo o consumo de tokens e prevenindo o estouro de cotas de contexto na inferência.

---

## O ecossistema do Claude Code configurado para SDD

A adoção sustentável do SDD depende da remoção de atritos na rotina diária. A ferramenta Claude Code CLI disponibiliza um ecossistema nativo de recursos que se acoplam com precisão a cada fase do ciclo de desenvolvimento.

![Ferramentas do Claude Code encaixadas nas fases do ciclo](../assets/08_diagrama_ferramentas_fases.png)

> **Figura 8.** O mapeamento das ferramentas nativas do Claude Code sobre as fases do ciclo de Spec Driven Development.

### 1. `CLAUDE.md` como memória permanente do projeto
Localizado na raiz do repositório, o arquivo `CLAUDE.md` é lido automaticamente na inicialização de cada sessão de trabalho. Ele funciona como o repositório imutável dos princípios do projeto: comandos de compilação, scripts de teste, políticas de banco de dados e convenções de estilo. Informações transitórias de um único incremento nunca devem poluir esse arquivo, pertencendo exclusivamente à especificação daquela tarefa.

### 2. Slash commands e o ritual automatizado do ciclo
No Claude Code, definimos comandos reutilizáveis na pasta `.claude/commands/` para transformar o fluxo de SDD em rotina instantânea.

O primeiro comando é o `.claude/commands/spec.md`, acionado via `/spec <descrição>`:

```markdown
Escreva uma especificação para o incremento descrito abaixo e salve em specs/ com o próximo número da sequência. Use exatamente esta estrutura:

## Objetivo
O problema real e quem se beneficia, em duas linhas.

## Requisitos funcionais
Um por linha, comportamento observável.

## Requisitos não-funcionais
Desempenho, segurança, persistência, com números.

## Escopo e Fora de escopo
As duas listas, sempre.

## Restrições técnicas
O "como" que já foi decidido, com o motivo.

## Critérios de aceite
Cada um verificável com sim ou não.

Antes de escrever, liste as ambiguidades que encontrou no meu pedido e me pergunte sobre elas.

Incremento: $ARGUMENTS
```

O segundo comando é o `.claude/commands/implementar-spec.md`, que padroniza a execução a partir do arquivo de especificação:

```markdown
Leia a spec em: $ARGUMENTS

1. Entre em plan mode e me proponha o plano de implementação. NÃO altere arquivos ainda.
2. Aguarde minha aprovação antes de tocar em qualquer arquivo.
3. Implemente APENAS o que está nesta spec; não adiante features de ciclos futuros.
4. Respeite as convenções e decisões registradas no CLAUDE.md.
5. Ao final, verifique o resultado contra os Critérios de aceite da spec e me diga, item a item, se cada um passou.
```

Com esse comando configurado, a instrução diária no terminal se resume a uma única linha enxuta: `/implementar-spec specs/01-feed-artigos.md`. Essa prática consolida uma regra de ouro: **os prompts no chat devem ser propositalmente magros**. O peso do conhecimento reside nas especificações versionadas e no `CLAUDE.md`. Se você sentir necessidade de digitar parágrafos explicativos no chat da CLI, não faça isso no prompt: atualize a especificação.

### 3. Plan Mode para pensar antes de tocar no disco
Acionado pelo atalho `Shift+Tab` no terminal do Claude Code ou integrado diretamente na lógica do `/implementar-spec`, o **Plan Mode** coloca o agente em modo de leitura estrita e investigação arquitetural preliminar.

O agente analisa a árvore de arquivos, inspeciona os esquemas existentes em `src/db/`, lê os contratos de rotas e propõe uma estratégia técnica passo a passo dividida pelas disciplinas de engenharia. O desenvolvedor valida o plano antes que qualquer linha seja modificada no repositório.

Essa disciplina reflete uma verdade econômica crucial: **descartar texto custa segundos; descartar código implementado custa horas**. Mudar de ideia durante a leitura de um plano técnico consome zero linhas de diff no Git; refatorar cinquenta arquivos modificados precipitadamente por um agente impulsivo consome tardes inteiras de depuração.

### 4. Orquestração de Subagentes e Equipes de IA para Validação Cruzada (Cross-Validation)
Pedir para o mesmo agente que implementou o código auditar a sua própria entrega é um dos erros conceituais mais graves na engenharia com inteligência artificial. O agente principal carrega o **viés de confirmação** de toda a sessão: ele tende a justificar as próprias premissas e a ignorar lacunas no código que ele mesmo gerou.

No Spec-Driven Development maduro, quebramos esse viés através de uma **Equipe de Agentes com Três Papéis Especializados**:

| Papel do Agente | Modo de Execução & Contexto | Responsabilidade Estrita | Saída / Entregável |
| :--- | :--- | :--- | :--- |
| **1. Agente Arquiteto** | **Plan Mode** (`Shift+Tab`) / Somente leitura | Lê `docs/arquitetura.md`, memória viva e a spec; formula o plano nas 6 disciplinas sem tocar no disco. | Estratégia técnica aprovada pelo engenheiro |
| **2. Agente Implementador** | **Execution Mode** / Contexto ativo de código | Materializa estritamente os arquivos autorizados no plano aprovado (DB, rotas, SPA e Docker). | Código desacoplado e testes unitários |
| **3. Subagente Auditor / QA** | **Janela Virgem Isolada** (Zero viés prévio) | Audita o `git diff` contra os critérios binários de aceite da spec e executa a suíte `npm test`. | Parecer binário (Aprovado / Reprovado) |

No Claude Code, definimos o subagente auditor dentro de `.claude/agents/revisor-de-spec.md`:

```markdown
---
name: revisor-de-spec
description: Confere a implementação contra os critérios de aceite da spec.
---

Você recebe o caminho de uma spec e o diff da implementação. Para cada critério de aceite da spec, responda:

- ATENDIDO, e onde no código isso acontece.
- NÃO ATENDIDO, e o que exatamente está faltando.
- DUVIDOSO, e qual ambiguidade da spec impede decidir.

Aponte também o que foi implementado e não estava na spec. Não sugira melhorias de estilo. Não elogie. Sua única pergunta é: isto cumpre a spec?
```

O auditor recebe exclusivamente a especificação e o `git diff`. Como sua janela de contexto não contém o histórico de tentativa e erro do implementador, sua avaliação é fria, imparcial e puramente determinística.

### 5. Memória Viva do Repositório: `AGENTS.md`, `CLAUDE.md` e Documentação de Arquitetura
Para evitar que o modelo sofra de "amnésia arquitetural" ao longo de semanas de desenvolvimento, o repositório mantém uma malha viva de documentação técnica:

- **`AGENTS.md` (Governança Universal):** Documento lido por qualquer agente de mercado (Claude Code, Antigravity, Cursor, Devin, Copilot). Estabelece a regra pétrea de **autoria humana nos commits** (proibição de trailers sintéticos) e aponta os padrões do projeto.
- **`CLAUDE.md` (Harness do Claude Code):** Declara comandos operacionais imediatos (`npm start`, `npm test`), variáveis locais e atalhos de slash commands.
- **`docs/arquitetura.md` e `docs/infraestrutura.md`:** Documentos vivos que registram diagramas C4, decisões de design tokens, convenções de erro HTTP 422, mapeamento de portas locais e estratégias de containerização Docker.
- **`specs/roadmap.md` e o comando `/status-sdd`:** Matriz de governança que rastreia os incrementos entregues (`CONCLUÍDO`) e pendentes (`BACKLOG`), impedindo que o agente gaste tokens revalidando código antigo em ciclos desnecessários.

### 6. Controle de versão com a disciplina dos dois commits
O fluxo de versionamento do SDD estabelece a separação explícita entre intenção e implementação através de dois commits por incremento:

```bash
# Passo 1: Commitar a intencao (especificacao)
git add specs/01-feed-artigos.md
git commit -m "spec: definir leitura de feed rss e listagem de artigos"

# Passo 2: Executar o ciclo (planejar, implementar e verificar com testes)
# ...

# Passo 3: Commitar a realizacao (codigo e testes validados)
git add src/ tests/ specs/roadmap.md
git commit -m "feat: implementar ingestao de feed rss conforme spec 01"
```

Essa separação registra a cronologia da intenção antes da escrita do código, garantindo que o histórico do Git conte a evolução arquitetural do produto com total transparência.

---

## Estudo de caso da API de Agregador de Notícias em seis ciclos de SDD

Para demonstrar a eficácia prática da metodologia, o repositório oficial da Pathbit disponibiliza no diretório `examples/` uma API completa de um agregador de notícias com resumo automatizado por inteligência artificial, construída em Node.js com Express, SQLite durável e SDK da Anthropic.

O projeto foi dividido em seis ciclos atômicos de SDD. A tabela a seguir documenta as armadilhas de produto e arquitetura que cada especificação congelou antecipadamente, evitando que o agente tomasse decisões inadequadas no improviso:

| Ciclo | Incremento Funcional | Decisão Crítica de Negócio Travada pela Spec |
| :--- | :--- | :--- |
| Ciclo 01 | Leitura de Feed RSS e Listagem | Chave primária de desduplicação fixada na coluna `link` e ordenação cronológica decrescente |
| Ciclo 02 | Gestão e Sincronização de Fontes | Validação prévia de XML e isolamento de falhas: uma fonte fora do ar não interrompe as demais |
| Ciclo 03 | Resumo de Artigos com IA | Política estrita de cache em banco local para mitigar custos e impedir chamadas redundantes à API |
| Ciclo 04 | Categorização e Filtros | Mapeamento temático com fallback seguro e retorno obrigatório de status HTTP 422 para datas inválidas |
| Ciclo 05 | Digest Diário e Testes | Resposta previsível para dias sem notícias e mock determinístico obrigatório da IA na suíte de testes |
| Ciclo 06 | Favoritos, Métricas e Deploy | Isolamento de portas e injeção de credenciais estritamente via variáveis de ambiente |

Em cada um desses ciclos, um pedido vago de *vibe coding* ("faça um agregador de notícias com IA") teria produzido um sistema imprevisível: o modelo chamaria a API da Anthropic a cada requisição de leitura esgotando o limite de tokens, usaria o título da notícia como chave de desduplicação duplicando matérias reescritas e derrubaria o servidor quando um dos feeds RSS estivesse fora do ar. A especificação transformou todas essas incertezas em contratos rígidos antes da escrita da primeira linha de código.

---

## Roteiro prático para adotar SDD na sua equipe

Para implementar o Spec Driven Development imediatamente em qualquer projeto apoiado por Claude Code, estruture cinco elementos na raiz do seu repositório:

1. **Memória permanente:** Crie um arquivo `CLAUDE.md` objetivo contendo comandos de build, suítes de teste e convenções de estilo que valem para todos os ciclos.
2. **Pasta de especificações:** Crie o diretório `specs/` versionado no Git para armazenar as especificações atômicas de cada incremento numeradas em ordem sequencial.
3. **Template de comando `/spec`:** Configure o arquivo `.claude/commands/spec.md` com as seis seções obrigatórias e a diretiva de caçar ambiguidades antes da escrita.
4. **Subagente de auditoria:** Configure o arquivo `.claude/agents/revisor-de-spec.md` para comparar diffs de código contra critérios de aceite em contexto virgem.
5. **Disciplina operacional:** Estabeleça o compromisso de revisar a rota técnica no Plan Mode (`Shift+Tab`) e commitar a especificação antes da autorização de escrita no disco.

Todos os templates de configuração, especificações do estudo de caso, comandos customizados e o subagente revisor estão prontos para cópia direta no diretório `examples/` do repositório da Pathbit.

---

## Conclusão

A evolução dos agentes autônomos de desenvolvimento não tornou a engenharia de software obsoleta. Ao contrário: transferiu o valor da profissão da digitação mecânica de código para a capacidade de formular problemas, desenhar arquiteturas e definir critérios de validação rigorosos.

Quando o custo de produzir código colapsa, a habilidade mais valiosa de um desenvolvedor deixa de ser a velocidade de digitação e passa a ser a precisão de pensamento. O Spec Driven Development devolve ao engenheiro o controle soberano sobre a arquitetura do sistema. Ao ancorar o Claude Code em especificações executáveis, planos validados previamente e auditorias em contexto isolado, transformamos a potência probabilística da inteligência artificial em uma esteira de entrega previsível, estável e profissional.

---

## Referências Bibliográficas

- [Beck, Kent: Test-Driven Development by Example (Addison-Wesley)](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
- [Anthropic: Claude Code Official CLI Documentation and Best Practices](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
- [Fowler, Martin: Specification by Example and Executable Specifications](https://martinfowler.com/bliki/SpecificationByExample.html)
- [Karpathy, Andrej: Software 2.0 and the Evolution of Programming with Neural Networks](https://karpathy.medium.com/software-2-0-2e22f080b06b)
- [North, Dan: Introducing Behaviour-Driven Development (BDD)](https://dannorth.net/introducing-bdd/)

---

Repositório oficial no GitHub no endereço https://github.com/pathbit/pathbit-ai-for-devs no módulo 0005_sdd_do_vibe_coding_a_engenharia_deterministica.

#InteligenciaArtificial #SpecDrivenDevelopment #SDD #ClaudeCode #EngenhariaDeSoftware #VibeCoding #SoftwareArchitecture #Pathbit
