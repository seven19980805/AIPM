import assert from 'node:assert/strict'
import { test } from 'node:test'


let sessionLanguageSync = {}
try {
  sessionLanguageSync = await import('./sessionLanguageSync.ts')
} catch {
  // The first TDD run intentionally reaches this branch before the module exists.
}


function deferred() {
  let resolve
  let reject
  const promise = new Promise((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}


function recordingPatch(result = { ok: true }) {
  const calls = []
  const patch = async (sessionId, language) => {
    calls.push({ sessionId, language })
    return result
  }
  patch.calls = calls
  return patch
}


test('a session language is only persisted when the user changes it', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const patch = recordingPatch()
  const sync = createSessionLanguageSync(patch)

  const unchanged = await sync({
    sessionId: 'session-1',
    language: 'en',
    serverLanguage: 'en',
  })

  assert.deepEqual(unchanged, { status: 'skipped', reason: 'unchanged' })
  assert.equal(patch.calls.length, 0)
})


test('loading a session without an explicit switch never writes', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const patch = recordingPatch()
  const sync = createSessionLanguageSync(patch)

  const outcome = await sync({
    sessionId: '',
    language: 'zh',
    serverLanguage: 'en',
  })

  assert.deepEqual(outcome, { status: 'skipped', reason: 'no-session' })
  assert.equal(patch.calls.length, 0)
})


test('an explicit switch patches the session language', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const patch = recordingPatch({ session_id: 'session-1', language: 'zh' })
  const sync = createSessionLanguageSync(patch)

  const outcome = await sync({
    sessionId: 'session-1',
    language: 'zh',
    serverLanguage: 'en',
  })

  assert.deepEqual(patch.calls, [{ sessionId: 'session-1', language: 'zh' }])
  assert.equal(outcome.status, 'applied')
  assert.equal(outcome.language, 'zh')
  assert.deepEqual(outcome.detail, { session_id: 'session-1', language: 'zh' })
})


test('a failed switch reverts to the language the server still holds', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const failure = new Error('network down')
  const sync = createSessionLanguageSync(async () => {
    throw failure
  })

  const outcome = await sync({
    sessionId: 'session-1',
    language: 'zh',
    serverLanguage: 'de',
  })

  assert.equal(outcome.status, 'failed')
  assert.equal(outcome.revertTo, 'de')
  assert.equal(outcome.error, failure)
})


test('rapid switching applies only the latest choice', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const first = deferred()
  const second = deferred()
  const pending = [first, second]
  const sync = createSessionLanguageSync(() => pending.shift().promise)

  const slow = sync({ sessionId: 's', language: 'zh', serverLanguage: 'en' })
  const fast = sync({ sessionId: 's', language: 'de', serverLanguage: 'en' })

  second.resolve({ language: 'de' })
  first.resolve({ language: 'zh' })

  assert.equal((await fast).status, 'applied')
  assert.equal((await fast).language, 'de')
  assert.equal((await slow).status, 'stale')
})


test('a superseded failure never clobbers a newer selection', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const first = deferred()
  const second = deferred()
  const pending = [first, second]
  const sync = createSessionLanguageSync(() => pending.shift().promise)

  const slow = sync({ sessionId: 's', language: 'zh', serverLanguage: 'en' })
  const fast = sync({ sessionId: 's', language: 'de', serverLanguage: 'en' })

  second.resolve({ language: 'de' })
  first.reject(new Error('too late'))

  assert.equal((await fast).status, 'applied')
  const stale = await slow
  assert.equal(stale.status, 'stale')
  assert.equal(stale.revertTo, undefined)
})


test('an older session that rejects the endpoint still reverts cleanly', async () => {
  const { createSessionLanguageSync } = sessionLanguageSync
  const notFound = new Error('Session not found.')
  const sync = createSessionLanguageSync(async () => {
    throw notFound
  })

  const outcome = await sync({
    sessionId: 'legacy-session',
    language: 'ms',
    serverLanguage: 'en',
  })

  assert.equal(outcome.status, 'failed')
  assert.equal(outcome.revertTo, 'en')
})
