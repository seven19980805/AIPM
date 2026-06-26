import assert from 'node:assert/strict'
import { test } from 'node:test'

import { documentQaStateFromApi, extractDocumentQaState } from './documentQa.ts'

test('maps the structured API payload (snake_case) to DocumentQaState', () => {
  const qa = documentQaStateFromApi({
    source_kind: 'design_doc',
    document_type: 'Design',
    demo_readiness: 'Ready with assumptions',
    production_readiness: 'Blocked',
    open_question_count: 2,
    production_blockers: ['Real MES integration is not yet specified.'],
    business_rule_findings: [],
    implementation_findings: ['Mock/demo data is acceptable for prototype validation only.'],
    classification_counts: {
      blocking_for_production: 0,
      ok_for_demo: 1,
      implementation_assumptions: 0,
      needs_review: 1,
    },
    // extra renderer-only fields must be ignored even if the backend ever sends them
    classified_questions: { blocking_for_production: [] },
    readiness_percentage: 100,
  })

  assert.equal(qa?.sourceKind, 'design_doc')
  assert.equal(qa?.documentType, 'Design')
  assert.equal(qa?.productionReadiness, 'Blocked')
  assert.equal(qa?.openQuestionCount, 2)
  assert.deepEqual(qa?.productionBlockers, ['Real MES integration is not yet specified.'])
  assert.equal(qa?.implementationFindings.length, 1)
  assert.equal(qa?.classificationCounts.needsReview, 1)
})

test('extractDocumentQaState returns null when no document QA is present', () => {
  assert.equal(extractDocumentQaState({ pm_methodology_state: {} }), null)
  assert.equal(extractDocumentQaState({ document_qa_state: null }), null)
  assert.equal(extractDocumentQaState(null), null)
  // present payload is mapped
  const qa = extractDocumentQaState({ document_qa_state: { source_kind: 'prd_doc', production_readiness: 'Ready' } })
  assert.equal(qa?.sourceKind, 'prd_doc')
  assert.equal(qa?.productionReadiness, 'Ready')
})
