#!/usr/bin/env python3
"""Resolve a formula de dimensionamento "licencas x desenvolvedores".

Toda constante daqui tem origem declarada. Troque as do bloco PROFILES pelas que
`measure_agent_usage.py` imprimir na SUA maquina -- as que vem de fabrica sao de
um ambiente que orquestra subagentes, e inflam o resultado de quem usa a CLI de
forma interativa.

O que o script NAO faz: dizer quantos desenvolvedores cabem em uma assinatura.
Isso exigiria `C_janela`, a capacidade absoluta de uma licenca dentro da janela
de reset, e nenhum dos fornecedores publica esse numero. O script imprime a
demanda `D` com a unidade correta e deixa a divisao indicada.
"""

import math

# --- medido: perfil de UMA sessao ativa de agente ---
# [FONTE: src/measure_agent_usage.py, executado em 2026-09-12 sobre
#  ~/.claude/projects (114 sessoes, 6.731 turnos unicos apos dedup por message.id)]
PROFILES = {
    "mediana": {
        "rate_per_hour": 198,     # R_h   requisicoes por hora ativa
        "billable_input": 4066,   # T_in  entrada que conta para ITPM (sem cache lido)
        "output": 706,            # T_out saida
        "total_input": 88464,     # T_tot entrada total, cache lido incluso
    },
    "p90": {
        "rate_per_hour": 343,
        "billable_input": 8227,
        "output": 1361,
        "total_input": 303214,
    },
}

# --- publicado: teto por tier da API da Anthropic (Opus 5 / Sonnet 5) ---
# Vale para o caminho de CHAVE DE API, nao para assinatura Pro/Max.
# [FONTE: https://platform.claude.com/docs/en/api/rate-limits -- lido em 2026-09-12]
API_TIERS = {
    "Start": {"rpm": 1_000, "itpm": 2_000_000, "otpm": 400_000},
    "Build": {"rpm": 5_000, "itpm": 5_000_000, "otpm": 1_000_000},
    "Scale": {"rpm": 10_000, "itpm": 10_000_000, "otpm": 2_000_000},
}

TEAM_SIZES = [3, 12, 40]        # tamanhos de time usados nos exemplos
CONCURRENCY = [0.4, 0.6, 1.0]   # fator `c`: fracao do time requisitando ao mesmo tempo [A MEDIR]
SLACK = 0.30                    # folga `F`: decisao de operacao, nao medicao
WINDOW_HOURS = 5                # `W_h` da janela de assinatura Claude
# [FONTE: https://support.claude.com/en/articles/11049741-what-is-the-max-plan
#  -- lido em 2026-09-12: "usage limit will reset every five hours"]
# No Antigravity a janela observada e outra: "reset after 2h", e POR FAMILIA de
# modelo -- e uma linha de log deste artigo, nao um numero publicado pelo Google.
ANTIGRAVITY_WINDOW_HOURS = 2


def br(value, decimals=0):
    """Formata numero no padrao brasileiro: ponto no milhar, virgula no decimal."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def burst_demand(team_size, concurrency, profile, slack=SLACK):
    """Demanda por minuto -- e o teto que estoura antes do teto da janela."""
    simultaneous = team_size * concurrency
    rpm = simultaneous * profile["rate_per_hour"] / 60 * (1 + slack)
    return simultaneous, rpm, rpm * profile["billable_input"], rpm * profile["output"]


def smallest_tier(rpm, itpm, otpm):
    """Menor tier de API que cobre a rajada exigida."""
    for name, tier in API_TIERS.items():
        if rpm <= tier["rpm"] and itpm <= tier["itpm"] and otpm <= tier["otpm"]:
            return name
    return "acima de Scale"


def window_demand(team_size, concurrency, profile, window_hours, slack=SLACK):
    """Demanda dentro da janela, em TOKEN TOTAL (entrada cacheada inclusa)."""
    simultaneous = team_size * concurrency
    demand = (simultaneous * profile["rate_per_hour"]
              * (profile["total_input"] + profile["output"])
              * window_hours * (1 + slack))
    return simultaneous, demand


def main():
    print("### CAMINHO DE ASSINATURA (9Router / OmniRoute) -- C_janela e [A MEDIR]")
    print("Unidade: TOKEN TOTAL, com a leitura de cache inclusa. O medidor da")
    print("assinatura nao publica o que conta, entao nao da para descontar o cache.")
    print("D = U_sim * R_h * (T_tot + T_out) * W_h * (1 + F)\n")
    windows = (
        (WINDOW_HOURS, "janela de 5h, publicada (Claude)"),
        (ANTIGRAVITY_WINDOW_HOURS, "janela de 2h por familia, observada em log (Antigravity)"),
    )
    for window_hours, window_label in windows:
        print(f"-- {window_label}")
        for label, profile in PROFILES.items():
            for size in TEAM_SIZES:
                simultaneous, demand = window_demand(size, 0.6, profile, window_hours)
                print(f"   perfil {label:>7} | {size:>2} devs | c=0,6 | U_sim={br(simultaneous, 1):>4} | "
                      f"W={window_hours}h | D = {br(demand):>18} tok -> L = ceil(D / C_janela)")
        print()

    print("\n### VERIFICACAO DE RAJADA -- o teto por minuto estoura antes do teto da janela")
    for label, profile in PROFILES.items():
        print(f"\nperfil {label}: R_h={profile['rate_per_hour']} req/h, "
              f"T_in={profile['billable_input']} tok/req, T_out={profile['output']} tok/req, "
              f"folga={SLACK:.0%}")
        print(f"{'devs':>5} {'c':>5} {'U_sim':>6} {'RPM':>7} {'ITPM':>11} {'OTPM':>9}  tier de API")
        for size in TEAM_SIZES:
            for factor in CONCURRENCY:
                simultaneous, rpm, itpm, otpm = burst_demand(size, factor, profile)
                print(f"{size:>5} {br(factor, 1):>5} {br(simultaneous, 1):>6} {br(rpm):>7} "
                      f"{br(itpm):>11} {br(otpm):>9}  {smallest_tier(rpm, itpm, otpm)}")

    print("\n\n### FOLGA DA RAJADA contra UMA licenca de API no tier Start (1.000 rpm)")
    print("Serve de ordem de grandeza tambem para a assinatura: o que aperta e a")
    print("janela, nao o pico por minuto.")
    for size in TEAM_SIZES:
        _, rpm, _, _ = burst_demand(size, 0.6, PROFILES["mediana"])
        print(f"{size:>2} devs, c=0,6 -> pico exigido {br(rpm):>5} rpm; "
              f"Start cobre {math.floor(API_TIERS['Start']['rpm'] / rpm)}x a demanda")


if __name__ == "__main__":
    main()
