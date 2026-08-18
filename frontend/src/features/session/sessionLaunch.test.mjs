import assert from 'node:assert/strict'
import { test } from 'node:test'

import { extractSessionLaunchContext } from './sessionLaunch.ts'
import * as sessionLaunch from './sessionLaunch.ts'


test('normalizes a backend launch context without trusting malformed items', () => {
  const context = extractSessionLaunchContext(
    {
      session_id: 'session-1',
      title: 'Template session',
      prompt_template: 'personal_project',
      applied_template_id: 'template-1',
      applied_template_name: 'Quality template',
      created_at: '',
      updated_at: '',
      messages: [],
      launch_context: {
        version: 1,
        mode: 'template',
        status: 'not_started',
        title: 'Quality template',
        description: 'Template guidance',
        question: 'Confirm the first quality decision',
        stages: [
          { key: 'scope', track: 'Quality', label: 'Confirm scope', status: 'current' },
          { key: '', track: 'Quality', label: 'Bad item', status: 'pending' },
        ],
        suggestions: [
          { id: 'quality', label: 'Quality', text: 'Quality: improve release review.' },
          { id: 'bad', label: '', text: '' },
        ],
        source: {
          type: 'template',
          id: 'template-1',
          name: 'Quality template',
          version: '1.0',
          language: 'en',
          start_function: 'from_scratch',
        },
      },
    },
    'en',
  )

  assert.equal(context.mode, 'template')
  assert.equal(context.question, 'Confirm the first quality decision')
  assert.equal(context.stages.length, 1)
  assert.equal(context.suggestions.length, 1)
})

test('reconstructs a useful template launch for an older backend response', () => {
  const context = extractSessionLaunchContext(
    {
      session_id: 'session-2',
      title: 'Old session',
      prompt_template: 'personal_project',
      applied_template_id: 'legacy-template',
      applied_template_name: 'Legacy process template',
      created_at: '',
      updated_at: '',
      messages: [],
      conversation_chain_state: {
        enabled: true,
        mode: 'template',
        current_node: 'objective',
        current_node_label: 'Confirm objective',
        status: 'not_started',
        nodes: [
          {
            track: 'Background',
            node: 'objective',
            label: 'Confirm objective',
            status: 'current',
          },
        ],
      },
    },
    'en',
  )

  assert.equal(context.mode, 'template')
  assert.equal(context.title, 'Legacy process template')
  assert.equal(context.question, 'Confirm objective')
  assert.equal(context.stages[0].key, 'objective')
  assert.equal(context.source.type, 'template')
})

test('gives a plain Chinese session a concrete first question and data-aware starters', () => {
  const context = extractSessionLaunchContext(
    {
      session_id: 'session-3',
      title: '',
      prompt_template: 'personal_project',
      applied_template_id: '',
      applied_template_name: '',
      created_at: '',
      updated_at: '',
      messages: [],
    },
    'zh',
  )

  assert.equal(context.mode, 'scratch')
  assert.match(context.question, /业务动作/)
  assert.ok(context.suggestions.some((item) => item.text.includes('SQL Server')))
  assert.ok(context.suggestions.some((item) => item.text.includes('SAP')))
  assert.ok(context.suggestions.some((item) => item.text.includes('Excel/CSV')))
})

test('same-session detail sync preserves accumulated workspace progress', () => {
  assert.equal(typeof sessionLaunch.shouldResetSessionWorkspace, 'function')
  assert.equal(sessionLaunch.shouldResetSessionWorkspace('session-1', 'session-1'), false)
  assert.equal(sessionLaunch.shouldResetSessionWorkspace('session-1', 'session-2'), true)
  assert.equal(sessionLaunch.shouldResetSessionWorkspace('', 'session-1'), true)
})
