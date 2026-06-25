import assert from 'node:assert/strict'
import { test } from 'node:test'

import { computeStructuredRequirementProgress } from './structuredRequirementProgress.ts'

const requirementKeys = [
  'objective',
  'scope',
  'users',
  'scenarios',
  'features',
  'pages',
  'rules',
  'integrations',
  'acceptance',
]

function confirmedModel(overrides = {}) {
  return {
    collection_status: Object.fromEntries(
      requirementKeys.map((key) => [
        key,
        { status: 'confirmed', reason: 'Confirmed.', pending_questions: [] },
      ]),
    ),
    open_questions: [],
    ...overrides,
  }
}

test('top-level open questions do not block generation readiness', () => {
  const progress = computeStructuredRequirementProgress(
    confirmedModel({
      open_questions: ['Confirm API auth details in implementation planning.'],
    }),
  )

  assert.equal(progress.openQuestionCount, 1)
  assert.equal(progress.blockingQuestionCount, 0)
  assert.equal(progress.fullyConfirmed, true)
  assert.equal(progress.readyToGenerate, true)
  assert.equal(progress.readinessPercentage, 100)
})

test('field-level pending questions still block generation readiness', () => {
  const model = confirmedModel()
  model.collection_status.acceptance = {
    status: 'confirmed',
    reason: 'Acceptance exists but owner still must confirm.',
    pending_questions: ['Confirm acceptance owner.'],
  }

  const progress = computeStructuredRequirementProgress(model)

  assert.equal(progress.openQuestionCount, 0)
  assert.equal(progress.blockingQuestionCount, 1)
  assert.equal(progress.fullyConfirmed, false)
  assert.equal(progress.readyToGenerate, false)
})
