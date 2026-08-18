const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')


export function apiUrl(path: string): string {
  if (!API_BASE_URL) {
    return path
  }
  return `${API_BASE_URL}${path}`
}


export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  })

  const data: unknown = await response.json().catch(() => ({}))
  if (!response.ok) {
    const errorPayload = typeof data === 'object' && data !== null
      ? data as Record<string, unknown>
      : {}
    const errorMessage = typeof errorPayload.error === 'string'
      ? errorPayload.error
      : `Request failed: ${response.status}`
    throw new Error(errorMessage)
  }
  return data as T
}
