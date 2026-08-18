import type {
  BusinessRoute,
  IntakeMode,
  LanguageCode,
  SessionDetail,
  SessionSummary,
  StartFunction,
} from '../types/session'
import { apiJson } from './http'


export type CreateSessionRequest = {
  language: LanguageCode
  template_id?: string
  template_start_mode?: 'guided'
  starter_department?: string
  start_function?: StartFunction
  intake_mode?: IntakeMode
  business_route?: BusinessRoute
}

export async function fetchSessions(): Promise<SessionSummary[]> {
  const data = await apiJson<{ sessions: SessionSummary[] }>('/api/sessions')
  return data.sessions ?? []
}


export function fetchSession(sessionId: string, language: LanguageCode): Promise<SessionDetail> {
  return apiJson<SessionDetail>(
    `/api/sessions/${encodeURIComponent(sessionId)}?language=${encodeURIComponent(language)}`,
  )
}

export function updateSessionLanguage(
  sessionId: string,
  language: LanguageCode,
): Promise<SessionDetail> {
  return apiJson<SessionDetail>(
    `/api/sessions/${encodeURIComponent(sessionId)}/language`,
    {
      method: 'PATCH',
      body: JSON.stringify({ language }),
    },
  )
}


export function createSessionRequest(payload: CreateSessionRequest): Promise<SessionDetail> {
  return apiJson<SessionDetail>('/api/sessions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
