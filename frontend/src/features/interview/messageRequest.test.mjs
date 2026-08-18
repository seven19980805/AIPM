import assert from 'node:assert/strict'
import { test } from 'node:test'

const messageRequestModule = await import('./messageRequest.ts').catch(() => ({}))
const { buildMessageRequestBody } = messageRequestModule

test('keeps the legacy text request shape when reply_context is absent', () => {
  assert.equal(typeof buildMessageRequestBody, 'function')

  assert.deepEqual(
    buildMessageRequestBody({
      message: 'The shift supervisor uses it.',
      displayMessage: 'The shift supervisor uses it.',
      language: 'en',
    }),
    {
      message: 'The shift supervisor uses it.',
      display_message: 'The shift supervisor uses it.',
      language: 'en',
    },
  )
})
test('adds only proposal identifiers to structured replies', () => {
  assert.equal(typeof buildMessageRequestBody, 'function')

  const body = buildMessageRequestBody({
    message: '采用这个提案',
    displayMessage: '采用这个提案',
    language: 'zh',
    replyContext: {
      decision_id: 'outcome',
      action: 'accept_proposal',
      proposal_id: 'proposal-42',
    },
  })

  assert.deepEqual(body.reply_context, {
    decision_id: 'outcome',
    action: 'accept_proposal',
    proposal_id: 'proposal-42',
  })
  assert.equal('proposal' in body.reply_context, false)
})
