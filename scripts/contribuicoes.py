"""gera o mini-gráfico animado de contribuições (de julho em diante) em svg.

uso: python scripts/contribuicoes.py <usuario> <pasta-de-saida>
com GITHUB_TOKEN usa a api graphql; sem token, lê a página pública de contribuições.
"""
import base64, datetime as dt, json, os, re, sys, urllib.request
from pathlib import Path

INICIO = dt.date(2026, 7, 1)
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
FONTE = Path(__file__).resolve().parent.parent / 'assets' / 'fonts' / 'stix-two-text-bold-italic.woff2'

TEMAS = {
    'dark': dict(bg='#09090c', borda='#17171c', tx='#f5f1f0', mu='#968e93',
                 niveis=['#16161b', '#4a0200', '#7a0400', '#b30500', '#e10600']),
    'light': dict(bg='#ffffff', borda='#ece6ff', tx='#1c0f3a', mu='#5f5380',
                  niveis=['#f1edfb', '#ddd6fe', '#c4b5fd', '#a78bfa', '#6d28d9']),
}


def via_graphql(usuario, token, hoje):
    q = '''query($u:String!,$de:DateTime!,$ate:DateTime!){user(login:$u){contributionsCollection(from:$de,to:$ate){
      contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}'''
    corpo = json.dumps({'query': q, 'variables': {
        'u': usuario, 'de': f'{INICIO}T00:00:00Z', 'ate': f'{hoje}T23:59:59Z'}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', data=corpo, headers={
        'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    dados = json.load(urllib.request.urlopen(req))
    semanas = dados['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    return {dt.date.fromisoformat(d['date']): d['contributionCount'] for s in semanas for d in s['contributionDays']}


def via_pagina(usuario, hoje):
    url = f'https://github.com/users/{usuario}/contributions?from={INICIO}&to={hoje}'
    html = urllib.request.urlopen(url).read().decode('utf-8')
    ids = dict(re.findall(r'data-date="([\d-]+)" id="([^"]+)"', html))
    dicas = {}
    for alvo, texto in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r'(\d+)', texto)
        dicas[alvo] = int(n.group(1)) if n else 0
    return {dt.date.fromisoformat(d): dicas.get(i, 0) for d, i in ids.items()}


def nivel(n, maximo):
    if n == 0:
        return 0
    return min(4, 1 + int(3 * (n - 1) / max(1, maximo - 1))) if maximo > 1 else 4


def svg(dias, hoje, tema):
    t = TEMAS[tema]
    fonte = base64.b64encode(FONTE.read_bytes()).decode()
    # a grade começa no domingo da semana de INICIO
    comeco = INICIO - dt.timedelta(days=(INICIO.weekday() + 1) % 7)
    n_semanas = (hoje - comeco).days // 7 + 1
    cel, gap, x0, y0 = 10, 3, 18, 44
    largura = x0 * 2 + n_semanas * (cel + gap) - gap
    altura = y0 + 7 * (cel + gap) + 14
    total = sum(n for d, n in dias.items() if INICIO <= d <= hoje)
    maximo = max([n for d, n in dias.items() if INICIO <= d <= hoje] or [0])

    celulas, meses, vistos = [], [], set()
    for s in range(n_semanas):
        for dw in range(7):
            d = comeco + dt.timedelta(days=s * 7 + dw)
            if d < INICIO or d > hoje:
                continue
            n = dias.get(d, 0)
            x, y = x0 + s * (cel + gap), y0 + dw * (cel + gap)
            atraso = s * 0.06 + dw * 0.015
            classe = ' class="hoje"' if d == hoje else ''
            celulas.append(
                f'<rect{classe} x="{x}" y="{y}" width="{cel}" height="{cel}" rx="3" '
                f'fill="{t["niveis"][nivel(n, maximo)]}" style="animation-delay:{atraso:.2f}s">'
                f'<title>{n} em {d.day} de {MESES[d.month - 1]}</title></rect>')
            if d.month not in vistos:
                vistos.add(d.month)
                meses.append(f'<text class="mes" x="{x}" y="{y0 - 8}">{MESES[d.month - 1]}</text>')

    rotulo = 'contribuição' if total == 1 else 'contribuições'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}" role="img" aria-label="{total} {rotulo} de julho em diante">
<style>
@font-face{{font-family:buzina;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{fonte}) format("woff2")}}
text{{font-family:buzina,"STIX Two Text",Georgia,serif;font-weight:700;font-style:italic}}
.titulo{{font-size:13px;fill:{t["mu"]}}} .total{{fill:{t["niveis"][4]}}} .mes{{font-size:10px;fill:{t["mu"]}}}
g.grade rect{{opacity:0;transform-box:fill-box;transform-origin:center;animation:entra .45s cubic-bezier(.2,.8,.2,1.3) forwards}}
g.grade rect.hoje{{animation:entra .45s cubic-bezier(.2,.8,.2,1.3) forwards,pulsa 1.6s ease-in-out 2s infinite}}
@keyframes entra{{from{{opacity:0;transform:scale(.2)}}to{{opacity:1;transform:scale(1)}}}}
@keyframes pulsa{{50%{{opacity:.45}}}}
@media (prefers-reduced-motion:reduce){{g.grade rect{{animation:none;opacity:1}}}}
</style>
<rect width="{largura}" height="{altura}" rx="18" fill="{t["bg"]}" stroke="{t["borda"]}"/>
<text class="titulo" x="{x0}" y="22"><tspan class="total">{total}</tspan> {rotulo} de julho em diante</text>
{"".join(meses)}
<g class="grade">{"".join(celulas)}</g>
</svg>'''


def main():
    usuario, saida = sys.argv[1], Path(sys.argv[2])
    hoje = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date()
    token = os.environ.get('GITHUB_TOKEN')
    dias = via_graphql(usuario, token, hoje) if token else via_pagina(usuario, hoje)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / 'contribuicoes.svg').write_text(svg(dias, hoje, 'light'), encoding='utf-8')
    (saida / 'contribuicoes-dark.svg').write_text(svg(dias, hoje, 'dark'), encoding='utf-8')
    print(f'{sum(n for d, n in dias.items() if d >= INICIO)} contribuições desde {INICIO}')


if __name__ == '__main__':
    main()
