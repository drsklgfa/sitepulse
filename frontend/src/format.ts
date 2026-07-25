export const formatDate = (value?: string | null): string => {
  if (!value) return 'Ainda não executado'
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

export const formatValue = (value?: string | null, type?: string): string => {
  if (value == null || value === '') return '—'
  if (type === 'price') {
    const number = Number(value)
    if (Number.isFinite(number)) {
      return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(number)
    }
  }
  return value
}

export const statusLabel = (status: string): string => ({
  queued: 'Na fila',
  running: 'Executando',
  succeeded: 'Concluída',
  failed: 'Falhou',
  changed: 'Alteração',
  no_change: 'Sem alteração',
}[status] ?? status)
