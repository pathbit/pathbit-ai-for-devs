#!/usr/bin/env python3
"""Mede o perfil de consumo real de um agente a partir do historico do Claude Code.

Le APENAS os campos numericos de `usage`, o `message.id` e o `timestamp`.
Nenhum conteudo de conversa e lido, agregado ou impresso.

Cuidado que muda o resultado: uma unica resposta da API costuma ser gravada em
VARIAS linhas `type: "assistant"` (texto + cada bloco de ferramenta), todas com
o mesmo `message.id` e o mesmo objeto `usage`. Contar linhas infla requisicoes e
tokens em mais de 2x -- na maquina deste artigo, 34.481 linhas para 16.007 ids
distintos (razao 2,15, medida em 2026-09-12). Aqui cada `message.id` conta uma vez.

Os numeros impressos aqui alimentam as constantes de `sizing.py` e a secao
"Quantas Contas para Quantos Desenvolvedores" do artigo. Rode no SEU ambiente:
o perfil de uma maquina que orquestra subagentes nao e o de quem usa a CLI de
forma interativa.
"""

import glob
import json
import os
import statistics
from datetime import datetime, timedelta

HISTORY_ROOT = os.path.expanduser("~/.claude/projects")
IDLE_GAP = timedelta(minutes=20)   # lacuna que encerra uma "hora ativa"
MIN_TURNS_PER_SESSION = 10         # sessao curta demais nao diz nada sobre ritmo
MIN_ACTIVE_SECONDS = 300


def read_session(path, census=None):
    """Devolve os turnos unicos de um arquivo de sessao, ordenados no tempo.

    Quando `census` e passado, contabiliza nele as linhas brutas e os
    `message.id` distintos do historico INTEIRO -- antes de qualquer filtro de
    sessao -- para que a razao de deduplicacao impressa no fim seja reproduzivel
    pelo leitor, e nao um numero de origem externa.
    """
    turns = {}
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if '"usage"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                if record.get("type") != "assistant":
                    continue
                message = record.get("message") or {}
                usage = message.get("usage") or {}
                if not isinstance(usage, dict):
                    continue
                fresh_input = usage.get("input_tokens") or 0
                cache_write = usage.get("cache_creation_input_tokens") or 0
                cache_read = usage.get("cache_read_input_tokens") or 0
                output = usage.get("output_tokens") or 0
                if fresh_input + cache_write + cache_read + output <= 0:
                    continue
                try:
                    when = datetime.fromisoformat(
                        str(record.get("timestamp")).replace("Z", "+00:00")
                    )
                except Exception:
                    continue
                # Censo bruto: conta a linha e o id ANTES do filtro de sessao.
                if census is not None:
                    census["lines"] += 1
                    if message.get("id"):
                        census["ids"].add(message["id"])
                # Deduplicacao: uma resposta da API = um message.id, nao uma linha.
                # Entre as linhas que repetem o id, fica a de maior contagem: as
                # primeiras podem trazer `output_tokens` ainda parcial.
                message_id = message.get("id") or f"{path}:{when.isoformat()}"
                candidate = (when, fresh_input + cache_write, output, cache_read)
                previous = turns.get(message_id)
                if previous is None or sum(candidate[1:]) > sum(previous[1:]):
                    turns[message_id] = candidate
    except Exception:
        return []
    return sorted(turns.values(), key=lambda t: t[0])


def active_seconds(turns):
    """Tempo em que o agente esteve de fato requisitando, ignorando pausas longas."""
    total = 0.0
    for previous, current in zip(turns, turns[1:]):
        delta = current[0] - previous[0]
        if timedelta(0) <= delta <= IDLE_GAP:
            total += delta.total_seconds()
    return total


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    index = int(round(fraction * (len(ordered) - 1)))
    return ordered[max(0, min(len(ordered) - 1, index))]


def main():
    billable_input, output_tokens, cached_input, total_input = [], [], [], []
    request_rates, session_spans = [], []
    grand_billable = grand_output = grand_cached = grand_turns = 0

    # Censo do historico inteiro, para a razao de deduplicacao do fim.
    census = {"lines": 0, "ids": set()}

    pattern = os.path.join(HISTORY_ROOT, "**", "*.jsonl")
    for session_path in glob.glob(pattern, recursive=True):
        turns = read_session(session_path, census)
        if len(turns) < MIN_TURNS_PER_SESSION:
            continue
        elapsed = active_seconds(turns)
        if elapsed < MIN_ACTIVE_SECONDS:
            continue
        count = len(turns)
        billable_input.append(sum(t[1] for t in turns) / count)
        output_tokens.append(sum(t[2] for t in turns) / count)
        cached_input.append(sum(t[3] for t in turns) / count)
        total_input.append(sum(t[1] + t[3] for t in turns) / count)
        request_rates.append(count / (elapsed / 3600.0))
        session_spans.append((turns[0][0], turns[-1][0]))
        grand_billable += sum(t[1] for t in turns)
        grand_output += sum(t[2] for t in turns)
        grand_cached += sum(t[3] for t in turns)
        grand_turns += count

    if not request_rates:
        print("Nenhuma sessao com historico suficiente em " + HISTORY_ROOT)
        print("Use o Claude Code por algumas horas e rode de novo.")
        return

    print(f"sessoes analisadas                          : {len(request_rates)}")
    print(f"turnos unicos (dedup por message.id)        : {grand_turns}")
    print(f"T_in  entrada que conta p/ ITPM  mediana    : {statistics.median(billable_input):.0f}")
    print(f"T_in  entrada que conta p/ ITPM  p90        : {percentile(billable_input, 0.90):.0f}")
    print(f"T_out saida                      mediana    : {statistics.median(output_tokens):.0f}")
    print(f"T_out saida                      p90        : {percentile(output_tokens, 0.90):.0f}")
    print(f"T_cache leitura de cache         mediana    : {statistics.median(cached_input):.0f}")
    print(f"T_tot entrada total (conta+cache) mediana   : {statistics.median(total_input):.0f}")
    print(f"T_tot entrada total (conta+cache) p90       : {percentile(total_input, 0.90):.0f}")
    print(f"R_h   requisicoes por hora ativa mediana    : {statistics.median(request_rates):.0f}")
    print(f"R_h   requisicoes por hora ativa p90        : {percentile(request_rates, 0.90):.0f}")
    total_all = grand_billable + grand_output + grand_cached
    print(f"fracao de leitura de cache no total         : {grand_cached / total_all * 100:.1f}%")
    print("razao entrada total / entrada que conta     : "
          f"{statistics.median(total_input) / statistics.median(billable_input):.1f}x")

    # Concorrencia: quantas sessoes se sobrepoem no tempo. Numa maquina de um
    # unico operador isto mede paralelismo de subagentes, nao concorrencia de time.
    events = []
    for start, end in session_spans:
        events.append((start, 1))
        events.append((end, -1))
    events.sort()
    open_sessions = peak = 0
    for _, delta in events:
        open_sessions += delta
        peak = max(peak, open_sessions)
    print(f"pico de sessoes simultaneas                 : {peak}")

    # A razao que justifica a deduplicacao. Vem do historico INTEIRO, antes do
    # filtro de sessao -- por isso a contagem de ids aqui e bem maior que a de
    # "turnos unicos" acima, que so olha sessoes longas o bastante para medir
    # ritmo. Quem conta linha em vez de id infla consumo por este fator.
    distinct_ids = len(census["ids"])
    print("\n-- censo de deduplicacao (historico inteiro, antes do filtro)")
    print(f"linhas 'assistant' com usage                : {census['lines']}")
    print(f"ids distintos (message.id)                  : {distinct_ids}")
    if distinct_ids:
        print("razao linhas / ids                          : "
              f"{census['lines'] / distinct_ids:.2f}x")


if __name__ == "__main__":
    main()
