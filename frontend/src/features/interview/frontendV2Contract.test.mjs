import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { test } from 'node:test'

async function source(path) {
  return readFile(new URL(path, import.meta.url), 'utf8').catch(() => '')
}

test('renders exactly one authoritative next-decision card above the composer', async () => {
  const app = await source('../../App.vue')
  const component = await source('../../components/interview/NextDecisionCard.vue')

  assert.match(component, /next-decision-card/)
  assert.doesNotMatch(component, /stepNumber|brief\.confirmed_decisions/)
  assert.equal((app.match(/<NextDecisionCard\b/g) ?? []).length, 1)
  assert.ok(app.indexOf('<NextDecisionCard') < app.indexOf('<form'))
  assert.match(component, /defer_decision/)
  assert.match(component, /editProposal/)
  assert.match(component, /proposal\.text/)
  assert.match(component, /decision\.options/)
  assert.match(component, /emit\('selectOption', option\.text\)/)
  assert.match(component, /Choose the closest answer/)
  assert.match(component, /选择最接近的答案/)
  assert.match(component, /One reply can cover several decisions/)
  assert.match(component, /一条回复可以覆盖多个决策点/)
  assert.match(app, /@edit-proposal="editInterviewProposal"/)
  assert.match(app, /@select-option="sendInterviewOption"/)
})

test('the decision card is decision-agnostic so new backend decisions render unchanged', async () => {
  const component = await source('../../components/interview/NextDecisionCard.vue')
  const types = await source('../../types/interviewState.ts')

  // No hard-coded decision list: the card renders whatever the server sends,
  // including the conditional writeback-authorization decision.
  assert.doesNotMatch(component, /'(outcome|actor_action|v1_flow|data_boundary|writeback)'/)
  assert.match(types, /decision_id: string/)
  // The example button is only offered when the server sends no options, so a
  // decision without a server-side proposal template can never dead-end.
  assert.match(component, /v-else-if="!decision\.options\.length"/)
})

test('right-hand delivery status consumes InterviewStateV2 and has no phase percentages', async () => {
  const deliveryCard = await source('../../components/delivery/DeliveryReadinessCard.vue')
  const inspector = await source('../../components/workspace/RequirementInspector.vue')
  const header = await source('../../components/workspace/WorkspaceHeader.vue')
  const preview = await source('../../components/RequirementMarkdownPreview.vue')
  const detailCounts = await source('../../lib/structuredRequirementProgress.ts')
  const legacyReadiness = await source('../delivery/deliveryReadiness.ts')

  assert.match(deliveryCard, /interviewState/)
  assert.doesNotMatch(deliveryCard, /buildDeliveryReadiness/)
  assert.doesNotMatch(deliveryCard, /phase-progress/)
  assert.doesNotMatch(deliveryCard, /\{\{[^}]*%/)
  assert.doesNotMatch(inspector, /readinessPercentage/)
  assert.doesNotMatch(header, /readinessPercentage/)
  assert.doesNotMatch(preview, /collectionCoveragePercentage|confirmationPercentage/)
  assert.doesNotMatch(detailCounts, /readinessPercentage|STATUS_READINESS_POINTS|readyToGenerate/)
  assert.equal(legacyReadiness, '')
  assert.match(deliveryCard, /Core evidence/)
  assert.match(deliveryCard, /核心证据/)
  assert.match(deliveryCard, /v-if="showStrictReview"/)
  assert.match(deliveryCard, /assumption_count/)
  assert.doesNotMatch(deliveryCard, /Quick decisions|快速决策/)
  assert.doesNotMatch(deliveryCard, /next_decision\?\.question|delivery-next/)
  assert.match(deliveryCard, /Generate draft with TBDs/)
  assert.match(deliveryCard, /生成含待确认项的草稿/)
})

test('reasoning is gated behind an explicit development flag', async () => {
  const app = await source('../../App.vue')

  assert.match(app, /VITE_SHOW_REASONING/)
  assert.match(app, /showReasoning && msg\.role === 'assistant'/)
})

test('asks for a real business route before showing the empty-session composer and starters', async () => {
  const app = await source('../../App.vue')
  const landing = await source('../../components/interview/EmptySessionLanding.vue')
  const workspace = await source('../../components/workspace/ConversationWorkspace.vue')

  assert.match(landing, /empty-session-landing/)
  assert.match(landing, /v-for="route in routes"/)
  assert.match(landing, /emit\('selectRoute', route\.id\)/)
  assert.match(landing, /v-if="selectedRoute"/)
  assert.match(landing, /starters\.slice\(0,\s*3\)/)
  assert.match(landing, /v-for="starter in visibleStarters"/)
  assert.equal((landing.match(/<button\b/g) ?? []).length, 2)

  assert.match(workspace, /singleColumn/)
  assert.match(workspace, /'single-column': singleColumn/)
  assert.equal((app.match(/<form\b/g) ?? []).length, 1)
  assert.match(app, /<EmptySessionLanding\b[^>]*v-if="!messages\.length"/s)
  assert.match(app, /:routes="emptySessionRouteOptions"/)
  assert.match(app, /:selected-route="emptySessionRouteSelected"/)
  assert.match(app, /@select-route="selectEmptySessionRoute"/)
  assert.match(app, /startIcSubstrateNewChat\(route,\s*'from_scratch'\)/)
  assert.match(app, /<form\s+v-if="messages\.length \|\| emptySessionRouteSelected"\s+class="composer-card"/s)
  assert.match(app, /:single-column="!messages\.length"/)
  assert.doesNotMatch(app, /<SessionLaunchPanel\b/)
  assert.match(app, /<NextDecisionCard\b[^>]*v-if="messages\.length"/s)
  assert.match(app, /<RequirementInspector\b[^>]*v-if="messages\.length"/s)
})

test('long option answers show a short label but still send the full text', async () => {
  const component = await source('../../components/interview/NextDecisionCard.vue')
  const types = await source('../../types/interviewState.ts')

  // The card must display the label but emit the full answer, or a one-click
  // writeback authorization would lose the evidence grounding depends on.
  assert.match(component, /option\.label \|\| option\.text/)
  assert.match(component, /emit\('selectOption', option\.text\)/)
  assert.match(component, /:title="option\.text"/)
  assert.match(types, /label\?: string/)
})

test('the language selector persists the session content language explicitly', async () => {
  const app = await source('../../App.vue')
  const sessions = await source('../../api/sessions.ts')

  assert.match(sessions, /method: 'PATCH'/)
  assert.match(app, /createSessionLanguageSync/)
  assert.match(app, /updateSessionLanguage/)

  // Only a user-initiated switch may persist; opening or refreshing a session
  // must never rewrite the content language the canonical model depends on.
  const selectLanguage = app.match(/function selectLanguage[\s\S]*?\n}/)?.[0] ?? ''
  assert.match(selectLanguage, /languageSwitchIsExplicit(\.value)? = true/)
  const loadSession = app.match(/async function loadSession[\s\S]*?\n}/)?.[0] ?? ''
  assert.doesNotMatch(loadSession, /updateSessionLanguage|syncSessionLanguage/)
  assert.match(app, /if \(!explicit\b|languageSwitchIsExplicit(\.value)? = false/)

  // A failed switch reverts so the UI matches what the server still holds, and
  // reports it with its own recoverable message rather than a load error.
  assert.match(app, /outcome\.status === 'failed'/)
  assert.match(app, /outcome\.revertTo/)
  assert.match(app, /languageSwitchFailed/)
  assert.doesNotMatch(app, /syncSessionLanguage[\s\S]{0,400}failedToLoadSession/)
})

test('every language has the recoverable language-switch message', async () => {
  const app = await source('../../App.vue')

  assert.equal((app.match(/languageSwitchFailed:/g) ?? []).length, 4)
})
