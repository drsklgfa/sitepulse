export type ExtractionType = 'text' | 'price' | 'number' | 'status' | 'html' | 'attribute'
export type ConditionType = 'any_change' | 'price_drop' | 'price_below' | 'contains' | 'not_contains' | 'status_not_ok'

export interface Monitor {
  id: number
  owner_id: number
  name: string
  description?: string | null
  url: string
  selector?: string | null
  extraction_type: ExtractionType
  attribute_name?: string | null
  render_js: boolean
  interval_minutes: number
  condition_type: ConditionType
  threshold?: number | null
  keyword?: string | null
  is_active: boolean
  last_value?: string | null
  last_checked_at?: string | null
  next_run_at?: string | null
  created_at: string
  updated_at: string
}

export interface Run {
  id: number
  monitor_id: number
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'changed' | 'no_change'
  started_at?: string | null
  finished_at?: string | null
  http_status?: number | null
  duration_ms?: number | null
  attempts?: number
  value?: string | null
  previous_value?: string | null
  changed: boolean
  alert_triggered: boolean
  error_message?: string | null
  created_at: string
}

export interface Notification {
  id: number
  monitor_id: number
  run_id?: number | null
  channel: string
  status: string
  title: string
  body: string
  created_at: string
}

export interface Dashboard {
  total_monitors: number
  active_monitors: number
  total_runs: number
  successful_runs: number
  changed_runs: number
  failed_runs: number
  unread_notifications: number
  success_rate: number
  average_duration_ms: number
  recent_runs: Run[]
  recent_notifications: Notification[]
}

export interface MonitorInput {
  name: string
  description?: string
  url: string
  selector?: string
  extraction_type: ExtractionType
  attribute_name?: string
  render_js: boolean
  interval_minutes: number
  condition_type: ConditionType
  threshold?: number
  keyword?: string
  is_active: boolean
}
