import type {
  BusinessRoute,
  IntakeMode,
  LanguageCode,
  StartFunction,
} from '../../types/session'


export const BUSINESS_ROUTES = ['production', 'quality', 'tdi'] as const

type DiscoveryIntakeMode = Exclude<IntakeMode, 'template'>

export type IntakeSessionRequest = {
  language: LanguageCode
  intake_mode: DiscoveryIntakeMode
  business_route: BusinessRoute
  starter_department: BusinessRoute
  start_function: StartFunction
}

export function normalizeBusinessRoute(value: string): BusinessRoute {
  const normalized = value.trim().toLowerCase()
  if ((BUSINESS_ROUTES as readonly string[]).includes(normalized)) {
    return normalized as BusinessRoute
  }
  throw new Error('Business route must be production, quality, or tdi.')
}

export function buildIntakeSessionRequest(
  mode: IntakeMode,
  businessRoute: string,
  language: LanguageCode,
): IntakeSessionRequest {
  if (mode !== 'scratch' && mode !== 'draft') {
    throw new Error('Intake mode must be scratch or draft.')
  }
  const route = normalizeBusinessRoute(businessRoute)
  return {
    language,
    intake_mode: mode,
    business_route: route,
    starter_department: route,
    start_function: mode === 'draft' ? 'improve_draft' : 'from_scratch',
  }
}
