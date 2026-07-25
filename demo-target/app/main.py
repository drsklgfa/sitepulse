from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

DATA_DIR = Path('/data') if Path('/data').exists() else Path('.')
STATE_FILE = DATA_DIR / 'demo-state.json'
LOCK = Lock()
DEFAULT_STATE = {
    'title': 'Notebook Aurora Pro 15',
    'price': 2499.90,
    'available': True,
    'news': 'SitePulse Demo Target iniciado com sucesso.',
    'revision': 1,
}


def load_state() -> dict:
    with LOCK:
        if not STATE_FILE.exists():
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            STATE_FILE.write_text(json.dumps(DEFAULT_STATE, ensure_ascii=False, indent=2), encoding='utf-8')
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))


def save_state(state: dict) -> dict:
    with LOCK:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    return state


class StateUpdate(BaseModel):
    price: float = Field(ge=0, le=10_000_000)
    available: bool
    title: str | None = Field(default=None, min_length=2, max_length=120)
    news: str | None = Field(default=None, min_length=2, max_length=500)


app = FastAPI(title='SitePulse Demo Target', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'demo-target'}


@app.get('/api/state')
def get_state() -> dict:
    return load_state()


@app.post('/api/state')
def update_state(payload: StateUpdate) -> dict:
    current = load_state()
    current.update(payload.model_dump(exclude_none=True))
    current['revision'] = int(current.get('revision', 0)) + 1
    return save_state(current)


@app.post('/api/randomize')
def randomize_state() -> dict:
    current = load_state()
    current['price'] = round(random.uniform(1799, 3299), 2)
    current['available'] = random.choice([True, True, False])
    current['news'] = random.choice([
        'Nova condição comercial publicada.',
        'Estoque regional atualizado.',
        'Prazo de entrega alterado.',
        'Campanha promocional ativada.',
    ])
    current['revision'] = int(current.get('revision', 0)) + 1
    return save_state(current)


@app.post('/api/reset')
def reset_state() -> dict:
    return save_state(dict(DEFAULT_STATE))


def money(value: float) -> str:
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def page_shell(content: str, title: str = 'SitePulse Demo Store') -> str:
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#07111f;color:#edf4ff;font-family:system-ui,sans-serif;min-height:100vh;display:grid;place-items:center;padding:30px}}
main{{width:min(900px,100%);background:#0d1a2b;border:1px solid #20344b;border-radius:20px;padding:34px;box-shadow:0 30px 90px #0006}}
nav{{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px}}nav strong{{color:#68e5c2}}nav span{{font-size:12px;color:#8294aa}}
.product{{display:grid;grid-template-columns:1fr 1fr;gap:35px}}.visual{{min-height:310px;border-radius:16px;background:radial-gradient(circle at 50% 45%,#295d6b,#0a1524 62%);display:grid;place-items:center;font-size:90px}}
h1{{font-size:36px;line-height:1.1;margin:10px 0}}.tag{{color:#68e5c2;font-size:11px;letter-spacing:1.5px;font-weight:800}}.price{{font-size:32px;font-weight:800;color:#68e5c2;margin:25px 0 7px}}.availability{{display:inline-block;padding:7px 10px;border-radius:30px;background:#68e5c21a;color:#68e5c2;font-size:12px}}p{{color:#91a2b6;line-height:1.65}}button{{background:#68e5c2;border:0;border-radius:9px;padding:12px 18px;font-weight:800;color:#06211c}}footer{{border-top:1px solid #20344b;margin-top:28px;padding-top:16px;color:#667a91;font-size:11px}}
@media(max-width:650px){{.product{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style></head><body><main><nav><strong>SitePulse Demo Store</strong><span>Página controlada para testes</span></nav>{content}<footer>Este ambiente existe apenas para demonstrar captura e detecção de mudanças de forma previsível.</footer></main></body></html>'''


@app.get('/', response_class=HTMLResponse)
def home() -> str:
    return page_shell('''<h1>Ambiente de demonstração</h1><p>Use <strong>/product</strong>, <strong>/dynamic</strong>, <strong>/news</strong>, <strong>/slow</strong> e <strong>/unstable</strong> para testar diferentes cenários.</p>''')


@app.get('/product', response_class=HTMLResponse)
def product() -> str:
    state = load_state()
    availability = 'Em estoque' if state['available'] else 'Indisponível'
    content = f'''<section class="product"><div class="visual">💻</div><div><span class="tag">TECNOLOGIA / DEMO</span><h1 data-testid="title">{state['title']}</h1><p>Produto fictício usado para demonstrar monitoramento de preço, texto e disponibilidade.</p><div class="price" data-testid="price">{money(float(state['price']))}</div><span class="availability" data-testid="availability">{availability}</span><p data-testid="revision">Revisão da página: {state['revision']}</p><button>Adicionar ao carrinho</button></div></section>'''
    return page_shell(content, state['title'])


@app.get('/dynamic', response_class=HTMLResponse)
def dynamic() -> str:
    content = '''<section><span class="tag">PÁGINA JAVASCRIPT</span><h1 data-testid="dynamic-title">Carregando…</h1><p>O conteúdo abaixo é inserido após uma chamada à API, exigindo renderização de navegador.</p><div class="price" data-testid="dynamic-price">Carregando…</div><span class="availability" data-testid="dynamic-availability">Aguardando…</span></section>
<script>fetch('/api/state').then(r=>r.json()).then(s=>{document.querySelector('[data-testid="dynamic-title"]').textContent=s.title;document.querySelector('[data-testid="dynamic-price"]').textContent=new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(s.price);document.querySelector('[data-testid="dynamic-availability"]').textContent=s.available?'Em estoque':'Indisponível';});</script>'''
    return page_shell(content, 'Demo JavaScript')


@app.get('/news', response_class=HTMLResponse)
def news() -> str:
    state = load_state()
    return page_shell(f'''<article><span class="tag">NOTÍCIAS / DEMO</span><h1>Boletim de mudanças</h1><p data-testid="news">{state['news']}</p><p data-testid="revision">Edição {state['revision']}</p></article>''', 'Boletim Demo')


@app.get('/slow', response_class=HTMLResponse)
async def slow(seconds: float = 2.0) -> str:
    await asyncio.sleep(min(max(seconds, 0), 12))
    return page_shell('<h1 data-testid="slow-result">Resposta concluída</h1><p>A rota simulou uma página lenta.</p>', 'Página lenta')


@app.get('/unstable', response_class=HTMLResponse)
def unstable(fail: bool = False) -> str:
    if fail:
        raise HTTPException(status_code=503, detail='Falha temporária simulada')
    return page_shell('<h1 data-testid="service-status">Operacional</h1><p>A rota pode responder com HTTP 503 por parâmetro.</p>', 'Página instável')
