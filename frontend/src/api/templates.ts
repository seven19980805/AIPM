import type { BusinessTemplateDetail, BusinessTemplateSummary } from '../types/businessTemplate'
import { apiJson } from './http'


export async function fetchBusinessTemplates(): Promise<BusinessTemplateSummary[]> {
  const data = await apiJson<{ templates: BusinessTemplateSummary[] }>('/api/templates')
  return data.templates ?? []
}


export function fetchBusinessTemplate(templateId: string): Promise<BusinessTemplateDetail> {
  return apiJson<BusinessTemplateDetail>(`/api/templates/${encodeURIComponent(templateId)}`)
}
