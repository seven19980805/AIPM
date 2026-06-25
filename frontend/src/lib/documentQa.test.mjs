import assert from 'node:assert/strict'
import { test } from 'node:test'

import { parseDocumentQa, documentQaStateFromApi, extractDocumentQaState } from './documentQa.ts'

test('parses English document QA appendix', () => {
  const markdown = [
    '# System Design Document',
    '',
    'Body.',
    '',
    '## Document QA',
    '',
    '- **Document type**: Design',
    '- **System-counted open questions**: 6',
    '- **Demo readiness**: Ready with assumptions',
    '- **Production readiness**: Blocked',
    '',
    '### Production Blockers',
    '- Real MES integration is not yet specified; mock/demo data is only enough for prototype delivery.',
    '',
    '### Open Question Classification',
    '- **Blocking for production**: 4',
    '- Which MES API or database view provides the data?',
    '- **OK for demo / polish later**: 2',
    '- Are there any branding constraints?',
    '- **Implementation assumptions**: 1',
    '- C# + SQLite default stack',
    '- **Needs review**: 0',
    '- None',
    '',
    '### Business Rule Sanity Checks',
    '- Behind-schedule rule may be wrong for mid-shift use.',
    '',
    '### Implementation Assumption Checks',
    '- Technology stack appears to be a system default or demo assumption.',
  ].join('\n')

  const qa = parseDocumentQa(markdown, 'design_doc')

  assert.equal(qa?.documentType, 'Design')
  assert.equal(qa?.openQuestionCount, 6)
  assert.equal(qa?.demoReadiness, 'Ready with assumptions')
  assert.equal(qa?.productionReadiness, 'Blocked')
  assert.equal(qa?.classificationCounts.blockingForProduction, 4)
  assert.equal(qa?.productionBlockers.length, 1)
  assert.equal(qa?.businessRuleFindings[0], 'Behind-schedule rule may be wrong for mid-shift use.')
  assert.equal(
    qa?.implementationFindings[0],
    'Technology stack appears to be a system default or demo assumption.',
  )
})

test('parses Chinese document QA appendix', () => {
  const markdown = [
    '# 需求文档',
    '',
    '## 文档质量检查 / Document QA',
    '',
    '- **文档类型**：需求文档',
    '- **系统计数的 open questions**：2',
    '- **Demo readiness**：Ready with assumptions',
    '- **Production readiness**：Needs review',
    '',
    '### 生产版阻塞项',
    '- None',
    '',
    '### Open Question 分类',
    '- **生产版阻塞**：1',
    '- 班次定义需要确认',
    '- **Demo 可接受 / 后续润色**：1',
    '- 颜色风格待定',
    '- **实现假设**：0',
    '- None',
    '- **仍需人工复核**：0',
    '- None',
    '',
    '### 业务规则 sanity check',
    '- None',
    '',
    '### 实现假设检查',
    '- None',
  ].join('\n')

  const qa = parseDocumentQa(markdown, 'prd_doc')

  assert.equal(qa?.documentType, '需求文档')
  assert.equal(qa?.openQuestionCount, 2)
  assert.equal(qa?.productionReadiness, 'Needs review')
  assert.deepEqual(qa?.productionBlockers, [])
  assert.equal(qa?.classificationCounts.blockingForProduction, 1)
  assert.equal(qa?.classificationCounts.okForDemo, 1)
})

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
    // extra renderer-only fields must be ignored
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
