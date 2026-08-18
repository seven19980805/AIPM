import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  filterTemplateCatalog,
  templateCatalogDomains,
} from './templateCatalog.ts'


const templates = [
  {
    template_id: 'qdm',
    template_key: 'qdm',
    template_name: 'Finished Lot Yield Dashboard',
    template_category: 'Data Visualization',
    business_domain: 'Quality',
    language: 'en',
    version: '1.0',
    description: 'Defect Pareto and lot yield review.',
    tags: ['Yield', 'Dashboard'],
    applicable_scenarios: ['Quality review'],
    section_count: 12,
    section_titles: ['Data Contract', 'Acceptance Criteria'],
  },
  {
    template_id: 'warehouse',
    template_key: 'warehouse',
    template_name: 'Warehouse Operations',
    template_category: 'Operations',
    business_domain: 'Logistics',
    language: 'en',
    version: '2.0',
    description: 'Inbound, outbound, and inventory workflow.',
    tags: ['Inventory'],
    applicable_scenarios: ['Cycle count'],
    section_count: 10,
    section_titles: ['Business Rules'],
  },
  {
    template_id: 'process',
    template_key: 'process',
    template_name: 'Business Process',
    template_category: 'Workflow',
    business_domain: 'General',
    language: 'en',
    version: '1.0',
    description: 'Approval and audit workflow.',
    tags: ['Approval'],
    applicable_scenarios: ['Internal request'],
    section_count: 9,
    section_titles: ['Permissions'],
  },
]


test('searches across title, description, tags, scenarios, and section names', () => {
  assert.deepEqual(
    filterTemplateCatalog(templates, { query: 'pareto' }).map((item) => item.template_id),
    ['qdm'],
  )
  assert.deepEqual(
    filterTemplateCatalog(templates, { query: 'cycle count' }).map((item) => item.template_id),
    ['warehouse'],
  )
  assert.deepEqual(
    filterTemplateCatalog(templates, { query: 'permissions' }).map((item) => item.template_id),
    ['process'],
  )
  assert.deepEqual(
    filterTemplateCatalog(templates, { query: 'finished pareto' }).map((item) => item.template_id),
    ['qdm'],
  )
})


test('combines business-domain filtering with search without mutating input', () => {
  const originalOrder = templates.map((item) => item.template_id)
  const result = filterTemplateCatalog(templates, {
    domain: 'Quality',
    query: 'dashboard',
  })

  assert.deepEqual(result.map((item) => item.template_id), ['qdm'])
  assert.deepEqual(templates.map((item) => item.template_id), originalOrder)
})


test('returns stable domain options with counts', () => {
  assert.deepEqual(
    templateCatalogDomains(templates),
    [
      { id: 'General', label: 'General', count: 1 },
      { id: 'Logistics', label: 'Logistics', count: 1 },
      { id: 'Quality', label: 'Quality', count: 1 },
    ],
  )
})
