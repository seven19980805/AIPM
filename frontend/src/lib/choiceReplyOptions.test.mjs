import assert from 'node:assert/strict'
import { test } from 'node:test'

import { extractChoiceReplyOptions } from './choiceReplyOptions.ts'

test('extracts inline A/B/C/D options without merging C and D', () => {
  const content = [
    'Now, for the first release scope (P0 vs out-of-scope), which best describes what must ship?',
    '',
    'A. Display only the current shift’s output per operator, with no targets, trends, or drill-down.  B. Display output per operator plus a target/plan, and highlight operators below target.  C. Include shift-to-shift trend and a simple drill-down to operator details.  D.',
    'Something else — please describe.',
    '',
    'This helps us set the MVP boundary and decide what data tables and calculations are required for v1.',
  ].join('\n')

  const options = extractChoiceReplyOptions(content)

  assert.deepEqual(
    options.map((option) => option.key),
    ['A', 'B', 'C', 'D'],
  )
  assert.equal(options[2].label, 'Include shift-to-shift trend and a simple drill-down to operator details.')
  assert.equal(options[3].label, 'Something else — please describe.')
})

test('keeps regular multiline A/B/C options unchanged', () => {
  const content = [
    'Choose one option:',
    'A. Confirm the suggested scope',
    'B. Provide the real business wording',
    'C. Keep this point pending for now',
  ].join('\n')

  const options = extractChoiceReplyOptions(content)

  assert.deepEqual(
    options.map((option) => option.value),
    [
      'A. Confirm the suggested scope',
      'B. Provide the real business wording',
      'C. Keep this point pending for now',
    ],
  )
})
