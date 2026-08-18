import type { BusinessTemplateSummary } from '../../types/businessTemplate'


export type TemplateCatalogDomain = {
  id: string
  label: string
  count: number
}

export function filterTemplateCatalog(
  templates: readonly BusinessTemplateSummary[],
  filters: {
    query?: string
    domain?: string
  } = {},
): BusinessTemplateSummary[] {
  const query = normalize(filters.query)
  const queryTokens = query.split(/\s+/).filter(Boolean)
  const domain = normalize(filters.domain)

  return templates.filter((template) => {
    const templateDomain = normalize(template.business_domain || template.template_category)
    if (domain && templateDomain !== domain) {
      return false
    }
    if (!queryTokens.length) {
      return true
    }
    const searchableText = searchableTemplateText(template)
    return queryTokens.every((token) => searchableText.includes(token))
  })
}


export function templateCatalogDomains(
  templates: readonly BusinessTemplateSummary[],
): TemplateCatalogDomain[] {
  const counts = new Map<string, number>()
  for (const template of templates) {
    const label = (template.business_domain || template.template_category).trim()
    if (!label) {
      continue
    }
    counts.set(label, (counts.get(label) ?? 0) + 1)
  }

  return Array.from(counts.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([label, count]) => ({
      id: label,
      label,
      count,
    }))
}


function searchableTemplateText(template: BusinessTemplateSummary): string {
  return normalize([
    template.template_name,
    template.template_category,
    template.business_domain,
    template.description,
    ...template.tags,
    ...template.applicable_scenarios,
    ...template.section_titles,
  ].join(' '))
}


function normalize(value: unknown): string {
  return String(value ?? '').trim().toLocaleLowerCase()
}
