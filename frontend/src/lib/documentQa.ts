import type { MessageKind } from '../types/session'

export type DocumentQaState = {
  sourceKind: MessageKind
  documentType: string
  demoReadiness: string
  productionReadiness: string
  openQuestionCount: number | null
  productionBlockers: string[]
  businessRuleFindings: string[]
  implementationFindings: string[]
  classificationCounts: {
    blockingForProduction: number | null
    okForDemo: number | null
    implementationAssumptions: number | null
    needsReview: number | null
  }
}

const QA_HEADING_PATTERN = /^##\s+(?:Document QA|文档质量检查.*Document QA)\s*$/im
const NEXT_H2_PATTERN = /^##\s+/m
const SECTION_HEADING_PATTERN = /^###\s+(.+?)\s*$/gm
const KEY_VALUE_BULLET_PATTERN = /^-\s+\*\*(.+?)\*\*[:：]\s*(.*?)\s*$/gm
const NONE_PATTERN = /^(?:none|无|沒有|没有)$/i

export function parseDocumentQa(content: string, sourceKind: MessageKind): DocumentQaState | null {
  const qaSection = extractQaSection(content)
  if (!qaSection) {
    return null
  }

  const keyValues = extractKeyValues(qaSection)
  const productionBlockers = extractBulletListAfterHeading(qaSection, [
    'Production Blockers',
    '生产版阻塞项',
  ])
  const businessRuleFindings = extractBulletListAfterHeading(qaSection, [
    'Business Rule Sanity Checks',
    '业务规则 sanity check',
  ])
  const implementationFindings = extractBulletListAfterHeading(qaSection, [
    'Implementation Assumption Checks',
    '实现假设检查',
  ])

  const openQuestionCount = parseNullableInteger(
    findKeyValue(keyValues, ['system-counted open questions', '系统计数的 open questions']),
  )

  return {
    sourceKind,
    documentType: findKeyValue(keyValues, ['document type', '文档类型']) || fallbackDocumentType(sourceKind),
    demoReadiness: findKeyValue(keyValues, ['demo readiness']) || 'Unknown',
    productionReadiness: findKeyValue(keyValues, ['production readiness']) || 'Unknown',
    openQuestionCount,
    productionBlockers,
    businessRuleFindings,
    implementationFindings,
    classificationCounts: {
      blockingForProduction: parseNullableInteger(
        findKeyValue(keyValues, ['blocking for production', '生产版阻塞']),
      ),
      okForDemo: parseNullableInteger(
        findKeyValue(keyValues, ['ok for demo / polish later', 'demo 可接受 / 后续润色']),
      ),
      implementationAssumptions: parseNullableInteger(
        findKeyValue(keyValues, ['implementation assumptions', '实现假设']),
      ),
      needsReview: parseNullableInteger(findKeyValue(keyValues, ['needs review', '仍需人工复核'])),
    },
  }
}

function extractQaSection(content: string): string {
  const match = QA_HEADING_PATTERN.exec(content)
  if (!match || match.index === undefined) {
    return ''
  }
  const start = match.index
  const rest = content.slice(start + match[0].length)
  const nextHeadingMatch = NEXT_H2_PATTERN.exec(rest)
  const end = nextHeadingMatch?.index === undefined ? content.length : start + match[0].length + nextHeadingMatch.index
  return content.slice(start, end).trim()
}

function extractKeyValues(section: string): Map<string, string> {
  const values = new Map<string, string>()
  for (const match of section.matchAll(KEY_VALUE_BULLET_PATTERN)) {
    const key = normalizeKey(match[1])
    const value = match[2].trim()
    if (key && value && !values.has(key)) {
      values.set(key, value)
    }
  }
  return values
}

function extractBulletListAfterHeading(section: string, headings: string[]): string[] {
  const targetHeadings = headings.map(normalizeKey)
  const headingMatches = [...section.matchAll(SECTION_HEADING_PATTERN)]
  const targetIndex = headingMatches.findIndex((match) => targetHeadings.includes(normalizeKey(match[1])))
  if (targetIndex === -1) {
    return []
  }
  const targetMatch = headingMatches[targetIndex]
  const nextMatch = headingMatches[targetIndex + 1]
  const start = (targetMatch.index ?? 0) + targetMatch[0].length
  const end = nextMatch?.index ?? section.length
  const body = section.slice(start, end)
  return body
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.startsWith('- '))
    .map((line) => line.replace(/^-\s+/, '').trim())
    .filter((line) => line && !NONE_PATTERN.test(line))
}

function findKeyValue(values: Map<string, string>, aliases: string[]): string {
  for (const alias of aliases) {
    const value = values.get(normalizeKey(alias))
    if (value) {
      return value
    }
  }
  return ''
}

function parseNullableInteger(value: string): number | null {
  const match = value.match(/\d+/)
  return match ? Number.parseInt(match[0], 10) : null
}

function normalizeKey(value: string): string {
  return value.trim().toLowerCase().replace(/\s+/g, ' ')
}

function fallbackDocumentType(sourceKind: MessageKind): string {
  if (sourceKind === 'design_doc') {
    return 'Design'
  }
  if (sourceKind === 'prd_doc') {
    return 'PRD'
  }
  return 'Document'
}

// --- structured API payload (preferred over reparsing the document Markdown) -------

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function asString(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return []
  }
  return value.map((item) => (typeof item === 'string' ? item.trim() : '')).filter(Boolean)
}

function asIntOrNull(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? Math.trunc(value) : null
}

/**
 * Map the backend ``document_qa_state`` payload to the typed {@link DocumentQaState}.
 * Returns null when no document QA is available (no generated document yet), which
 * matches the absence-of-key the backend emits for that case.
 */
export function documentQaStateFromApi(raw: unknown): DocumentQaState | null {
  if (!isRecord(raw)) {
    return null
  }
  const sourceKind: MessageKind = raw.source_kind === 'design_doc' ? 'design_doc' : 'prd_doc'
  const counts = isRecord(raw.classification_counts) ? raw.classification_counts : {}
  return {
    sourceKind,
    documentType: asString(raw.document_type) || fallbackDocumentType(sourceKind),
    demoReadiness: asString(raw.demo_readiness) || 'Unknown',
    productionReadiness: asString(raw.production_readiness) || 'Unknown',
    openQuestionCount: asIntOrNull(raw.open_question_count),
    productionBlockers: asStringArray(raw.production_blockers),
    businessRuleFindings: asStringArray(raw.business_rule_findings),
    implementationFindings: asStringArray(raw.implementation_findings),
    classificationCounts: {
      blockingForProduction: asIntOrNull(counts.blocking_for_production),
      okForDemo: asIntOrNull(counts.ok_for_demo),
      implementationAssumptions: asIntOrNull(counts.implementation_assumptions),
      needsReview: asIntOrNull(counts.needs_review),
    },
  }
}

/** Read ``document_qa_state`` out of a structured-requirement API payload. */
export function extractDocumentQaState(payload: unknown): DocumentQaState | null {
  if (!isRecord(payload)) {
    return null
  }
  return documentQaStateFromApi(payload.document_qa_state)
}
