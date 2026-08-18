import assert from 'node:assert/strict'
import { test } from 'node:test'

import { buildTemplateSessionRequest } from './templateStart.ts'


test('builds an explicit guided template launch request', () => {
  assert.deepEqual(
    buildTemplateSessionRequest('  quality-template  ', 'en', {
      businessRoute: 'quality',
    }),
    {
      language: 'en',
      template_id: 'quality-template',
      template_start_mode: 'guided',
      intake_mode: 'template',
      business_route: 'quality',
      start_function: 'from_scratch',
    },
  )
})

test('template launch remains separate from draft completion mode', () => {
  assert.deepEqual(
    buildTemplateSessionRequest('quality-template', 'zh', {
      businessRoute: 'quality',
    }),
    {
      language: 'zh',
      template_id: 'quality-template',
      template_start_mode: 'guided',
      intake_mode: 'template',
      business_route: 'quality',
      start_function: 'from_scratch',
    },
  )
})

test('allows catalog templates outside the three IC Substrate routes', () => {
  assert.deepEqual(
    buildTemplateSessionRequest('finance-template', 'zh', {
      businessRoute: 'Finance Management',
    }),
    {
      language: 'zh',
      template_id: 'finance-template',
      template_start_mode: 'guided',
      start_function: 'from_scratch',
    },
  )
})

test('rejects an empty template id', () => {
  assert.throws(
    () => buildTemplateSessionRequest(' ', 'en'),
    /Template id is required/,
  )
})
