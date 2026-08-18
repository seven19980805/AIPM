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

test('reports exact field counts without inventing a readiness score', () => {
  const progress = computeStructuredRequirementProgress(
    confirmedModel({
      open_questions: ['Confirm API auth details in implementation planning.'],
    }),
  )

  assert.equal(progress.openQuestionCount, 1)
  assert.equal(progress.blockingQuestionCount, 0)
  assert.equal(progress.fullyConfirmed, true)
  assert.equal(progress.confirmedCount, 9)
  assert.equal(progress.totalCount, 9)
  assert.equal('readyToGenerate' in progress, false)
  assert.equal('readinessPercentage' in progress, false)
})

test('field-level pending questions keep the detail snapshot unconfirmed', () => {
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
})

test('page layout stays visible in detail counts without becoming an action gate', () => {
  const model = confirmedModel()
  model.collection_status.pages = {
    status: 'missing',
    reason: 'Derive screens from workflow and features.',
    pending_questions: ['Confirm exact layout later.'],
  }

  const progress = computeStructuredRequirementProgress(model)

  assert.equal(progress.fullyConfirmed, false)
  assert.equal(progress.blockingQuestionCount, 0)
  assert.equal(progress.confirmedCount, 8)
  assert.equal(progress.totalCount, 9)
})
