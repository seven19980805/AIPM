import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  buildGoCodingTargetUrl,
  closeGoCodingWindow,
  isGoCodingTargetReachable,
  navigateGoCodingWindow,
  reserveGoCodingWindow,
} from './goCodingWindow.ts'


test('builds the coding URL without dropping existing query parameters', () => {
  const target = new URL(
    buildGoCodingTargetUrl(
      'http://localhost:8888/workspace?theme=dark',
      'hf_token',
      'http://127.0.0.1:8002',
    ),
  )

  assert.equal(target.pathname, '/workspace')
  assert.equal(target.searchParams.get('theme'), 'dark')
  assert.equal(target.searchParams.get('source'), 'rqmd')
  assert.equal(target.searchParams.get('handoff_token'), 'hf_token')
  assert.equal(target.searchParams.get('pm_api_base_url'), 'http://127.0.0.1:8002')
})

test('reserves a window synchronously and detaches its opener', () => {
  const popup = {
    opener: { name: 'parent' },
    location: { replace() {} },
    close() {},
  }
  const calls = []

  const result = reserveGoCodingWindow((...args) => {
    calls.push(args)
    return popup
  })

  assert.equal(result, popup)
  assert.equal(popup.opener, null)
  assert.deepEqual(calls, [['about:blank', '_blank']])
})

test('reports a blocked popup without trying to navigate it', () => {
  assert.equal(reserveGoCodingWindow(() => null), null)
})

test('checks that the configured coding workspace is reachable', async () => {
  const calls = []
  const reachable = await isGoCodingTargetReachable(
    'http://localhost:5173/workspace',
    async (...args) => {
      calls.push(args)
      return {}
    },
  )

  assert.equal(reachable, true)
  assert.equal(calls.length, 1)
  assert.equal(calls[0][0], 'http://localhost:5173/workspace')
  assert.equal(calls[0][1].method, 'HEAD')
  assert.equal(calls[0][1].mode, 'no-cors')
})

test('treats a network failure as an unavailable coding workspace', async () => {
  const reachable = await isGoCodingTargetReachable(
    'http://localhost:5173',
    async () => {
      throw new TypeError('fetch failed')
    },
  )

  assert.equal(reachable, false)
})

test('navigates or closes the already-reserved coding window', () => {
  const events = []
  const popup = {
    opener: null,
    location: {
      replace(url) {
        events.push(['replace', url])
      },
    },
    close() {
      events.push(['close'])
    },
  }

  navigateGoCodingWindow(popup, 'http://localhost:8888/?handoff_token=hf_token')
  closeGoCodingWindow(popup)

  assert.deepEqual(events, [
    ['replace', 'http://localhost:8888/?handoff_token=hf_token'],
    ['close'],
  ])
})
