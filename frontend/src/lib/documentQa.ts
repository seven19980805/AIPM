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

function fallbackDocumentType(sourceKind: MessageKind): string {
  if (sourceKind === 'design_doc') {
    return 'Design'
  }
  if (sourceKind === 'prd_doc') {
    return 'PRD'
  }
  return 'Document'
}

// --- structured API payload (the document QA card is driven entirely by this) ------

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
