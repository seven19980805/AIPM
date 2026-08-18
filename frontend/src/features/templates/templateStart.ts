import type { BusinessRoute, LanguageCode } from '../../types/session'


export type TemplateSessionRequest = {
  language: LanguageCode
  template_id: string
  template_start_mode: 'guided'
  intake_mode?: 'template'
  business_route?: BusinessRoute
  start_function: 'from_scratch'
}

export function buildTemplateSessionRequest(
  templateId: string,
  language: LanguageCode,
  options: {
    businessRoute?: string
  } = {},
): TemplateSessionRequest {
  const normalizedTemplateId = templateId.trim()
  if (!normalizedTemplateId) {
    throw new Error('Template id is required.')
  }

  const request: TemplateSessionRequest = {
    language,
    template_id: normalizedTemplateId,
    template_start_mode: 'guided',
    start_function: 'from_scratch',
  }

  const normalizedRoute = options.businessRoute?.trim().toLowerCase()
  if (normalizedRoute && ['production', 'quality', 'tdi'].includes(normalizedRoute)) {
    request.intake_mode = 'template'
    request.business_route = normalizedRoute as BusinessRoute
  }

  return request
}
