"""gera os cards redondos dos projetos (assets/projetos/) e das skills (assets/skills/), no tema claro e no escuro.

uso: python scripts/cards.py
"""
import base64, textwrap, urllib.request
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FONTE = base64.b64encode((RAIZ / 'assets' / 'fonts' / 'stix-two-text-bold-italic.woff2').read_bytes()).decode()

PROJETOS = [
    ('taubate', 'taubaté esportes',
     'portal que dá visibilidade a modalidades de taubaté que quase não aparecem na mídia local: handebol, tênis de mesa e vôlei.',
     'react.js · javascript · tailwind css'),
    ('he4rt-quiz', 'he4rt quiz',
     'bot de discord que manda uma pergunta por dia sobre tecnologia para a comunidade he4rt developers.',
     'python · discord'),
    ('f1', 'fórmula 1 — lights out',
     'site sobre fórmula 1 que liga o motor: um v6 turbo-híbrido sintetizado no navegador, que ronca conforme você rola a página.',
     'html · css · javascript'),
    ('buzina', 'buzina de bibi',
     'meu portfólio, com tema claro e escuro e uma buzina que funciona de verdade.',
     'html · css · javascript'),
]

TEMAS = {
    'dark': dict(bg='#09090c', borda='#1d1d23', tx='#f5f1f0', mu='#968e93', ac='#e10600'),
    'light': dict(bg='#ffffff', borda='#e4dcff', tx='#1c0f3a', mu='#5f5380', ac='#6d28d9'),
}

L, A = 420, 210


def card(titulo, desc, stack, tema):
    t = TEMAS[tema]
    linhas = textwrap.wrap(desc, 46)
    corpo = ''.join(f'<tspan x="30" dy="{0 if i == 0 else 21}">{escape(l)}</tspan>' for i, l in enumerate(linhas))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{L}" height="{A}" viewBox="0 0 {L} {A}" role="img" aria-label="{escape(titulo)}: {escape(desc)}">
<style>
@font-face{{font-family:buzina;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{FONTE}) format("woff2")}}
text{{font-family:buzina,"STIX Two Text",Georgia,serif;font-weight:700;font-style:italic}}
.t{{font-size:21px;fill:{t["tx"]}}} .d{{font-size:14.5px;fill:{t["mu"]}}} .s{{font-size:13px;fill:{t["ac"]}}} .seta{{font-size:18px;fill:{t["ac"]}}}
.conteudo{{opacity:0;animation:sobe .7s cubic-bezier(.2,.8,.2,1) .1s forwards}}
.ponto{{animation:pisca 2.4s ease-in-out infinite}}
@keyframes sobe{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
@keyframes pisca{{50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{.conteudo{{animation:none;opacity:1}}.ponto{{animation:none}}}}
</style>
<rect x=".5" y=".5" width="{L - 1}" height="{A - 1}" rx="28" fill="{t["bg"]}" stroke="{t["borda"]}"/>
<g class="conteudo">
<circle class="ponto" cx="36" cy="38" r="5" fill="{t["ac"]}"/>
<text class="seta" x="{L - 30}" y="44" text-anchor="end">↗</text>
<text class="t" x="30" y="78">{escape(titulo)}</text>
<text class="d" y="110">{corpo}</text>
<text class="s" x="30" y="{A - 26}">{escape(stack)}</text>
</g>
</svg>'''


SKILLS = [
    ('front-end', 'front-end', ['html', 'css', 'js', 'react', 'tailwind']),
    ('back-end', 'back-end', ['php', 'mysql', 'python']),
    ('ferramentas', 'ferramentas', ['git', 'github', 'figma', 'vscode', 'npm']),
]

LS, AS, ICONE, VAO = 280, 132, 40, 8


def icone(nome, tema):
    url = f'https://skillicons.dev/icons?i={nome}&theme={tema}'
    req = urllib.request.Request(url, headers={'User-Agent': 'buzina-cards'})
    return base64.b64encode(urllib.request.urlopen(req).read()).decode()


def card_skill(titulo, icones, tema):
    t = TEMAS[tema]
    largura = len(icones) * ICONE + (len(icones) - 1) * VAO
    x0 = (LS - largura) / 2
    imgs = ''.join(
        f'<image class="i" style="animation-delay:{.15 + i * .08:.2f}s" x="{x0 + i * (ICONE + VAO):.1f}" y="62" '
        f'width="{ICONE}" height="{ICONE}" href="data:image/svg+xml;base64,{icone(n, tema)}"><title>{n}</title></image>'
        for i, n in enumerate(icones))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{LS}" height="{AS}" viewBox="0 0 {LS} {AS}" role="img" aria-label="{titulo}: {", ".join(icones)}">
<style>
@font-face{{font-family:buzina;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{FONTE}) format("woff2")}}
text{{font-family:buzina,"STIX Two Text",Georgia,serif;font-weight:700;font-style:italic;font-size:19px;fill:{t["tx"]}}}
.i{{opacity:0;transform-box:fill-box;transform-origin:center;animation:entra .5s cubic-bezier(.2,.8,.2,1.3) forwards}}
@keyframes entra{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.i{{animation:none;opacity:1}}}}
</style>
<rect x=".5" y=".5" width="{LS - 1}" height="{AS - 1}" rx="28" fill="{t["bg"]}" stroke="{t["borda"]}"/>
<text x="{LS / 2}" y="42" text-anchor="middle">{escape(titulo)}</text>
{imgs}
</svg>'''


CONTATOS = [
    ('portfolio', 'portfólio', 'portfolio', 158),
    ('linkedin', 'linkedin', 'linkedin', 150),
    ('instagram', 'instagram', 'instagram', 162),
]

# marcas desenhadas numa caixa de 24×24, em branco sobre o círculo da cor da marca
MARCAS = {
    'linkedin': ('#0a66c2', '''<g fill="#fff" transform="translate(-1.6 0)"><circle cx="8" cy="6.9" r="1.95"/><rect x="6.3" y="10" width="3.4" height="8.6" rx=".5"/>
<path d="M11.6 10h3.2v1.5c.6-1 1.7-1.8 3.3-1.8 2.6 0 3.6 1.7 3.6 4.4v4.5h-3.3v-4c0-1.2-.4-2-1.5-2-1.2 0-1.8.9-1.8 2v4h-3.5z"/></g>'''),
    'instagram': ('url(#ig)', '''<g fill="none" stroke="#fff" stroke-width="1.9"><rect x="5" y="5" width="14" height="14" rx="4.3"/><circle cx="12" cy="12" r="3.3"/></g>
<circle cx="16.1" cy="7.9" r="1.1" fill="#fff"/>'''),
    'portfolio': (None, '''<g fill="none" stroke="#fff" stroke-width="1.7"><circle cx="12" cy="12" r="7"/><ellipse cx="12" cy="12" rx="3" ry="7"/><path d="M5 12h14"/></g>'''),
}

R = 18


def pilula(texto, marca, largura, tema):
    t = TEMAS[tema]
    cor, desenho = MARCAS[marca]
    cor = cor or t['ac']
    s = 2 * R / 24
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="52" viewBox="0 0 {largura} 52" role="img" aria-label="{escape(texto)}">
<defs><radialGradient id="ig" cx="30%" cy="107%" r="150%"><stop offset="0" stop-color="#fdf497"/><stop offset=".05" stop-color="#fdf497"/><stop offset=".45" stop-color="#fd5949"/><stop offset=".6" stop-color="#d6249f"/><stop offset=".9" stop-color="#285aeb"/></radialGradient></defs>
<style>
@font-face{{font-family:buzina;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{FONTE}) format("woff2")}}
text{{font-family:buzina,"STIX Two Text",Georgia,serif;font-weight:700;font-style:italic;font-size:19px;fill:{t["tx"]}}}
</style>
<rect x=".5" y=".5" width="{largura - 1}" height="51" rx="26" fill="{t["bg"]}" stroke="{t["borda"]}"/>
<circle cx="26" cy="26" r="{R}" fill="{cor}"/>
<g transform="translate({26 - R} {26 - R}) scale({s:.4f})">{desenho}</g>
<text x="54" y="32">{escape(texto)}</text>
</svg>'''


def main():
    pasta = RAIZ / 'assets' / 'projetos'
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, titulo, desc, stack in PROJETOS:
        (pasta / f'{nome}.svg').write_text(card(titulo, desc, stack, 'light'), encoding='utf-8')
        (pasta / f'{nome}-dark.svg').write_text(card(titulo, desc, stack, 'dark'), encoding='utf-8')
    skills = RAIZ / 'assets' / 'skills'
    skills.mkdir(parents=True, exist_ok=True)
    for nome, titulo, icones in SKILLS:
        (skills / f'{nome}.svg').write_text(card_skill(titulo, icones, 'light'), encoding='utf-8')
        (skills / f'{nome}-dark.svg').write_text(card_skill(titulo, icones, 'dark'), encoding='utf-8')
    contato = RAIZ / 'assets' / 'contato'
    contato.mkdir(parents=True, exist_ok=True)
    for nome, texto, ic, largura in CONTATOS:
        (contato / f'{nome}.svg').write_text(pilula(texto, ic, largura, 'light'), encoding='utf-8')
        (contato / f'{nome}-dark.svg').write_text(pilula(texto, ic, largura, 'dark'), encoding='utf-8')
    print(f'{len(PROJETOS)} cards de projeto e {len(SKILLS)} de skills gerados')


if __name__ == '__main__':
    main()
