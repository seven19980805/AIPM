import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  BUSINESS_ROUTES,
  buildIntakeSessionRequest,
} from './intakeSession.ts'


test('exposes exactly the three production business routes', () => {
  assert.deepEqual(BUSINESS_ROUTES, ['production', 'quality', 'tdi'])
})

test('builds separate scratch and draft session contracts', () => {
  assert.deepEqual(
    buildIntakeSessionRequest('scratch', 'production', 'en'),
    {
      language: 'en',
      intake_mode: 'scratch',
      business_route: 'production',
      starter_department: 'production',
      start_function: 'from_scratch',
    },
  )
  assert.deepEqual(
    buildIntakeSessionRequest('draft', 'tdi', 'zh'),
    {
      language: 'zh',
      intake_mode: 'draft',
      business_route: 'tdi',
      starter_department: 'tdi',
      start_function: 'improve_draft',
    },
  )
})

test('rejects unsupported modes and routes', () => {
  assert.throws(
    () => buildIntakeSessionRequest('scratch', 'general', 'en'),
    /production, quality, or tdi/,
  )
  assert.throws(
    () => buildIntakeSessionRequest('template', 'quality', 'en'),
    /scratch or draft/,
  )
})
