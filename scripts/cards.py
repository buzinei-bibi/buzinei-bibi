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
    ('portfolio', 'portfólio', None, 132),
    ('linkedin', 'linkedin', 'linkedin', 136),
    ('instagram', 'instagram', 'instagram', 150),
]


def pilula(texto, ic, largura, tema):
    t = TEMAS[tema]
    if ic:
        marca = (f'<clipPath id="c"><circle cx="24" cy="22" r="13"/></clipPath>'
                 f'<image clip-path="url(#c)" x="11" y="9" width="26" height="26" href="data:image/svg+xml;base64,{icone(ic, tema)}"/>')
    else:
        marca = f'<circle cx="24" cy="22" r="6" fill="{t["ac"]}"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="44" viewBox="0 0 {largura} 44" role="img" aria-label="{escape(texto)}">
<style>
@font-face{{font-family:buzina;font-weight:700;font-style:italic;src:url(data:font/woff2;base64,{FONTE}) format("woff2")}}
text{{font-family:buzina,"STIX Two Text",Georgia,serif;font-weight:700;font-style:italic;font-size:17px;fill:{t["tx"]}}}
</style>
<rect x=".5" y=".5" width="{largura - 1}" height="43" rx="22" fill="{t["bg"]}" stroke="{t["borda"]}"/>
{marca}
<text x="46" y="28">{escape(texto)}</text>
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
