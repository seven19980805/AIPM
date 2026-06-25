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
  readinessPercentage: number
  collectionCoveragePercentage: number
  confirmationPercentage: number
  fullyConfirmed: boolean
  readyToGenerate: boolean
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

type RequirementProgressKey = (typeof REQUIREMENT_KEYS)[number]

const REQUIREMENT_WEIGHTS: Record<RequirementProgressKey, number> = {
  objective: 1.2,
  scope: 1,
  users: 1,
  scenarios: 1.1,
  features: 1.4,
  pages: 0.8,
  rules: 1.2,
  integrations: 0.8,
  acceptance: 1.5,
}

const STATUS_READINESS_POINTS: Record<RequirementCollectionStatus, number> = {
  missing: 0,
  captured: 0.2,
  pending_confirmation: 0.35,
  confirmed: 1,
  conflict: 0,
}

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
  const blockingQuestionCount = pendingQuestionCount
  const collectionCoveragePercentage = totalCount
    ? Math.round((collectedCount / totalCount) * 100)
    : 0
  const confirmationPercentage = totalCount
    ? Math.round((confirmedCount / totalCount) * 100)
    : 0
  const fullyConfirmed =
    totalCount > 0 &&
    confirmedCount === totalCount &&
    conflictCount === 0 &&
    blockingQuestionCount === 0
  const totalWeight = REQUIREMENT_KEYS.reduce((sum, key) => sum + REQUIREMENT_WEIGHTS[key], 0)
  const earnedWeight = statusByKey.reduce(
    (sum, item) => sum + REQUIREMENT_WEIGHTS[item.key] * STATUS_READINESS_POINTS[item.status],
    0,
  )
  let readinessPercentage = totalWeight ? Math.round((earnedWeight / totalWeight) * 100) : 0

  if (fullyConfirmed) {
    readinessPercentage = 100
  } else if (conflictCount > 0) {
    readinessPercentage = Math.min(readinessPercentage, 69)
  } else if (pendingConfirmationCount > 0 || blockingQuestionCount > 0) {
    readinessPercentage = Math.min(readinessPercentage, 94)
  }
  // Formal-document gate (kept in sync with backend _structured_requirement_progress):
  // every structured requirement item must be confirmed. Field-level pending
  // questions keep the interview going; top-level open_questions are carried as
  // PRD caveats rather than hard blockers.
  const readyToGenerate = fullyConfirmed

  return {
    totalCount,
    confirmedCount,
    collectedCount,
    pendingConfirmationCount,
    conflictCount,
    openQuestionCount,
    pendingQuestionCount,
    blockingQuestionCount,
    readinessPercentage,
    collectionCoveragePercentage,
    confirmationPercentage,
    fullyConfirmed,
    readyToGenerate,
  }
}

function countStatuses(
  statuses: RequirementCollectionStatus[],
  target: RequirementCollectionStatus,
): number {
  return statuses.filter((status) => status === target).length
}
