import type {
  RequirementCollectionStatus,
  StructuredRequirementModel,
} from '../types/structuredRequirement'

export type StructuredRequirementProgress = {
  totalCount: number
  confirmedCount: number
  collectedCount: number
  pendingConfirmationCount: number
  conflictCount: number
  openQuestionCount: number
  pendingQuestionCount: number
  blockingQuestionCount: number
  fullyConfirmed: boolean
}

const REQUIREMENT_KEYS = [
  'objective',
  'scope',
  'users',
  'scenarios',
  'features',
  'pages',
  'rules',
  'integrations',
  'acceptance',
] as const

const REQUIRED_KEYS = REQUIREMENT_KEYS.filter((key) => key !== 'pages')

export function computeStructuredRequirementProgress(
  model: StructuredRequirementModel,
): StructuredRequirementProgress {
  const statusByKey = REQUIREMENT_KEYS.map((key) => ({
    key,
    status: model.collection_status[key]?.status ?? 'missing',
  }))
  const statuses = statusByKey.map((item) => item.status)
  const totalCount = statuses.length
  const confirmedCount = countStatuses(statuses, 'confirmed')
  const collectedCount = statuses.filter((status) => status !== 'missing').length
  const conflictCount = countStatuses(statuses, 'conflict')
  const pendingConfirmationCount = statuses.filter(
    (status) => status !== 'missing' && status !== 'confirmed' && status !== 'conflict',
  ).length
  const openQuestionCount = model.open_questions.filter((item) => item.trim()).length
  const pendingQuestionCount = REQUIREMENT_KEYS.reduce(
    (sum, key) =>
      sum + (model.collection_status[key]?.pending_questions ?? []).filter((item) => item.trim()).length,
    0,
  )
  // Top-level open_questions are PRD caveats/notes. They should be visible in
  // previews, but they must not keep the interview circling once every
  // structured requirement item is confirmed.
  const blockingQuestionCount = REQUIRED_KEYS.reduce(
    (sum, key) =>
      sum + (model.collection_status[key]?.pending_questions ?? []).filter((item) => item.trim()).length,
    0,
  )
  const fullyConfirmed =
    totalCount > 0 &&
    confirmedCount === totalCount &&
    conflictCount === 0 &&
    pendingQuestionCount === 0
  return {
    totalCount,
    confirmedCount,
    collectedCount,
    pendingConfirmationCount,
    conflictCount,
    openQuestionCount,
    pendingQuestionCount,
    blockingQuestionCount,
    fullyConfirmed,
  }
}

function countStatuses(
  statuses: RequirementCollectionStatus[],
  target: RequirementCollectionStatus,
): number {
  return statuses.filter((status) => status === target).length
}
