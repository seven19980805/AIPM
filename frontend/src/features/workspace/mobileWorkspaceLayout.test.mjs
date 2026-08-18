import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

test('keeps the wrapping top bar from shrinking into the conversation on mobile', async () => {
  const app = await readFile(new URL('../../App.vue', import.meta.url), 'utf8')
  const topbarRule = app.match(/\.main-topbar\s*\{([^}]*)\}/)?.[1] ?? ''

  assert.match(topbarRule, /flex:\s*0 0 auto;/)
})
