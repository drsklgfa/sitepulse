import type { Dashboard, Monitor, Notification, Run } from './types'

const now = new Date()
const ago = (minutes: number) => new Date(now.getTime() - minutes * 60_000).toISOString()

export const mockMonitors: Monitor[] = [
  {
    id: 1, owner_id: 1, name: 'Preço do notebook demonstrativo',
    description: 'Monitora o preço no ambiente controlado do Demo Lab.',
    url: 'http://demo-target:8080/product', selector: "[data-testid='price']",
    extraction_type: 'price', render_js: false, interval_minutes: 30,
    condition_type: 'any_change', is_active: true, last_value: '2199.90',
    last_checked_at: ago(4), next_run_at: ago(-26), created_at: ago(4000), updated_at: ago(4),
  },
  {
    id: 2, owner_id: 1, name: 'Disponibilidade do produto',
    description: 'Alerta quando o estoque muda.',
    url: 'http://demo-target:8080/product', selector: "[data-testid='availability']",
    extraction_type: 'text', render_js: false, interval_minutes: 15,
    condition_type: 'any_change', is_active: true, last_value: 'Em estoque',
    last_checked_at: ago(8), next_run_at: ago(-7), created_at: ago(3800), updated_at: ago(8),
  },
  {
    id: 3, owner_id: 1, name: 'Página dinâmica com JavaScript',
    description: 'Exemplo preparado para Playwright.',
    url: 'http://demo-target:8080/dynamic', selector: "[data-testid='dynamic-price']",
    extraction_type: 'price', render_js: true, interval_minutes: 60,
    condition_type: 'price_drop', is_active: false, last_value: null,
    last_checked_at: null, next_run_at: null, created_at: ago(3000), updated_at: ago(3000),
  },
]

export const mockRuns: Run[] = [
  { id: 19, monitor_id: 1, status: 'changed', http_status: 200, duration_ms: 327, value: '2199.90', previous_value: '2499.90', changed: true, alert_triggered: true, created_at: ago(4), started_at: ago(4), finished_at: ago(4) },
  { id: 18, monitor_id: 2, status: 'no_change', http_status: 200, duration_ms: 244, value: 'Em estoque', previous_value: 'Em estoque', changed: false, alert_triggered: false, created_at: ago(8), started_at: ago(8), finished_at: ago(8) },
  { id: 17, monitor_id: 1, status: 'no_change', http_status: 200, duration_ms: 301, value: '2499.90', previous_value: '2499.90', changed: false, alert_triggered: false, created_at: ago(34), started_at: ago(34), finished_at: ago(34) },
  { id: 16, monitor_id: 2, status: 'failed', http_status: 503, duration_ms: 15012, value: null, previous_value: 'Em estoque', changed: false, alert_triggered: false, error_message: 'Página indisponível após 3 tentativas', created_at: ago(50), started_at: ago(50), finished_at: ago(50) },
]

export const mockNotifications: Notification[] = [
  { id: 4, monitor_id: 1, run_id: 19, channel: 'in_app', status: 'sent', title: 'Preço reduzido em R$ 300,00', body: 'O notebook passou de R$ 2.499,90 para R$ 2.199,90.', created_at: ago(4) },
  { id: 3, monitor_id: 1, run_id: 19, channel: 'email', status: 'sent', title: 'Alteração detectada', body: 'A notificação demonstrativa foi recebida pelo Mailpit.', created_at: ago(4) },
]

export const mockDashboard: Dashboard = {
  total_monitors: 3,
  active_monitors: 2,
  total_runs: 19,
  successful_runs: 18,
  changed_runs: 4,
  failed_runs: 1,
  unread_notifications: 2,
  success_rate: 94.7,
  average_duration_ms: 412,
  recent_runs: mockRuns,
  recent_notifications: mockNotifications,
}
