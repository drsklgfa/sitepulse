import { mockDashboard, mockMonitors, mockNotifications, mockRuns } from './mock'
import type { Dashboard, Monitor, MonitorInput, Notification, Run } from './types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

class ApiClient {
  private token = localStorage.getItem('sitepulse_token')

  get isDemo(): boolean { return DEMO_MODE }
  get isAuthenticated(): boolean { return Boolean(this.token) || DEMO_MODE }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    if (DEMO_MODE) throw new Error('demo-mode')
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
        ...options.headers,
      },
    })
    if (!response.ok) {
      const payload = await response.json().catch(() => ({ detail: 'Erro inesperado' }))
      throw new Error(payload.detail || `Erro HTTP ${response.status}`)
    }
    if (response.status === 204) return undefined as T
    return response.json() as Promise<T>
  }

  async login(email: string, password: string): Promise<void> {
    if (DEMO_MODE) return
    const data = await this.request<{ access_token: string }>('/auth/login', {
      method: 'POST', body: JSON.stringify({ email, password }),
    })
    this.token = data.access_token
    localStorage.setItem('sitepulse_token', data.access_token)
  }

  logout(): void {
    this.token = null
    localStorage.removeItem('sitepulse_token')
  }

  async dashboard(): Promise<Dashboard> {
    if (DEMO_MODE) return structuredClone(mockDashboard)
    return this.request('/dashboard')
  }

  async monitors(): Promise<Monitor[]> {
    if (DEMO_MODE) return structuredClone(mockMonitors)
    return this.request('/monitors')
  }

  async runs(): Promise<Run[]> {
    if (DEMO_MODE) return structuredClone(mockRuns)
    return this.request('/runs')
  }

  async notifications(): Promise<Notification[]> {
    if (DEMO_MODE) return structuredClone(mockNotifications)
    return this.request('/notifications')
  }

  async createMonitor(payload: MonitorInput): Promise<Monitor> {
    if (DEMO_MODE) {
      return { id: Date.now(), owner_id: 1, last_value: null, last_checked_at: null, next_run_at: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), ...payload }
    }
    return this.request('/monitors', { method: 'POST', body: JSON.stringify(payload) })
  }

  async runMonitor(id: number): Promise<void> {
    if (DEMO_MODE) return
    await this.request(`/monitors/${id}/run`, { method: 'POST' })
  }

  async deleteMonitor(id: number): Promise<void> {
    if (DEMO_MODE) return
    await this.request(`/monitors/${id}`, { method: 'DELETE' })
  }
}

export const api = new ApiClient()
