import assert from 'node:assert/strict'
import { test } from 'node:test'

import * as structuredRequirement from '../types/structuredRequirement.ts'
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

test('methodology progress does not regress when a later extraction drops prior evidence', () => {
  const mergePMMethodologyState = structuredRequirement.mergePMMethodologyState
  assert.equal(typeof mergePMMethodologyState, 'function')

  const previous = {
    version: '1',
    score: 91,
    ready_for_pm_review: false,
    recommended_next_method: 'rules',
    missing_evidence: ['rules'],
    checks: [
      {
        key: 'outcome',
        label: 'Outcome',
        method: 'Opportunity Solution Tree',
        status: 'ready',
        ready: true,
        evidence: ['Planner outcome confirmed'],
        missing: [],
        next_question: '',
        source_methods: [],
      },
      {
        key: 'rules',
        label: 'Rules',
        method: 'Business rules',
        status: 'partial',
        ready: false,
        evidence: ['Formula pending'],
        missing: ['Formula'],
        next_question: 'Confirm the formula.',
        source_methods: [],
      },
    ],
    prompt_guidance: [],
  }
  const next = {
    ...previous,
    score: 83,
    checks: [
      {
        ...previous.checks[0],
        status: 'missing',
        ready: false,
        evidence: [],
        missing: ['Outcome'],
      },
      {
        ...previous.checks[1],
        status: 'ready',
        ready: true,
        evidence: ['Formula confirmed'],
        missing: [],
      },
    ],
  }

  const merged = mergePMMethodologyState(previous, next)

  assert.equal(merged.score, 91)
  assert.equal(merged.checks.find((check) => check.key === 'outcome').status, 'ready')
  assert.equal(merged.checks.find((check) => check.key === 'rules').status, 'ready')
})
