import assert from 'node:assert/strict'
import { test } from 'node:test'

import { parseDocumentQa } from './documentQa.ts'

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
