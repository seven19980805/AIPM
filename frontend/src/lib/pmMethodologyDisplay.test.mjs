import assert from 'node:assert/strict'
import { test } from 'node:test'

import { summarizePMMethodologyDisplay } from './pmMethodologyDisplay.ts'

const checks = [
  {
    key: 'priority',
    label: 'Priority and scope trade-offs',
    method: 'Prioritization framework',
    status: 'partial',
    ready: false,
    evidence: ['P0 dashboard scope captured'],
    missing: ['Explicit out-of-scope trade-off'],
    next_question: 'Which part is P0 for the first release?',
  },
  {
    key: 'outcome',
    label: 'Outcome, opportunity, solution',
    method: 'Opportunity Solution Tree',
    status: 'ready',
    ready: true,
    evidence: ['Enable weekly yield review'],
    missing: [],
    next_question: '',
  },
]

test('ready structured gate makes methodology gaps advisory in the panel', () => {
  const display = summarizePMMethodologyDisplay(
    {
      version: '1',
      score: 91,
      ready_for_pm_review: false,
      recommended_next_method: 'priority',
      missing_evidence: ['Priority and scope trade-offs'],
      checks,
      prompt_guidance: [],
    },
    true,
  )

  assert.equal(display.readyCount, 2)
  assert.equal(display.missingCount, 0)
  assert.equal(display.showNextQuestions, false)
  assert.deepEqual(
    display.checks.map((check) => check.key),
    ['outcome'],
  )
})

test('collecting structured gate still surfaces methodology gaps as quality hints', () => {
  const display = summarizePMMethodologyDisplay(
    {
      version: '1',
      score: 91,
      ready_for_pm_review: false,
      recommended_next_method: 'priority',
      missing_evidence: ['Priority and scope trade-offs'],
      checks,
      prompt_guidance: [],
    },
    false,
  )

  assert.equal(display.readyCount, 1)
  assert.equal(display.missingCount, 1)
  assert.equal(display.showNextQuestions, true)
  assert.deepEqual(
    display.checks.map((check) => check.key),
    ['priority', 'outcome'],
  )
})
