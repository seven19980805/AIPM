export type InterviewStage =
  | 'brief_discovery'
  | 'brief_ready'
  | 'strict_review'
  | 'refresh_brief'
  | 'handoff_ready'

export type BriefDocumentStatus = 'missing' | 'current' | 'stale'
export type NextDecisionMode = 'free_text' | 'confirm_proposal'
export type ReviewInputMode = 'question' | 'manual' | 'complete'
export type InterviewReplyAction =
  | 'request_example'
  | 'accept_proposal'
  | 'defer_decision'

export type InterviewReplyContext = {
  decision_id: string
  action: InterviewReplyAction
  proposal_id?: string
}

export type InterviewProposal = {
  proposal_id: string
  text: string
}

export type InterviewAnswerOption = {
  option_id: string
  /** Full answer sent as the user's message; grounding depends on it. */
  text: string
  /** Short scannable label for the card. Falls back to `text`. */
  label?: string
}

export type InterviewNextDecision = {
  decision_id: string
  label: string
  question: string
  hint: string
  mode: NextDecisionMode
  proposal: InterviewProposal | null
  can_defer: boolean
  options: InterviewAnswerOption[]
}

export type InterviewStateV2 = {
  schema_version: '2.0'
  stage: InterviewStage
  brief: {
    confirmed_decisions: number
    total_decisions: number
    assumption_count: number
    ready: boolean
    document_status: BriefDocumentStatus
  }
  review: {
    remaining_count: number
    remaining_keys: string[]
    ready: boolean
    asked_count: number
    max_questions: number
    input_mode: ReviewInputMode
  }
  next_decision: InterviewNextDecision | null
  actions: {
    can_generate_brief: boolean
    can_handoff: boolean
  }
}

const stages = new Set<InterviewStage>([
  'brief_discovery',
  'brief_ready',
  'strict_review',
  'refresh_brief',
  'handoff_ready',
])
const documentStatuses = new Set<BriefDocumentStatus>(['missing', 'current', 'stale'])
const decisionModes = new Set<NextDecisionMode>(['free_text', 'confirm_proposal'])

export function createEmptyInterviewState(): InterviewStateV2 {
  return {
    schema_version: '2.0',
    stage: 'brief_discovery',
    brief: {
      confirmed_decisions: 0,
      total_decisions: 5,
      assumption_count: 0,
      ready: false,
      document_status: 'missing',
    },
    review: {
      remaining_count: 0,
      remaining_keys: [],
      ready: false,
      asked_count: 0,
      max_questions: 2,
      input_mode: 'question',
    },
    next_decision: null,
    actions: {
      can_generate_brief: false,
      can_handoff: false,
    },
  }
}

export function normalizeInterviewState(payload: unknown): InterviewStateV2 {
  const empty = createEmptyInterviewState()
  const root = asRecord(payload)
  if (asString(root.schema_version) !== '2.0') {
    return empty
  }

  const brief = asRecord(root.brief)
  const review = asRecord(root.review)
  const actions = asRecord(root.actions)
  const rawStage = asString(root.stage) as InterviewStage
  const rawDocumentStatus = asString(brief.document_status) as BriefDocumentStatus

  return {
    schema_version: '2.0',
    stage: stages.has(rawStage) ? rawStage : empty.stage,
    brief: {
      confirmed_decisions: asNonNegativeInteger(brief.confirmed_decisions),
      total_decisions: asPositiveInteger(brief.total_decisions, 5),
      assumption_count: asNonNegativeInteger(brief.assumption_count),
      ready: Boolean(brief.ready),
      document_status: documentStatuses.has(rawDocumentStatus)
        ? rawDocumentStatus
        : empty.brief.document_status,
    },
    review: {
      remaining_count: asNonNegativeInteger(review.remaining_count),
      remaining_keys: asStringList(review.remaining_keys),
      ready: Boolean(review.ready),
      asked_count: asNonNegativeInteger(review.asked_count),
      max_questions: asPositiveInteger(review.max_questions, 2),
      input_mode:
        review.input_mode === 'manual' || review.input_mode === 'complete'
          ? review.input_mode
          : 'question',
    },
    next_decision: normalizeNextDecision(root.next_decision),
    actions: {
      can_generate_brief: Boolean(actions.can_generate_brief),
      can_handoff: Boolean(actions.can_handoff),
    },
  }
}

export function extractInterviewState(payload: unknown): InterviewStateV2 | null {
  const root = asRecord(payload)
  if (root.interview_state !== undefined) {
    return normalizeInterviewState(root.interview_state)
  }

  const summary = asRecord(root.summary)
  if (summary.interview_state !== undefined) {
    return normalizeInterviewState(summary.interview_state)
  }
  return null
}

export function shouldShowLegacyChoiceReplies(state: InterviewStateV2 | null): boolean {
  return state === null
}

function normalizeNextDecision(value: unknown): InterviewNextDecision | null {
  const decision = asRecord(value)
  const decisionId = asString(decision.decision_id)
  const question = asString(decision.question)
  if (!decisionId || !question) {
    return null
  }

  const rawMode = asString(decision.mode) as NextDecisionMode
  return {
    decision_id: decisionId,
    label: asString(decision.label),
    question,
    hint: asString(decision.hint),
    mode: decisionModes.has(rawMode) ? rawMode : 'free_text',
    proposal: normalizeProposal(decision.proposal),
    can_defer: Boolean(decision.can_defer),
    options: normalizeAnswerOptions(decision.options),
  }
}

function normalizeAnswerOptions(value: unknown): InterviewAnswerOption[] {
  if (!Array.isArray(value)) return []
  return value
    .map((item) => {
      const option = asRecord(item)
      return {
        option_id: asString(option.option_id),
        text: asString(option.text),
      }
    })
    .filter((option) => option.option_id && option.text)
    .slice(0, 3)
}

function normalizeProposal(value: unknown): InterviewProposal | null {
  const proposal = asRecord(value)
  const proposalId = asString(proposal.proposal_id)
  const text = asString(proposal.text || proposal.content || proposal.summary)
  if (!proposalId || !text) {
    return null
  }
  return {
    proposal_id: proposalId,
    text,
  }
}

function asRecord(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {}
}

function asString(value: unknown): string {
  return typeof value === 'string' ? value.trim() : ''
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return []
  return value
    .map((item) => asString(item))
    .filter(Boolean)
}

function asNonNegativeInteger(value: unknown): number {
  const number = typeof value === 'number' ? value : Number(value)
  return Number.isFinite(number) ? Math.max(0, Math.trunc(number)) : 0
}

function asPositiveInteger(value: unknown, fallback: number): number {
  const number = asNonNegativeInteger(value)
  return number > 0 ? number : fallback
}
