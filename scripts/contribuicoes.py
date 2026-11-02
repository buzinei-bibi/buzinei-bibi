"""gera a cobrinha que anda pela grade de contribuições (de julho em diante) e come os quadradinhos, em svg.

uso: python scripts/contribuicoes.py <usuario> <pasta-de-saida>
com GITHUB_TOKEN usa a api graphql; sem token, lê a página pública de contribuições.
"""
import base64, datetime as dt, json, os, re, sys, urllib.request
from pathlib import Path

INICIO = dt.date(2026, 7, 1)
PASSO = 0.11  # segundos por casa andada
TAMANHOS = [11, 9.5, 8, 6.5]  # cabeça → rabo
FOLGA = 16  # espaço transparente à esquerda, entre o texto e o card
MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
FONTE = Path(__file__).resolve().parent.parent / 'assets' / 'fonts' / 'stix-two-text-bold-italic.woff2'

TEMAS = {
    'dark': dict(bg='#09090c', borda='#17171c', tx='#f5f1f0', mu='#968e93',
                 niveis=['#16161b', '#4a0200', '#7a0400', '#b30500', '#e10600'], cobra='#ffb454'),
    'light': dict(bg='#ffffff', borda='#ece6ff', tx='#1c0f3a', mu='#5f5380',
                  niveis=['#f1edfb', '#ddd6fe', '#c4b5fd', '#a78bfa', '#6d28d9'], cobra='#a21caf'),
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


def rota(alvos, inicio, fim):
    """caminho casa a casa: vai sempre ao quadradinho colorido mais perto e depois sai pela direita."""
    caminho, atual, restantes = [inicio], inicio, set(alvos)
    while restantes:
        prox = min(restantes, key=lambda c: (abs(c[0] - atual[0]) + abs(c[1] - atual[1]), c))
        caminho += passos(atual, prox)
        atual = prox
        restantes.discard(prox)
    return caminho + passos(atual, fim)


def passos(a, b):
    (x, y), saida = a, []
    while (x, y) != b:
        if y != b[1]:
            y += 1 if b[1] > y else -1
        else:
            x += 1 if b[0] > x else -1
        saida.append((x, y))
    return saida


def svg(dias, hoje, tema):
    t = TEMAS[tema]
    fonte = base64.b64encode(FONTE.read_bytes()).decode()
    # a grade começa no domingo da semana de INICIO
    comeco = INICIO - dt.timedelta(days=(INICIO.weekday() + 1) % 7)
    n_semanas = (hoje - comeco).days // 7 + 1
    cel, gap, x0, y0 = 10, 3, 18, 30
    passo = cel + gap
    largura = x0 * 2 + n_semanas * passo - gap
    altura = y0 + 7 * passo + 15
    total = sum(n for d, n in dias.items() if INICIO <= d <= hoje)
    maximo = max([n for d, n in dias.items() if INICIO <= d <= hoje] or [0])

    casas, meses, vistos = {}, [], set()
    for s in range(n_semanas):
        for dw in range(7):
            d = comeco + dt.timedelta(days=s * 7 + dw)
            if d < INICIO or d > hoje:
                continue
            casas[(s, dw)] = (d, dias.get(d, 0))
            if d.month not in vistos:
                vistos.add(d.month)
                meses.append(f'<text class="mes" x="{x0 + s * passo}" y="{y0 - 8}">{MESES[d.month - 1]}</text>')

    alvos = [c for c, (_, n) in casas.items() if n > 0]
    caminho = rota(alvos, (-3, 0), (n_semanas + 3, 6))
    ciclo = (len(caminho) + len(TAMANHOS)) * PASSO + 1.5  # + uma pausa com a grade vazia
    pct = lambda i: 100 * i * PASSO / ciclo
    comida = {}
    for i, c in enumerate(caminho):
        comida.setdefault(c, i)

    celulas, quadros = [], []
    for (s, dw), (d, n) in casas.items():
        x, y = x0 + s * passo, y0 + dw * passo
        cor = t['niveis'][nivel(n, maximo)]
        anim = ''
        if n > 0:
            k = f'c{s}_{dw}'
            p = pct(comida[(s, dw)])
            quadros.append(f'@keyframes {k}{{0%,{p:.3f}%{{fill:{cor}}}{p + .01:.3f}%,99.9%{{fill:{t["niveis"][0]}}}100%{{fill:{cor}}}}}')
            anim = f' style="animation:{k} {ciclo:.2f}s linear infinite"'
        celulas.append(f'<rect x="{x}" y="{y}" width="{cel}" height="{cel}" rx="3" fill="{cor}"{anim}>'
                       f'<title>{n} em {d.day} de {MESES[d.month - 1]}</title></rect>')

    # um único trajeto; cada gomo segue a cabeça com atraso de um passo
    trajeto = ''.join(f'{pct(i):.3f}%{{transform:translate({x0 + cx * passo}px,{y0 + cy * passo}px)}}'
                      for i, (cx, cy) in enumerate(caminho))
    fim = caminho[-1]
    trajeto += f'100%{{transform:translate({x0 + fim[0] * passo}px,{y0 + fim[1] * passo}px)}}'
    gomos = ''.join(
        f'<rect class="gomo" x="{(cel - tam) / 2}" y="{(cel - tam) / 2}" width="{tam}" height="{tam}" rx="{tam / 2.6:.1f}" '
        f'style="animation-delay:{k * PASSO:.2f}s"/>'
        for k, tam in reversed(list(enumerate(TAMANHOS))))

    rotulo = 'contribuição' if total == 1 else 'contribuições'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura + FOLGA}" height="{altura}" viewBox="-{FOLGA} 0 {largura + FOLGA} {altura}" role="img" aria-label="cobrinha comendo minhas {total} {rotulo} de julho em diante">
<style>
@font-face{{font-family:buzina;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{fonte}) format("woff2")}}
text{{font-family:buzina,"STIX Two Text",Georgia,serif;font-weight:700;font-style:italic}}
.mes{{font-size:10px;fill:{t["mu"]}}}
.gomo{{fill:{t["cobra"]};transform:translate(-100px,0);animation:cobra {ciclo:.2f}s linear infinite backwards}}
@keyframes cobra{{{trajeto}}}
{"".join(quadros)}
@media (prefers-reduced-motion:reduce){{.gomo{{display:none}}rect{{animation:none!important}}}}
</style>
<clipPath id="card"><rect width="{largura}" height="{altura}" rx="18"/></clipPath>
<rect width="{largura}" height="{altura}" rx="18" fill="{t["bg"]}" stroke="{t["borda"]}"/>
{"".join(meses)}
<g>{"".join(celulas)}</g>
<g clip-path="url(#card)">{gomos}</g>
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
