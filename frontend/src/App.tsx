import { FormEvent, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import { formatDate, formatValue, statusLabel } from './format'
import type { Dashboard, Monitor, MonitorInput, Notification, Run } from './types'

type Tab = 'dashboard' | 'monitors' | 'runs' | 'alerts' | 'demo' | 'docs'

type Toast = { kind: 'success' | 'error'; message: string } | null

const navItems: Array<{ id: Tab; icon: string; label: string }> = [
  { id: 'dashboard', icon: '◫', label: 'Visão geral' },
  { id: 'monitors', icon: '◎', label: 'Monitores' },
  { id: 'runs', icon: '↻', label: 'Execuções' },
  { id: 'alerts', icon: '◉', label: 'Alertas' },
  { id: 'demo', icon: '◇', label: 'Demo Lab' },
  { id: 'docs', icon: '≡', label: 'Documentação' },
]

const defaultInput: MonitorInput = {
  name: '',
  description: '',
  url: 'http://demo-target:8080/product',
  selector: "[data-testid='price']",
  extraction_type: 'price',
  render_js: false,
  interval_minutes: 30,
  condition_type: 'any_change',
  is_active: true,
}

function App() {
  const [authenticated, setAuthenticated] = useState(api.isAuthenticated)
  const [tab, setTab] = useState<Tab>('dashboard')
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [monitors, setMonitors] = useState<Monitor[]>([])
  const [runs, setRuns] = useState<Run[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [toast, setToast] = useState<Toast>(null)
  const [dark, setDark] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [dashboardData, monitorData, runData, notificationData] = await Promise.all([
        api.dashboard(), api.monitors(), api.runs(), api.notifications(),
      ])
      setDashboard(dashboardData)
      setMonitors(monitorData)
      setRuns(runData)
      setNotifications(notificationData)
    } catch (error) {
      setToast({ kind: 'error', message: error instanceof Error ? error.message : 'Falha ao carregar dados.' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (authenticated) void load()
  }, [authenticated])

  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setToast(null), 3500)
    return () => window.clearTimeout(timer)
  }, [toast])

  if (!authenticated) {
    return <Login onSuccess={() => setAuthenticated(true)} />
  }

  const runMonitor = async (monitor: Monitor) => {
    try {
      await api.runMonitor(monitor.id)
      setToast({ kind: 'success', message: `Verificação de “${monitor.name}” enviada para a fila.` })
      window.setTimeout(() => void load(), 800)
    } catch (error) {
      setToast({ kind: 'error', message: error instanceof Error ? error.message : 'Não foi possível executar.' })
    }
  }

  const deleteMonitor = async (monitor: Monitor) => {
    if (!window.confirm(`Excluir o monitor “${monitor.name}”?`)) return
    try {
      await api.deleteMonitor(monitor.id)
      setMonitors((items) => items.filter((item) => item.id !== monitor.id))
      setToast({ kind: 'success', message: 'Monitor excluído.' })
    } catch (error) {
      setToast({ kind: 'error', message: error instanceof Error ? error.message : 'Não foi possível excluir.' })
    }
  }

  const createMonitor = async (input: MonitorInput) => {
    const created = await api.createMonitor(input)
    setMonitors((items) => [created, ...items])
    setModalOpen(false)
    setToast({ kind: 'success', message: 'Monitor criado com sucesso.' })
  }

  const logout = () => {
    api.logout()
    setAuthenticated(false)
  }

  return (
    <div className={dark ? 'app theme-dark' : 'app theme-light'}>
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><span /></div>
          <div><strong>SitePulse</strong><small>Web Intelligence</small></div>
        </div>
        <div className="workspace">
          <span className="workspace-avatar">SP</span>
          <div><small>Workspace</small><strong>Demo Portfolio</strong></div>
          <span className="workspace-chevron">⌄</span>
        </div>
        <nav>
          <p className="nav-title">NAVEGAÇÃO</p>
          {navItems.map((item) => (
            <button key={item.id} className={tab === item.id ? 'nav-item active' : 'nav-item'} onClick={() => setTab(item.id)}>
              <span>{item.icon}</span>{item.label}
              {item.id === 'alerts' && notifications.length > 0 && <b>{notifications.length}</b>}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="system-card"><i /><div><strong>Sistema operacional</strong><small>API, Redis e worker saudáveis</small></div></div>
          <button className="profile-button" onClick={logout}>
            <span>DE</span><div><strong>Demo User</strong><small>demo@sitepulse.local</small></div><b>↪</b>
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">SITEPULSE / {navItems.find((item) => item.id === tab)?.label.toUpperCase()}</span>
            <h1>{pageTitle(tab)}</h1>
          </div>
          <div className="top-actions">
            {api.isDemo && <span className="demo-badge">SHOWCASE MODE</span>}
            <button className="icon-button" onClick={() => setDark((value) => !value)} title="Alternar tema">{dark ? '☼' : '☾'}</button>
            <button className="secondary-button" onClick={() => void load()}>↻ Atualizar</button>
            <button className="primary-button" onClick={() => setModalOpen(true)}>＋ Novo monitor</button>
          </div>
        </header>

        <section className="content">
          {loading ? <Loading /> : (
            <>
              {tab === 'dashboard' && dashboard && <DashboardView dashboard={dashboard} monitors={monitors} />}
              {tab === 'monitors' && <MonitorsView monitors={monitors} onRun={runMonitor} onDelete={deleteMonitor} onCreate={() => setModalOpen(true)} />}
              {tab === 'runs' && <RunsView runs={runs} monitors={monitors} />}
              {tab === 'alerts' && <AlertsView notifications={notifications} />}
              {tab === 'demo' && <DemoLab monitors={monitors} onRun={runMonitor} demoMode={api.isDemo} onToast={setToast} />}
              {tab === 'docs' && <DocsView />}
            </>
          )}
        </section>
      </main>

      {modalOpen && <MonitorModal onClose={() => setModalOpen(false)} onSave={createMonitor} />}
      {toast && <div className={`toast ${toast.kind}`}>{toast.kind === 'success' ? '✓' : '!'} {toast.message}</div>}
    </div>
  )
}

function Login({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState('demo@sitepulse.local')
  const [password, setPassword] = useState('SitePulseDemo123!')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.login(email, password)
      onSuccess()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Falha ao entrar.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-glow glow-one" /><div className="login-glow glow-two" />
      <section className="login-copy">
        <div className="brand large"><div className="brand-mark"><span /></div><div><strong>SitePulse</strong><small>Web Intelligence</small></div></div>
        <span className="kicker">MONITORAMENTO QUE NÃO DORME</span>
        <h1>Descubra mudanças<br /><em>antes de todo mundo.</em></h1>
        <p>Uma plataforma completa para capturar, comparar e transformar mudanças na web em decisões rápidas.</p>
        <div className="login-features">
          <span>✓ Scraping HTTP e Playwright</span><span>✓ Filas assíncronas com Redis</span><span>✓ Alertas e histórico auditável</span>
        </div>
      </section>
      <form className="login-card" onSubmit={submit}>
        <span className="login-card-icon">◉</span>
        <h2>Bem-vindo de volta</h2>
        <p>Entre na conta demonstrativa para explorar o produto.</p>
        <label>E-mail<input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required /></label>
        <label>Senha<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required /></label>
        {error && <div className="form-error">{error}</div>}
        <button className="primary-button login-submit" disabled={loading}>{loading ? 'Entrando…' : 'Acessar dashboard →'}</button>
        <small className="login-hint">No GitHub Pages, o showcase entra automaticamente sem backend.</small>
      </form>
    </div>
  )
}

function DashboardView({ dashboard, monitors }: { dashboard: Dashboard; monitors: Monitor[] }) {
  const bars = [38, 62, 48, 75, 57, 82, 66, 92, 71, 86, 65, 79]
  return (
    <div className="dashboard-grid">
      <div className="hero-card">
        <div><span className="kicker">STATUS DA OPERAÇÃO</span><h2>Seu monitoramento está<br /><em>funcionando perfeitamente.</em></h2><p>{dashboard.active_monitors} monitores ativos verificando mudanças automaticamente.</p></div>
        <div className="pulse-orbit"><span className="orbit orbit-one" /><span className="orbit orbit-two" /><i>◉</i><b>{dashboard.success_rate}%<small>sucesso</small></b></div>
      </div>
      <div className="stats-row">
        <Metric label="Monitores ativos" value={dashboard.active_monitors} detail={`${dashboard.total_monitors} configurados`} icon="◎" trend="+2 este mês" />
        <Metric label="Verificações" value={dashboard.total_runs} detail="execuções registradas" icon="↻" trend={`${dashboard.successful_runs} concluídas`} />
        <Metric label="Mudanças" value={dashboard.changed_runs} detail="alterações detectadas" icon="◇" trend={`${dashboard.unread_notifications} alertas`} />
        <Metric label="Tempo médio" value={`${dashboard.average_duration_ms} ms`} detail="por captura" icon="⌁" trend="processamento assíncrono" />
      </div>
      <div className="panel chart-panel">
        <div className="panel-header"><div><span className="kicker">ATIVIDADE</span><h3>Verificações recentes</h3></div><span className="period-chip">Últimos 12 ciclos</span></div>
        <div className="chart"><div className="chart-grid-lines"><i /><i /><i /><i /></div>{bars.map((height, index) => <span key={index} style={{ height: `${height}%` }} className={index === 7 ? 'hot' : ''} />)}</div>
        <div className="chart-legend"><span><i className="legend-primary" />Bem-sucedidas</span><span><i className="legend-hot" />Com alteração</span></div>
      </div>
      <div className="panel monitored-panel">
        <div className="panel-header"><div><span className="kicker">PRIORIDADE</span><h3>Monitores em destaque</h3></div><button className="text-button">Ver todos →</button></div>
        <div className="monitor-cards">{monitors.slice(0, 3).map((monitor) => <CompactMonitor key={monitor.id} monitor={monitor} />)}</div>
      </div>
      <div className="panel activity-panel">
        <div className="panel-header"><div><span className="kicker">LINHA DO TEMPO</span><h3>Últimas execuções</h3></div></div>
        <div className="timeline">{dashboard.recent_runs.slice(0, 5).map((run) => <RunTimeline key={run.id} run={run} monitors={monitors} />)}</div>
      </div>
      <div className="panel health-panel">
        <div className="panel-header"><div><span className="kicker">INFRAESTRUTURA</span><h3>Saúde dos serviços</h3></div><span className="status-dot">Tudo operacional</span></div>
        <div className="health-list"><Health name="FastAPI" detail="API e autenticação" /><Health name="PostgreSQL" detail="Persistência e histórico" /><Health name="Redis + Celery" detail="Fila e agendamento" /><Health name="Playwright" detail="Páginas dinâmicas" /></div>
      </div>
    </div>
  )
}

function Metric({ label, value, detail, icon, trend }: { label: string; value: number | string; detail: string; icon: string; trend: string }) {
  return <div className="metric-card"><div className="metric-top"><span>{icon}</span><small>{trend}</small></div><strong>{value}</strong><h4>{label}</h4><p>{detail}</p></div>
}

function CompactMonitor({ monitor }: { monitor: Monitor }) {
  return <div className="compact-monitor"><div className="compact-icon">{monitor.extraction_type === 'price' ? 'R$' : monitor.render_js ? 'JS' : 'TXT'}</div><div><strong>{monitor.name}</strong><small>{monitor.is_active ? 'Ativo' : 'Pausado'} · a cada {monitor.interval_minutes} min</small></div><b>{formatValue(monitor.last_value, monitor.extraction_type)}</b></div>
}

function RunTimeline({ run, monitors }: { run: Run; monitors: Monitor[] }) {
  const monitor = monitors.find((item) => item.id === run.monitor_id)
  return <div className="timeline-item"><i className={`run-${run.status}`} /><div><strong>{monitor?.name || `Monitor #${run.monitor_id}`}</strong><small>{statusLabel(run.status)} · {formatDate(run.created_at)}</small></div><span>{run.duration_ms ? `${run.duration_ms} ms` : '—'}</span></div>
}

function Health({ name, detail }: { name: string; detail: string }) {
  return <div><i /><span><strong>{name}</strong><small>{detail}</small></span><b>Operacional</b></div>
}

function MonitorsView({ monitors, onRun, onDelete, onCreate }: { monitors: Monitor[]; onRun: (monitor: Monitor) => void; onDelete: (monitor: Monitor) => void; onCreate: () => void }) {
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => monitors.filter((monitor) => monitor.name.toLowerCase().includes(query.toLowerCase())), [monitors, query])
  return <div className="page-stack">
    <div className="page-intro"><div><span className="kicker">CONTROLE CENTRAL</span><h2>Todos os monitores</h2><p>Configure páginas, seletores, condições e periodicidade em um único lugar.</p></div><button className="primary-button" onClick={onCreate}>＋ Criar monitor</button></div>
    <div className="panel table-panel"><div className="table-toolbar"><label className="search-box">⌕<input placeholder="Buscar monitor…" value={query} onChange={(event) => setQuery(event.target.value)} /></label><div><span className="filter-chip active">Todos {monitors.length}</span><span className="filter-chip">Ativos {monitors.filter((item) => item.is_active).length}</span></div></div>
      <div className="table-wrap"><table><thead><tr><th>Monitor</th><th>Valor atual</th><th>Frequência</th><th>Última verificação</th><th>Status</th><th /></tr></thead><tbody>{filtered.map((monitor) => <tr key={monitor.id}><td><div className="table-title"><span>{monitor.extraction_type === 'price' ? 'R$' : monitor.render_js ? 'JS' : 'TXT'}</span><div><strong>{monitor.name}</strong><small>{monitor.selector || 'Página completa'}</small></div></div></td><td><b>{formatValue(monitor.last_value, monitor.extraction_type)}</b></td><td>A cada {monitor.interval_minutes} min</td><td>{formatDate(monitor.last_checked_at)}</td><td><span className={monitor.is_active ? 'state active' : 'state paused'}>{monitor.is_active ? 'Ativo' : 'Pausado'}</span></td><td><div className="row-actions"><button onClick={() => onRun(monitor)} title="Executar">▶</button><button onClick={() => onDelete(monitor)} title="Excluir">×</button></div></td></tr>)}</tbody></table></div>
      {filtered.length === 0 && <Empty title="Nenhum monitor encontrado" text="Ajuste a busca ou crie um novo monitor." />}
    </div>
  </div>
}

function RunsView({ runs, monitors }: { runs: Run[]; monitors: Monitor[] }) {
  return <div className="page-stack"><div className="page-intro"><div><span className="kicker">AUDITORIA COMPLETA</span><h2>Histórico de execuções</h2><p>Cada captura registra status, duração, valor anterior, valor atual e possíveis erros.</p></div></div>
    <div className="panel table-panel"><div className="table-wrap"><table><thead><tr><th>Execução</th><th>Monitor</th><th>Resultado</th><th>Valor</th><th>HTTP</th><th>Duração</th><th>Data</th></tr></thead><tbody>{runs.map((run) => { const monitor = monitors.find((item) => item.id === run.monitor_id); return <tr key={run.id}><td><b>#{run.id}</b></td><td>{monitor?.name || `Monitor #${run.monitor_id}`}</td><td><span className={`run-badge ${run.status}`}>{statusLabel(run.status)}</span></td><td>{formatValue(run.value, monitor?.extraction_type)}</td><td>{run.http_status || '—'}</td><td>{run.duration_ms ? `${run.duration_ms} ms` : '—'}</td><td>{formatDate(run.created_at)}</td></tr> })}</tbody></table></div></div>
  </div>
}

function AlertsView({ notifications }: { notifications: Notification[] }) {
  return <div className="page-stack"><div className="page-intro"><div><span className="kicker">SINAIS IMPORTANTES</span><h2>Central de alertas</h2><p>Notificações internas e e-mails gerados quando uma condição é atendida.</p></div></div>
    <div className="alert-grid">{notifications.map((notification) => <article className="alert-card" key={notification.id}><div className="alert-icon">{notification.channel === 'email' ? '✉' : '◉'}</div><div><span className="alert-meta">{notification.channel.toUpperCase()} · {formatDate(notification.created_at)}</span><h3>{notification.title}</h3><p>{notification.body}</p></div><span className={`state ${notification.status === 'sent' ? 'active' : 'paused'}`}>{notification.status === 'sent' ? 'Enviado' : notification.status}</span></article>)}</div>
    {notifications.length === 0 && <Empty title="Nenhum alerta ainda" text="Os alertas aparecerão quando uma condição de monitoramento for atendida." />}
  </div>
}

function DemoLab({ monitors, onRun, demoMode, onToast }: { monitors: Monitor[]; onRun: (monitor: Monitor) => void; demoMode: boolean; onToast: (toast: Toast) => void }) {
  const [price, setPrice] = useState('2199.90')
  const [available, setAvailable] = useState(true)
  const demoTarget = import.meta.env.VITE_DEMO_TARGET_URL || 'http://localhost:8080'

  const updateTarget = async () => {
    if (demoMode) {
      onToast({ kind: 'success', message: `Simulação atualizada: R$ ${price.replace('.', ',')} · ${available ? 'Em estoque' : 'Indisponível'}.` })
      return
    }
    try {
      const response = await fetch(`${demoTarget}/api/state`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ price: Number(price), available }) })
      if (!response.ok) throw new Error('Falha ao atualizar o Demo Target')
      onToast({ kind: 'success', message: 'Página demonstrativa alterada. Execute o monitor para detectar a mudança.' })
    } catch (error) {
      onToast({ kind: 'error', message: error instanceof Error ? error.message : 'Falha no Demo Lab.' })
    }
  }

  return <div className="page-stack"><div className="page-intro"><div><span className="kicker">AMBIENTE CONTROLADO</span><h2>Demo Lab</h2><p>Altere uma página própria e acompanhe todo o ciclo: captura, comparação, snapshot, alerta e notificação.</p></div><span className="demo-badge">SEM DEPENDÊNCIA EXTERNA</span></div>
    <div className="demo-grid"><section className="panel demo-control"><div className="step-number">01</div><h3>Modifique o produto</h3><p>O Demo Target simula uma página de e-commerce segura e previsível.</p><label>Preço demonstrativo (R$)<input type="number" step="0.01" value={price} onChange={(event) => setPrice(event.target.value)} /></label><label className="toggle-line"><span><strong>Produto disponível</strong><small>Alterna o texto de estoque</small></span><input type="checkbox" checked={available} onChange={(event) => setAvailable(event.target.checked)} /></label><button className="primary-button full" onClick={() => void updateTarget()}>Salvar alteração</button></section>
      <section className="panel demo-control"><div className="step-number">02</div><h3>Execute o monitor</h3><p>O trabalho será enviado à fila e processado fora da API.</p>{monitors.slice(0, 2).map((monitor) => <button key={monitor.id} className="demo-monitor-button" onClick={() => onRun(monitor)}><span>▶</span><div><strong>{monitor.name}</strong><small>{monitor.selector}</small></div><b>Executar</b></button>)}</section>
      <section className="panel demo-flow"><div className="step-number">03</div><h3>Observe o fluxo</h3><div className="flow-line"><span>1</span><div><strong>FastAPI</strong><small>valida e cria a execução</small></div></div><div className="flow-arrow">↓</div><div className="flow-line"><span>2</span><div><strong>Redis + Celery</strong><small>organiza o processamento</small></div></div><div className="flow-arrow">↓</div><div className="flow-line"><span>3</span><div><strong>Scraper</strong><small>captura e compara o conteúdo</small></div></div><div className="flow-arrow">↓</div><div className="flow-line"><span>4</span><div><strong>PostgreSQL + Mailpit</strong><small>salva histórico e entrega o alerta</small></div></div></section></div>
  </div>
}

function DocsView() {
  return <div className="page-stack"><div className="page-intro"><div><span className="kicker">PROJETO DIDÁTICO</span><h2>Como o SitePulse funciona</h2><p>Uma visão direta das decisões técnicas demonstradas no repositório.</p></div></div>
    <div className="docs-grid"><DocCard number="01" title="Captura híbrida" text="HTTPX e BeautifulSoup cuidam de páginas leves. Playwright entra apenas quando JavaScript é necessário." tags={['HTTPX', 'BeautifulSoup', 'Playwright']} /><DocCard number="02" title="Processamento assíncrono" text="A API responde rapidamente enquanto workers Celery processam as tarefas publicadas no Redis." tags={['Celery', 'Redis', 'Retries']} /><DocCard number="03" title="Histórico confiável" text="PostgreSQL guarda monitores, execuções, snapshots e notificações com relacionamento auditável." tags={['PostgreSQL', 'SQLAlchemy', 'Alembic']} /><DocCard number="04" title="Qualidade contínua" text="Testes, lint, builds e análise de segurança executam automaticamente em cada push e pull request." tags={['Pytest', 'Vitest', 'GitHub Actions']} /><DocCard number="05" title="Segurança por padrão" text="Validação de URLs, bloqueio SSRF, limites de tamanho, timeout, redirecionamentos controlados e autenticação JWT." tags={['SSRF', 'JWT', 'Rate-ready']} /><DocCard number="06" title="Execução portátil" text="Docker Compose inicia frontend, API, banco, Redis, workers, scheduler, Mailpit, Flower e Demo Target." tags={['Docker', 'Compose', 'Healthchecks']} /></div>
  </div>
}

function DocCard({ number, title, text, tags }: { number: string; title: string; text: string; tags: string[] }) {
  return <article className="doc-card"><span>{number}</span><h3>{title}</h3><p>{text}</p><div>{tags.map((tag) => <b key={tag}>{tag}</b>)}</div></article>
}

function MonitorModal({ onClose, onSave }: { onClose: () => void; onSave: (input: MonitorInput) => Promise<void> }) {
  const [input, setInput] = useState<MonitorInput>(defaultInput)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setSaving(true); setError('')
    try { await onSave(input) } catch (reason) { setError(reason instanceof Error ? reason.message : 'Não foi possível salvar.'); setSaving(false) }
  }
  return <div className="modal-backdrop" onMouseDown={onClose}><form className="modal" onSubmit={submit} onMouseDown={(event) => event.stopPropagation()}><div className="modal-header"><div><span className="kicker">NOVO MONITOR</span><h2>Configure uma fonte</h2></div><button type="button" onClick={onClose}>×</button></div><div className="form-grid"><label className="wide">Nome<input required value={input.name} onChange={(event) => setInput({ ...input, name: event.target.value })} placeholder="Ex.: Preço do notebook" /></label><label className="wide">URL<input required value={input.url} onChange={(event) => setInput({ ...input, url: event.target.value })} /></label><label>Seletor CSS<input value={input.selector || ''} onChange={(event) => setInput({ ...input, selector: event.target.value })} /></label><label>Tipo de extração<select value={input.extraction_type} onChange={(event) => setInput({ ...input, extraction_type: event.target.value as MonitorInput['extraction_type'] })}><option value="text">Texto</option><option value="price">Preço</option><option value="number">Número</option><option value="status">Status HTTP</option><option value="html">HTML</option><option value="attribute">Atributo</option></select></label><label>Intervalo em minutos<input type="number" min="1" value={input.interval_minutes} onChange={(event) => setInput({ ...input, interval_minutes: Number(event.target.value) })} /></label><label>Condição<select value={input.condition_type} onChange={(event) => setInput({ ...input, condition_type: event.target.value as MonitorInput['condition_type'] })}><option value="any_change">Qualquer mudança</option><option value="price_drop">Queda de preço</option><option value="price_below">Preço abaixo de</option><option value="contains">Contém palavra</option><option value="not_contains">Não contém palavra</option><option value="status_not_ok">Status com erro</option></select></label><label className="wide">Descrição<textarea value={input.description || ''} onChange={(event) => setInput({ ...input, description: event.target.value })} placeholder="Explique o objetivo deste monitor." /></label><label className="toggle-line wide"><span><strong>Renderizar JavaScript</strong><small>Utiliza Playwright; ative apenas quando necessário.</small></span><input type="checkbox" checked={input.render_js} onChange={(event) => setInput({ ...input, render_js: event.target.checked })} /></label></div>{error && <div className="form-error">{error}</div>}<div className="modal-footer"><button type="button" className="secondary-button" onClick={onClose}>Cancelar</button><button className="primary-button" disabled={saving}>{saving ? 'Salvando…' : 'Criar monitor'}</button></div></form></div>
}

function Empty({ title, text }: { title: string; text: string }) { return <div className="empty"><span>◎</span><h3>{title}</h3><p>{text}</p></div> }
function Loading() { return <div className="loading"><div className="loader" /><strong>Sincronizando o SitePulse…</strong><small>Carregando monitores, execuções e alertas</small></div> }
function pageTitle(tab: Tab): string { return ({ dashboard: 'Visão geral', monitors: 'Monitores', runs: 'Execuções', alerts: 'Alertas', demo: 'Demo Lab', docs: 'Documentação' })[tab] }

export default App
