export type BusinessTemplateSummary = {
  template_id: string
  template_key: string
  template_name: string
  template_category: string
  business_domain: string
  language: string
  version: string
  description: string
  tags: string[]
  applicable_scenarios: string[]
  section_count: number
  section_titles: string[]
}

export type BusinessTemplateSection = {
  section_key: string
  section_title: string
  sort_order: number
  field_count: number
}

export type BusinessTemplateDetail = BusinessTemplateSummary & {
  storage_model: string
  render_config: Record<string, unknown>
  sections: BusinessTemplateSection[]
  template_markdown: string
  prompt_hints?: Array<Record<string, unknown>>
  prompt_questions?: Array<Record<string, unknown>>
}
