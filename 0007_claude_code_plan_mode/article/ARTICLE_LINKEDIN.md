# O detalhe que muda o nome de uma exportação semanal

A rotina precisa produzir `orders-2020-W53.csv` para 1.º de janeiro de 2021. Usar o ano civil no nome dá um resultado incompatível com a regra de semana ISO.

## Comece com um resultado verificável

A tarefa do exemplo é adicionar `weekly_filename(day)` com ano e semana ISO. O argumento `date(2021, 1, 1)` precisa devolver `orders-2020-W53.csv`. Aquele dia pertence à última semana ISO de 2020, embora esteja no ano civil de 2021. Esse caso expõe implementações que juntam `day.year` com uma semana calculada à parte.

| Função | Entrada de referência | Saída esperada |
| --- | --- | --- |
| `daily_filename` | 7 de junho de 2026 | `orders-2026-06-07.csv` |
| `hourly_filename` | Mesmo dia, hora 2 | `orders-2026-06-07-02.csv` |
| `weekly_filename` | 1.º de janeiro de 2021 | `orders-2020-W53.csv` |

## Investigue em Plan Mode

Entre na pasta `examples` e execute `claude --permission-mode plan` em uma sessão interativa. O modo permite explorar o projeto e preparar um plano antes de editar os arquivos do workspace. O cliente apresenta o plano para revisão e oferece as opções de permissão da etapa seguinte. Leia os comandos que a ferramenta propõe e selecione as permissões adequadas ao seu projeto. [Modos de permissão do Claude Code](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode).

Peça ao agente que cite as funções que já existem, proponha os arquivos afetados e descreva os testes. Um plano para o exemplo precisa manter os dois formatos existentes, usar o ano retornado por `date.isocalendar()` e cobrir a fronteira de ano. Devolva o plano para ajuste se ele tentar renomear os arquivos antigos.

## Experimente no seu projeto de estudo

No Plan Mode do Claude Code, peça ao agente os arquivos afetados e os casos de teste antes da edição. Revise se ele mantém os nomes diário e horário. Depois compare o diff e rode a suíte.

Uma boa revisão começa quando alguém consegue dizer o que deve continuar funcionando.

[Guia, exemplo e comandos no GitHub](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0007_claude_code_plan_mode)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
