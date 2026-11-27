# Exercício de plan Mode no Claude Code

O [código inicial](src/reports.py) contém nomes de exportação diária e horária. Os [testes iniciais](tests/test_reports.py) protegem ambos os formatos. Para comparar o diff em um diretório independente, copie esta pasta para um local temporário, execute `git init`, adicione `src` e `tests` e crie um commit inicial com a identidade Git já configurada.

## Prompt para planejar

```text
Leia src/reports.py e os testes. Planeje adicionar weekly_filename(day)
usando ano e semana ISO. date(2021, 1, 1) deve renderizar
orders-2020-W53.csv. Preserve as funções diária e horária.

Indique arquivos, riscos de compatibilidade e os testes que rodaria.

Aguarde minha revisão do plano antes da implementação.

```

O plano deve prever `date.isocalendar()` e cobrir a fronteira de ano. Após a implementação, execute `git diff -- src tests` e `python3 -m unittest discover -s tests -v`.
