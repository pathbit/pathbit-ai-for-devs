#!/usr/bin/env bash
# Validacao HTTP dos dois paineis, contra as rotas que existem de verdade.
#
# Exigencias do usuario que este script comprova:
#   - nenhum 403/503 ao acionar os botoes das telas DEPOIS de trocar a senha;
#   - nenhuma credencial visivel em corpo de resposta, inclusive no 401, que e
#     o que o navegador mostra quando se aperta ESC no dialogo do Basic Auth;
#   - token de OAuth nunca apresentado como "ilimitado".
#
# Nenhuma credencial e ecoada na saida: so o veredito de cada verificacao.
#
# Uso:
#   NOVE_USER=admin NOVE_PASS=<atual> NOVE_NOVA=<nova> \
#   OMNI_USER=admin OMNI_PASS=<atual> OMNI_NOVA=<nova> \
#   tools/valida_paineis.sh
#
# ATENCAO: o script TROCA a senha do painel como parte da verificacao -- e
# justamente o caminho que ja quebrou antes. Ao terminar, a senha em vigor e a
# que foi passada em *_NOVA. Nao rode contra uma instalacao de producao sem
# saber disso.
#
# Enderecos: NOVE_URL e OMNI_URL, com o padrao das stacks dos artigos.
# Painel cuja senha vem de DASHBOARD_PASSWORD e detectado sozinho: nesse modo a
# troca pela tela tem de ser RECUSADA, e e isso que se verifica.

set -uo pipefail
FALHAS=0
TOTAL=0
CORPO=$(mktemp)
trap 'rm -f "$CORPO"' EXIT

ok()    { TOTAL=$((TOTAL+1)); printf '  ok    %-54s %s\n' "$1" "${2:-}"; }
falha() { TOTAL=$((TOTAL+1)); FALHAS=$((FALHAS+1)); printf '  FALHA %-54s %s\n' "$1" "${2:-}"; }

verifica() { [ "$2" = "$3" ] && ok "$1" "$3" || falha "$1" "esperado=$2 obtido=$3"; }

aceitavel() {  # aceitavel <descricao> <codigo> — recusa explicitamente 4xx/5xx
  case "$2" in
    200|302|303) ok "$1" "$2" ;;
    403|503) falha "$1" "$2 <- exatamente o que nao pode acontecer" ;;
    *) falha "$1" "$2" ;;
  esac
}

nao_contem() {
  if grep -qiE "$3" "$2"; then falha "$1" "encontrou padrao proibido"; else ok "$1" "limpo"; fi
}

req() {  # req <metodo> <url> <cred> [dados] -> imprime o codigo, corpo em $CORPO
  local metodo="$1" url="$2" cred="$3" dados="${4:-}"
  local origem="${url%%/*}//${url#*//}"; origem="${url%%"${url#*://*/}"}"; origem="${origem%/}"
  local args=(-s -o "$CORPO" -w '%{http_code}' -X "$metodo" --max-time 20)
  [ -n "$cred" ] && args+=(-u "$cred")
  if [ -n "$dados" ]; then
    args+=(--data "$dados" -H 'Content-Type: application/x-www-form-urlencoded')
  fi
  # Origin coerente: e o que o navegador envia num POST da propria pagina.
  args+=(-H "Origin: $origem" -H "Sec-Fetch-Site: same-origin")
  curl "${args[@]}" "$url"
}

botoes() {  # botoes <base> <cred> <rotulo>
  local base="$1" cred="$2" rotulo="$3"
  for acao in /acoes/atualizar /acoes/sincronizar /acoes/cron /acoes/testar-gateway; do
    aceitavel "POST $acao $rotulo" "$(req POST "$base$acao" "$cred" "x=1")"
  done
  aceitavel "POST /acoes/idioma $rotulo" "$(req POST "$base/acoes/idioma" "$cred" "idioma=pt")"
  for api in /api/sync /api/test-gateway /api/cron-run; do
    aceitavel "POST $api $rotulo" "$(req POST "$base$api" "$cred" "{}")"
  done
}

painel() {  # painel <nome> <base> <usuario> <senha> <senha_nova>
  local nome="$1" base="$2" usuario="$3" senha="$4" nova="$5"
  local cred="$usuario:$senha"
  echo
  echo "=============== $nome ($base) ==============="

  echo "-- publico --"
  verifica "GET /healthz" 200 "$(req GET "$base/healthz" "")"
  verifica "GET / sem credencial (o que o ESC mostra)" 401 "$(req GET "$base/" "")"
  nao_contem "  o 401 nao ensina a credencial" "$CORPO" \
    "admin *[/:] *[a-z0-9]|senha padr|default password|pathbit-?2|credenciais padr"
  verifica "GET /credenciais-atualizadas sem auth" 200 "$(req GET "$base/credenciais-atualizadas" "")"
  verifica "GET / com senha errada" 401 "$(req GET "$base/" "$usuario:errada-x9")"

  echo "-- autenticado --"
  for rota in / /index.html /api/status /api/cron-status; do
    verifica "GET $rota" 200 "$(req GET "$base$rota" "$cred")"
  done

  echo "-- botoes com a senha atual --"
  botoes "$base" "$cred" "(senha atual)"

  echo "-- conteudo da pagina --"
  req GET "$base/" "$cred" >/dev/null
  nao_contem "  sem token/chave no HTML" "$CORPO" \
    "ya29\.|1//[A-Za-z0-9_-]{20}|sk-[A-Za-z0-9]{20}|pbkdf2_sha256\\\$"
  nao_contem "  OAuth nunca aparece como ilimitado" "$CORPO" "unlimited|ilimitad"
  req GET "$base/api/status" "$cred" >/dev/null
  # Procura VALOR de segredo, nao nome de campo: "hasApiKey": false e
  # justamente o projeto correto (campo projetado, nunca a linha crua).
  nao_contem "  /api/status sem segredo" "$CORPO" \
    "\"(access|refresh)_?[Tt]oken\" *: *\"|\"api_?[Kk]ey\" *: *\"|ya29\.|sk-[A-Za-z0-9]{20}"

  echo "-- cabecalhos em toda resposta --"
  for alvo in "/:$cred" "/:" "/credenciais-atualizadas:"; do
    local rota="${alvo%%:*}" c="${alvo#*:}"
    local h
    if [ -n "$c" ]; then h=$(curl -s -D - -o /dev/null -u "$c" --max-time 20 "$base$rota")
    else h=$(curl -s -D - -o /dev/null --max-time 20 "$base$rota"); fi
    for cab in X-Content-Type-Options X-Frame-Options Content-Security-Policy Referrer-Policy; do
      grep -qi "^$cab:" <<<"$h" && ok "$cab em $rota${c:+ (auth)}" || falha "$cab em $rota${c:+ (auth)}" "ausente"
    done
  done

  echo "-- CSRF: POST de outra origem tem de ser recusado --"
  local c_cross
  c_cross=$(curl -s -o "$CORPO" -w '%{http_code}' -u "$cred" --max-time 20 \
    -H "Origin: https://exemplo-malicioso.invalid" -H "Sec-Fetch-Site: cross-site" \
    --data "idioma=en" "$base/acoes/idioma")
  if [ "$c_cross" = "303" ] && grep -q "tom=danger" <<<"$(curl -s -D - -o /dev/null -u "$cred" \
      -H "Origin: https://exemplo-malicioso.invalid" -H "Sec-Fetch-Site: cross-site" \
      --data "idioma=en" "$base/acoes/idioma" | tr -d '\r')"; then
    ok "POST de origem estranha recusado" "303 -> aviso"
  else
    falha "POST de origem estranha recusado" "obtido=$c_cross"
  fi

  # Quando a senha vem de DASHBOARD_PASSWORD, o ambiente e a fonte da verdade
  # e a troca pela tela NAO pode valer -- senao a stack subiria de novo com a
  # senha do compose e o operador acharia que trocou. O painel tem de recusar
  # com aviso, e e isso que se verifica aqui.
  local cabecalho_troca
  cabecalho_troca=$(curl -s -D - -o /dev/null -u "$cred" --max-time 20 \
    --data "user=$usuario&password=$nova" "$base/acoes/credenciais" | tr -d '\r')
  if grep -qiE "variavel[+ ]de[+ ]ambiente" <<<"$cabecalho_troca"; then
    echo "-- senha vem do ambiente: a troca pela tela tem de ser recusada --"
    ok "troca recusada com aviso" "303 -> aviso de ambiente"
    verifica "  a senha do ambiente continua valendo" 200 "$(req GET "$base/" "$cred")"
    verifica "  a senha tentada nao passou a valer" 401 "$(req GET "$base/" "$usuario:$nova")"
    botoes "$base" "$cred" "(senha do ambiente)"
    return 0
  fi

  echo "-- troca de senha e, em seguida, os botoes de novo --"
  # A propria sondagem acima ja foi o POST de troca: repeti-lo com a senha
  # antiga daria 401 depois que a troca surtiu efeito.
  aceitavel "POST /acoes/credenciais" "$(sed -n '1s/.* \([0-9][0-9][0-9]\) .*/\1/p' <<<"$(head -1 <<<"$cabecalho_troca")")"
  # A senha antiga tem de parar de valer, e a nova tem de abrir tudo.
  # Excecao de projeto: a credencial de recuperacao continua valendo depois da
  # troca — e justamente o break-glass, seria inutil se caducasse aqui.
  if [ "${QUEBRA_VIDRO:-0}" = "1" ]; then
    verifica "  recuperacao segue valendo (break-glass)" 200 "$(req GET "$base/" "$cred")"
  else
    verifica "  senha antiga deixou de valer" 401 "$(req GET "$base/" "$cred")"
  fi
  verifica "  senha nova abre o painel" 200 "$(req GET "$base/" "$usuario:$nova")"
  botoes "$base" "$usuario:$nova" "(senha nova)"

  echo "-- senha fraca tem de ser recusada --"
  local c_fraca
  c_fraca=$(req POST "$base/acoes/credenciais" "$usuario:$nova" \
    "user=$usuario&password=abc")
  aceitavel "POST /acoes/credenciais (senha fraca)" "$c_fraca"
  verifica "  a senha fraca nao passou a valer" 401 "$(req GET "$base/" "$usuario:abc")"
  verifica "  a senha forte continua valendo" 200 "$(req GET "$base/" "$usuario:$nova")"
}

# Enderecos configuraveis: o padrao e o das stacks dos artigos (9091 para o
# 9RTKSync do artigo 0003, 9092 para o OminiRTkSync), mas qualquer instalacao
# serve passando NOVE_URL / OMNI_URL.
NOVE_URL="${NOVE_URL:-http://127.0.0.1:9091}"
OMNI_URL="${OMNI_URL:-http://127.0.0.1:9092}"

QUEBRA_VIDRO="${NOVE_QUEBRA_VIDRO:-0}"
painel "9RTKSync (router-sync)" "$NOVE_URL" "$NOVE_USER" "$NOVE_PASS" "$NOVE_NOVA"
QUEBRA_VIDRO="${OMNI_QUEBRA_VIDRO:-0}"
painel "OminiRTkSync"           "$OMNI_URL" "$OMNI_USER" "$OMNI_PASS" "$OMNI_NOVA"

echo
echo "===================================================="
echo "verificacoes: $TOTAL   falhas: $FALHAS"
exit $((FALHAS > 0))
