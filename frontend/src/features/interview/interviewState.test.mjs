import assert from 'node:assert/strict'
import { test } from 'node:test'

const interviewStateModule = await import('../../types/interviewState.ts').catch(() => ({}))

const {
  createEmptyInterviewState,
  extractInterviewState,
  normalizeInterviewState,
  shouldShowLegacyChoiceReplies,
} = interviewStateModule

const activeStatePayload = {
  schema_version: '2.0',
  stage: 'brief_discovery',
  brief: {
    confirmed_decisions: 1,
    total_decisions: 5,
    assumption_count: 1,
    ready: false,
    document_status: 'missing',
  },
  review: {
    remaining_count: 7,
    remaining_keys: ['rules', 'ownership'],
    ready: false,
    asked_count: 1,
    max_questions: 2,
    input_mode: 'question',
  },
  next_decision: {
    decision_id: 'actor_action',
    label: '用户与业务动作',
    question: '谁会使用它，并据此做什么决定？',
    hint: '例如：值班主管根据产品代码良率趋势安排复测。',
    mode: 'free_text',
    proposal: null,
    can_defer: true,
    options: [
      {
        option_id: 'actor-action-quality-1',
        text: '质量工程师根据缺陷趋势决定优先调查的产品和批次。',
      },
      {
        option_id: 'actor-action-quality-2',
        text: '质量主管根据待判批次和风险等级安排处置。',
      },
      {
        option_id: 'actor-action-quality-3',
        text: '检验员根据异常清单决定复检项目。',
      },
    ],
  },
  actions: {
    can_generate_brief: false,
    can_handoff: false,
  },
}

test('normalizes the authoritative V2 state without recomputing its progress', () => {
  assert.equal(typeof normalizeInterviewState, 'function')

  const state = normalizeInterviewState(activeStatePayload)

  assert.equal(state.schema_version, '2.0')
  assert.equal(state.brief.confirmed_decisions, 1)
  assert.equal(state.brief.total_decisions, 5)
  assert.equal(state.brief.assumption_count, 1)
  assert.equal(state.review.remaining_count, 7)
  assert.deepEqual(state.review.remaining_keys, ['rules', 'ownership'])
  assert.equal(state.review.asked_count, 1)
  assert.equal(state.review.max_questions, 2)
  assert.equal(state.review.input_mode, 'question')
  assert.equal(state.next_decision.decision_id, 'actor_action')
  assert.equal(state.next_decision.question, activeStatePayload.next_decision.question)
  assert.equal(state.next_decision.can_defer, true)
  assert.equal(state.next_decision.options.length, 3)
  assert.equal(state.next_decision.options[0].option_id, 'actor-action-quality-1')
})

test('extracts interview_state from session and SSE summary payloads', () => {
  assert.equal(typeof extractInterviewState, 'function')

  const extracted = extractInterviewState({ interview_state: activeStatePayload })

  assert.equal(extracted?.next_decision.decision_id, 'actor_action')
})

test('uses a safe empty state for legacy or malformed payloads', () => {
  assert.equal(typeof createEmptyInterviewState, 'function')

  const empty = createEmptyInterviewState()
  const malformed = normalizeInterviewState({ schema_version: '1.0', brief: null })

  assert.equal(empty.schema_version, '2.0')
  assert.equal(empty.brief.total_decisions, 5)
  assert.equal(malformed.next_decision, null)
  assert.equal(malformed.actions.can_generate_brief, false)
})

test('keeps legacy A/B/C rendering only when no V2 state is available', () => {
  assert.equal(typeof shouldShowLegacyChoiceReplies, 'function')
  assert.equal(shouldShowLegacyChoiceReplies(null), true)
  assert.equal(shouldShowLegacyChoiceReplies(normalizeInterviewState(activeStatePayload)), false)
})
