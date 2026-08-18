import assert from 'node:assert/strict'
import { test } from 'node:test'


let languagePreference = {}
try {
  languagePreference = await import('./languagePreference.ts')
} catch {
  // The first TDD run intentionally reaches this branch before the module exists.
}


function createMemoryStorage(initial = {}) {
  const values = new Map(Object.entries(initial))
  return {
    getItem(key) {
      return values.has(key) ? values.get(key) : null
    },
    setItem(key, value) {
      values.set(key, String(value))
    },
  }
}


test('persists and restores the selected supported language', () => {
  assert.equal(typeof languagePreference.loadLanguagePreference, 'function')
  assert.equal(typeof languagePreference.saveLanguagePreference, 'function')

  const storage = createMemoryStorage()
  languagePreference.saveLanguagePreference(storage, 'zh')

  assert.equal(languagePreference.loadLanguagePreference(storage), 'zh')
})


test('falls back to English for missing or unsupported language values', () => {
  assert.equal(typeof languagePreference.loadLanguagePreference, 'function')

  assert.equal(languagePreference.loadLanguagePreference(createMemoryStorage()), 'en')
  assert.equal(
    languagePreference.loadLanguagePreference(
      createMemoryStorage({ 'ats-aipm-language': 'fr' }),
    ),
    'en',
  )
})
