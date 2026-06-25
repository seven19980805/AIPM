<script setup lang="ts">
import { computed, ref } from 'vue'

import { structuredRequirementPanelCopy } from './structuredRequirementCopy'
import type { DocumentQaState } from '../lib/documentQa'
import { summarizePMMethodologyDisplay } from '../lib/pmMethodologyDisplay'
import { computeStructuredRequirementProgress } from '../lib/structuredRequirementProgress'
import type { LanguageCode } from '../types/session'
import type {
  ICSubstrateEvidenceCheck,
  ICSubstrateEvidenceState,
  PMMethodologyCheck,
  PMMethodologyCheckStatus,
  PMMethodologyState,
  RequirementCollectionItem,
  RequirementCollectionStatus,
  StructuredRequirementFeature,
  StructuredRequirementModel,
  StructuredRequirementPage,
} from '../types/structuredRequirement'

const props = withDefaults(
  defineProps<{
    language: LanguageCode
    model: StructuredRequirementModel
    pmMethodologyState: PMMethodologyState
    icSubstrateEvidenceState: ICSubstrateEvidenceState
    loading?: boolean
    syncing?: boolean
    generatingDocuments?: boolean
    openingGoCoding?: boolean
    generationDisabled?: boolean
    generationLabel?: string
    hasPrdDocument?: boolean
    documentQaState?: DocumentQaState | null
    error?: string
  }>(),
  {
    loading: false,
    syncing: false,
    generatingDocuments: false,
    openingGoCoding: false,
    generationDisabled: false,
    generationLabel: '',
    hasPrdDocument: false,
    documentQaState: null,
    error: '',
  },
)
const emit = defineEmits<{
  (event: 'generate-documents'): void
  (event: 'go-coding'): void
}>()

type RequirementRow = {
  key: string
  label: string
  value: string
  status: RequirementCollectionStatus
  reason: string
  pendingQuestion: string
}

const copy = computed(
  () => structuredRequirementPanelCopy[props.language] ?? structuredRequirementPanelCopy.en,
)

const requirementRows = computed<RequirementRow[]>(() => {
  const model = props.model
  const status = model.collection_status

  return [
    buildRow(
      'objective',
      copy.value.rows.objective,
      summarizeText(model.background.objective),
      status.objective,
    ),
    buildRow(
      'scope',
      copy.value.rows.scope,
      summarizeScope(model.scope.in_scope, model.scope.out_of_scope),
      status.scope,
    ),
    buildRow(
      'users',
      copy.value.rows.users,
      summarizeList(model.users_and_scenarios.target_users),
      status.users,
    ),
    buildRow(
      'scenarios',
      copy.value.rows.scenarios,
      summarizeList(model.users_and_scenarios.core_scenarios),
      status.scenarios,
    ),
    buildRow(
      'features',
      copy.value.rows.features,
      summarizeFeatures(model.functional_requirements.overview, model.functional_requirements.feature_details),
      status.features,
    ),
    buildRow(
      'pages',
      copy.value.rows.pages,
      summarizePages(model.page_and_interaction.pages),
      status.pages,
    ),
    buildRow(
      'rules',
      copy.value.rows.rules,
      summarizeList(model.business_rules),
      status.rules,
    ),
    buildRow(
      'integrations',
      copy.value.rows.integrations,
      summarizeList(model.data_and_dependencies),
      status.integrations,
    ),
    buildRow(
      'acceptance',
      copy.value.rows.acceptance,
      summarizeList(model.acceptance_criteria),
      status.acceptance,
    ),
  ].sort((left, right) => statusPriority(left.status) - statusPriority(right.status))
})

const progress = computed(() => computeStructuredRequirementProgress(props.model))

const progressTitleText = computed(() => copy.value.progressTitle)

const progressStyle = computed(() => {
  const progressValue = progress.value.readinessPercentage * 3.6
  return {
    background: `conic-gradient(var(--accent) 0deg ${progressValue}deg, #e7eefb ${progressValue}deg 360deg)`,
  }
})

const progressRingText = computed(() => `${progress.value.readinessPercentage}%`)

const progressCaptionText = computed(() => copy.value.progressLabels.finalReadiness)

const generationActionLabel = computed(() => {
  if (props.generationLabel) {
    return props.generationLabel
  }
  return copy.value.generateDocuments
})

// PM Methodology is advisory (a quality score), not a hard gate. Generate unlocks on the
// structured "Fully Confirmed" gate alone; Go Coding additionally needs the document.
const canGenerateDocuments = computed(() => progress.value.readyToGenerate)

const canOpenPanelGoCoding = computed(
  () => progress.value.readyToGenerate && props.hasPrdDocument,
)

// Secondary advisory cards collapse by default so the readiness gate (Progress) and
// the structured model stay in view without a tall scroll. The header shows a one-line
// summary; clicking it expands the full card.
const documentQaExpanded = ref(false)
const methodologyExpanded = ref(false)
const icEvidenceExpanded = ref(false)

const methodologyVisible = computed(() => props.pmMethodologyState.checks.length > 0)

const methodologyDisplay = computed(() =>
  summarizePMMethodologyDisplay(props.pmMethodologyState, progress.value.readyToGenerate),
)

const methodologyReadyCount = computed(
  () => methodologyDisplay.value.readyCount,
)

const methodologyMissingCount = computed(() => methodologyDisplay.value.missingCount)

const methodologyTopChecks = computed(() => methodologyDisplay.value.checks)

const methodologyShowNextQuestions = computed(() => methodologyDisplay.value.showNextQuestions)

const icEvidenceVisible = computed(
  () => props.icSubstrateEvidenceState.enabled && props.icSubstrateEvidenceState.checks.length > 0,
)

const icEvidenceReadyCount = computed(
  () => props.icSubstrateEvidenceState.checks.filter((check) => check.ready).length,
)

const icEvidenceTopChecks = computed(() =>
  [...props.icSubstrateEvidenceState.checks]
    .sort((left, right) => methodologyStatusPriority(left.status) - methodologyStatusPriority(right.status))
    .slice(0, 4),
)

const icEvidenceContextRows = computed(() => {
  const context = props.icSubstrateEvidenceState.domain_context
  return [
    {
      key: 'objects',
      label: copy.value.icEvidenceLabels.objects,
      value: summarizeList(context.business_objects, 3),
    },
    {
      key: 'grain',
      label: copy.value.icEvidenceLabels.grain,
      value: summarizeText(context.object_grain),
    },
    {
      key: 'source',
      label: copy.value.icEvidenceLabels.source,
      value: summarizeText(context.source_of_truth),
    },
  ].filter((item) => item.value)
})

const documentQaVisible = computed(() => props.documentQaState !== null)

const documentQaSourceLabel = computed(() => {
  if (!props.documentQaState) {
    return ''
  }
  return props.documentQaState.sourceKind === 'design_doc' ? '设计文档 QA' : '需求文档 QA'
})

const documentQaProductionClass = computed(() => {
  const readiness = props.documentQaState?.productionReadiness.toLowerCase() ?? ''
  if (readiness.includes('blocked')) {
    return 'blocked'
  }
  if (readiness.includes('review')) {
    return 'review'
  }
  if (readiness.includes('ready')) {
    return 'ready'
  }
  return 'unknown'
})

const documentQaTopBlockers = computed(() =>
  (props.documentQaState?.productionBlockers ?? []).slice(0, 3),
)

const documentQaFindingCount = computed(
  () =>
    (props.documentQaState?.productionBlockers.length ?? 0) +
    (props.documentQaState?.businessRuleFindings.length ?? 0) +
    (props.documentQaState?.implementationFindings.length ?? 0),
)

const documentQaDemoReadinessText = computed(() =>
  formatDocumentQaReadiness(props.documentQaState?.demoReadiness ?? '', 'Demo'),
)

const documentQaProductionReadinessText = computed(() =>
  formatDocumentQaReadiness(props.documentQaState?.productionReadiness ?? '', '生产版'),
)

const documentQaHandoffNote = computed(() => {
  if (!props.documentQaState) {
    return ''
  }
  if (documentQaProductionClass.value === 'blocked') {
    return 'Demo 可以交接；生产版仍有阻塞项。'
  }
  if (documentQaProductionClass.value === 'review') {
    return 'Demo 可以交接；生产假设需要人工复核。'
  }
  return '文档已可交接。'
})

function buildRow(
  key: string,
  label: string,
  rawValue: string,
  collectionItem: RequirementCollectionItem,
): RequirementRow {
  const value = rawValue.trim()
  return {
    key,
    label,
    value: value || copy.value.notCaptured,
    status: collectionItem.status,
    reason: collectionItem.reason.trim(),
    pendingQuestion: collectionItem.pending_questions[0]?.trim() || '',
  }
}

function statusPriority(status: RequirementCollectionStatus): number {
  if (status === 'conflict') {
    return 0
  }
  if (status === 'pending_confirmation') {
    return 1
  }
  if (status === 'missing') {
    return 2
  }
  if (status === 'captured') {
    return 3
  }
  return 4
}

function statusLabel(status: RequirementCollectionStatus): string {
  if (status === 'confirmed') {
    return copy.value.status.confirmed
  }
  if (status === 'pending_confirmation') {
    return copy.value.status.pendingConfirmation
  }
  if (status === 'captured') {
    return copy.value.status.captured
  }
  if (status === 'conflict') {
    return copy.value.status.conflict
  }
  return copy.value.status.missing
}

function statusClass(status: RequirementCollectionStatus): string {
  if (status === 'pending_confirmation') {
    return 'pending'
  }
  return status
}

function methodologyStatusLabel(status: PMMethodologyCheckStatus): string {
  return copy.value.methodologyStatus[status] ?? copy.value.methodologyStatus.missing
}

function methodologyStatusPriority(status: PMMethodologyCheckStatus): number {
  if (status === 'conflict') {
    return 0
  }
  if (status === 'missing') {
    return 1
  }
  if (status === 'partial') {
    return 2
  }
  return 3
}

function methodologyEvidenceSummary(check: PMMethodologyCheck): string {
  if (check.evidence.length) {
    return summarizeList(check.evidence, 1)
  }
  if (check.missing.length) {
    return summarizeList(check.missing, 2)
  }
  return copy.value.notCaptured
}

function formatDocumentQaReadiness(value: string, scopeLabel: string): string {
  const normalized = value.trim()
  const lower = normalized.toLowerCase()
  const prefix = scopeLabel === 'Demo' ? 'Demo ' : scopeLabel
  if (!normalized) {
    return '-'
  }
  if (lower.includes('blocked')) {
    return `${prefix}受阻`
  }
  if (lower.includes('review')) {
    return '需人工复核'
  }
  if (lower.includes('ready') && lower.includes('assumption')) {
    return `${prefix}可交接（含假设）`
  }
  if (lower.includes('ready')) {
    return `${prefix}可交接`
  }
  return normalized
}

function icEvidenceSummary(check: ICSubstrateEvidenceCheck): string {
  if (check.evidence.length) {
    return summarizeList(check.evidence, 1)
  }
  if (check.missing.length) {
    return summarizeList(check.missing, 1)
  }
  return copy.value.notCaptured
}

function summarizeScope(inScope: string[], outOfScope: string[]): string {
  const include = summarizeList(inScope, 2)
  const exclude = summarizeList(outOfScope, 2)
  if (include && exclude) {
    return `${copy.value.scopeLabels.in}: ${include} / ${copy.value.scopeLabels.out}: ${exclude}`
  }
  if (include) {
    return `${copy.value.scopeLabels.in}: ${include}`
  }
  if (exclude) {
    return `${copy.value.scopeLabels.out}: ${exclude}`
  }
  return ''
}

function summarizeFeatures(overview: string, features: StructuredRequirementFeature[]): string {
  const names = features
    .map((item) => item.feature_name || item.description)
    .filter(Boolean)
  const featureSummary = summarizeList(names, 2)
  if (featureSummary) {
    return featureSummary
  }
  return summarizeText(overview)
}

function summarizePages(pages: StructuredRequirementPage[]): string {
  const names = pages.map((item) => item.page_name || item.entry_point).filter(Boolean)
  return summarizeList(names, 2)
}

function summarizeList(values: string[], limit = 2): string {
  const normalized = values.map((item) => item.trim()).filter(Boolean)
  if (!normalized.length) {
    return ''
  }

  const clipped = normalized.slice(0, limit).join(' / ')
  return normalized.length > limit ? `${clipped} ...` : clipped
}

function summarizeText(value: string): string {
  const normalized = value.trim()
  if (!normalized) {
    return ''
  }

  return normalized.length > 96 ? `${normalized.slice(0, 96).trimEnd()} ...` : normalized
}
</script>

<template>
  <aside class="requirement-panel-stack">
    <section class="requirement-card progress-card">
      <header class="card-head compact">
        <div class="card-title">
          <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="2" width="6" height="4" rx="1"/>
            <path d="M9 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3"/>
            <path d="M9 12h6"/>
            <path d="M9 16h4"/>
          </svg>
          <h3>{{ progressTitleText }}</h3>
        </div>
        <span v-if="syncing" class="sync-badge">{{ copy.syncing }}</span>
      </header>

      <div class="progress-body">
        <div class="progress-visual">
          <div class="progress-ring" :style="progressStyle">
            <div class="progress-ring-inner">
              <span>{{ progressRingText }}</span>
            </div>
          </div>
          <p class="progress-caption">{{ progressCaptionText }}</p>
        </div>

        <div class="progress-meta">
          <div class="progress-row">
            <span>{{ copy.progressLabels.coverage }}</span>
            <strong>{{ progress.collectedCount }}/{{ progress.totalCount }}</strong>
          </div>
          <div class="progress-row">
            <span>{{ copy.progressLabels.confirmationRate }}</span>
            <strong>{{ progress.confirmationPercentage }}%</strong>
          </div>
          <div class="progress-row">
            <span>{{ copy.progressLabels.pendingConfirmation }}</span>
            <strong>{{ progress.pendingConfirmationCount }}</strong>
          </div>
          <div class="progress-row">
            <span>{{ copy.progressLabels.blockingQuestions }}</span>
            <strong>{{ progress.blockingQuestionCount }}</strong>
          </div>
          <div class="progress-row">
            <span>{{ copy.progressLabels.conflict }}</span>
            <strong>{{ progress.conflictCount }}</strong>
          </div>
        </div>
      </div>

      <div class="progress-actions">
        <button
          v-if="hasPrdDocument"
          class="go-coding-btn primary"
          type="button"
          :disabled="loading || generatingDocuments || generationDisabled || openingGoCoding || !canOpenPanelGoCoding"
          @click="emit('go-coding')"
        >
          {{ openingGoCoding ? copy.openingGoCoding : copy.goCoding }}
        </button>
        <button
          class="generate-prd-btn"
          :class="{ ready: canGenerateDocuments, secondary: hasPrdDocument }"
          type="button"
          :disabled="loading || generatingDocuments || generationDisabled || openingGoCoding || !canGenerateDocuments"
          @click="emit('generate-documents')"
        >
          {{ generatingDocuments ? copy.generatingDocuments : generationActionLabel }}
        </button>
      </div>
    </section>

    <section v-if="documentQaVisible && documentQaState" class="requirement-card document-qa-card">
      <button
        type="button"
        class="card-head card-head-toggle"
        :aria-expanded="documentQaExpanded"
        @click="documentQaExpanded = !documentQaExpanded"
      >
        <div class="card-title">
          <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 11l2 2 4-5"/>
            <path d="M21 12a9 9 0 1 1-6.2-8.56"/>
          </svg>
          <h3>Document QA</h3>
        </div>
        <div class="card-head-meta">
          <span class="card-head-summary document-qa-status" :class="documentQaProductionClass">
            {{ documentQaProductionReadinessText }}
          </span>
          <svg class="card-chevron" :class="{ open: documentQaExpanded }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </div>
      </button>

      <div v-show="documentQaExpanded" class="card-collapsible">
        <div class="document-qa-summary">
          <div class="document-qa-row">
            <span>{{ documentQaSourceLabel }}</span>
            <strong>{{ documentQaState.documentType }}</strong>
          </div>
          <div class="document-qa-row">
            <span>Demo 可交付性</span>
            <strong>{{ documentQaDemoReadinessText }}</strong>
          </div>
          <div class="document-qa-row">
            <span>生产可用性</span>
            <strong class="document-qa-status" :class="documentQaProductionClass">
              {{ documentQaProductionReadinessText }}
            </strong>
          </div>
          <div class="document-qa-row">
            <span>未决问题</span>
            <strong>{{ documentQaState.openQuestionCount ?? '-' }}</strong>
          </div>
          <div class="document-qa-row">
            <span>QA 发现</span>
            <strong>{{ documentQaFindingCount }}</strong>
          </div>
        </div>

        <p class="document-qa-note" :class="documentQaProductionClass">
          {{ documentQaHandoffNote }}
        </p>

        <div v-if="documentQaTopBlockers.length" class="document-qa-blockers">
          <span>主要阻塞项</span>
          <ul>
            <li v-for="blocker in documentQaTopBlockers" :key="blocker">{{ blocker }}</li>
          </ul>
        </div>
      </div>
    </section>

    <section v-if="methodologyVisible" class="requirement-card methodology-card">
      <button
        type="button"
        class="card-head card-head-toggle"
        :aria-expanded="methodologyExpanded"
        @click="methodologyExpanded = !methodologyExpanded"
      >
        <div class="card-title">
          <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 3v18"/>
            <path d="M4 8h16"/>
            <path d="M5 16h14"/>
            <path d="M7 3h10"/>
            <path d="M7 21h10"/>
          </svg>
          <h3>{{ copy.methodologyTitle }}</h3>
        </div>
        <div class="card-head-meta">
          <span class="card-head-summary">{{ pmMethodologyState.score }}% · {{ methodologyReadyCount }}/{{ pmMethodologyState.checks.length }}</span>
          <svg class="card-chevron" :class="{ open: methodologyExpanded }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </div>
      </button>

      <div v-show="methodologyExpanded" class="card-collapsible">
      <div class="methodology-summary">
        <div>
          <span>{{ copy.methodologyLabels.score }}</span>
          <strong>{{ pmMethodologyState.score }}%</strong>
        </div>
        <div>
          <span>{{ copy.methodologyLabels.ready }}</span>
          <strong>{{ methodologyReadyCount }}/{{ pmMethodologyState.checks.length }}</strong>
        </div>
        <div>
          <span>{{ copy.methodologyLabels.missing }}</span>
          <strong>{{ methodologyMissingCount }}</strong>
        </div>
      </div>

      <div class="methodology-list">
        <article
          v-for="check in methodologyTopChecks"
          :key="check.key"
          class="methodology-item"
          :class="check.status"
        >
          <header class="methodology-item-head">
            <div>
              <h4>{{ check.label }}</h4>
              <p>{{ check.method }}</p>
            </div>
            <span class="methodology-status" :class="check.status">
              {{ methodologyStatusLabel(check.status) }}
            </span>
          </header>
          <p class="methodology-evidence">
            {{ methodologyEvidenceSummary(check) }}
          </p>
          <div
            v-if="methodologyShowNextQuestions && !check.ready && check.next_question"
            class="methodology-question"
          >
            <span>{{ copy.methodologyLabels.nextQuestion }}</span>
            <p>{{ check.next_question }}</p>
          </div>
        </article>
      </div>
      </div>
    </section>

    <section v-if="icEvidenceVisible" class="requirement-card ic-evidence-card">
      <button
        type="button"
        class="card-head card-head-toggle"
        :aria-expanded="icEvidenceExpanded"
        @click="icEvidenceExpanded = !icEvidenceExpanded"
      >
        <div class="card-title">
          <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 7h16"/>
            <path d="M4 12h16"/>
            <path d="M4 17h16"/>
            <path d="M8 4v16"/>
            <path d="M16 4v16"/>
          </svg>
          <h3>{{ copy.icEvidenceTitle }}</h3>
        </div>
        <div class="card-head-meta">
          <span class="card-head-summary">{{ icSubstrateEvidenceState.readiness_score }}% · {{ icEvidenceReadyCount }}/{{ icSubstrateEvidenceState.checks.length }}</span>
          <svg class="card-chevron" :class="{ open: icEvidenceExpanded }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </div>
      </button>

      <div v-show="icEvidenceExpanded" class="card-collapsible">
      <div class="methodology-summary ic-evidence-summary">
        <div>
          <span>{{ copy.icEvidenceLabels.score }}</span>
          <strong>{{ icSubstrateEvidenceState.readiness_score }}%</strong>
        </div>
        <div>
          <span>{{ copy.icEvidenceLabels.ready }}</span>
          <strong>{{ icEvidenceReadyCount }}/{{ icSubstrateEvidenceState.checks.length }}</strong>
        </div>
        <div>
          <span>{{ copy.icEvidenceLabels.context }}</span>
          <strong>{{ icSubstrateEvidenceState.department || copy.notCaptured }}</strong>
        </div>
      </div>

      <div v-if="icSubstrateEvidenceState.product_shape_label || icEvidenceContextRows.length" class="ic-context-strip">
        <div v-if="icSubstrateEvidenceState.product_shape_label">
          <span>{{ copy.icEvidenceLabels.shape }}</span>
          <strong>{{ icSubstrateEvidenceState.product_shape_label }}</strong>
        </div>
        <div v-for="item in icEvidenceContextRows" :key="item.key">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>

      <div class="methodology-list">
        <article
          v-for="check in icEvidenceTopChecks"
          :key="check.key"
          class="methodology-item ic-evidence-item"
          :class="check.status"
        >
          <header class="methodology-item-head">
            <div>
              <h4>{{ check.label }}</h4>
            </div>
            <span class="methodology-status" :class="check.status">
              {{ methodologyStatusLabel(check.status) }}
            </span>
          </header>
          <p class="methodology-evidence">
            {{ icEvidenceSummary(check) }}
          </p>
          <div v-if="!check.ready && check.next_question" class="methodology-question">
            <span>{{ copy.icEvidenceLabels.nextQuestion }}</span>
            <p>{{ check.next_question }}</p>
          </div>
        </article>
      </div>
      </div>
    </section>

    <section class="requirement-card table-card">
      <header class="card-head">
        <div class="card-title">
          <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <path d="M14 2v6h6"/>
            <path d="M16 13H8"/>
            <path d="M16 17H8"/>
            <path d="M10 9H8"/>
          </svg>
          <h3>{{ copy.requirementTitle }}</h3>
        </div>
        <span v-if="syncing" class="sync-badge">{{ copy.syncing }}</span>
      </header>

      <div v-if="loading" class="card-state">
        {{ copy.loading }}
      </div>
      <div v-else-if="error" class="card-state error">
        {{ error }}
      </div>
      <div v-else class="card-list-shell">
        <div class="requirement-list">
          <article
            v-for="row in requirementRows"
            :key="row.key"
            class="requirement-item-card"
            :class="statusClass(row.status)"
          >
            <header class="requirement-item-head">
              <h4>{{ row.label }}</h4>
              <span class="status-pill" :class="statusClass(row.status)">
                {{ statusLabel(row.status) }}
              </span>
            </header>

            <p class="requirement-item-content" :title="row.value">
              {{ row.value }}
            </p>

            <div v-if="row.reason || row.pendingQuestion" class="requirement-item-notes">
              <div v-if="row.reason" class="requirement-note">
                <span class="requirement-note-label">{{ copy.cardLabels.reason }}</span>
                <p>{{ row.reason }}</p>
              </div>
              <div v-if="row.pendingQuestion" class="requirement-note question">
                <span class="requirement-note-label">{{ copy.cardLabels.pendingQuestion }}</span>
                <p>{{ row.pendingQuestion }}</p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>
  </aside>
</template>

<style scoped>
.requirement-panel-stack {
  width: 100%;
  height: auto;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 14px;
  overflow: visible;
}

.requirement-card {
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--panel);
  box-shadow: var(--shadow-soft, 0 2px 8px rgba(38, 55, 70, 0.06));
  overflow: hidden;
  height: auto;
}

.table-card {
  order: 2;
  flex: 0 0 auto;
  width: 100%;
  min-height: 0;
  height: auto;
  display: flex;
  flex-direction: column;
}

.progress-card {
  order: 1;
  flex: 0 0 auto;
  align-self: start;
  width: 100%;
}

.card-head {
  padding: 16px 16px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.card-head.compact {
  padding-bottom: 8px;
}

.card-title {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title h3 {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.25;
  overflow-wrap: break-word;
}

.sync-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 0.7rem;
  font-weight: 700;
  white-space: nowrap;
}

.sync-badge::before {
  content: '';
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  animation: syncPulse 1.2s ease-in-out infinite;
}

.card-icon {
  width: 20px;
  height: 20px;
  color: var(--accent);
  flex-shrink: 0;
}

/* Collapsible secondary cards (Document QA / PM Methodology / IC Evidence) */
.card-head-toggle {
  width: 100%;
  margin: 0;
  border: 0;
  background: transparent;
  font: inherit;
  color: inherit;
  text-align: left;
  cursor: pointer;
  border-radius: 12px;
}

.card-head-toggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.card-head-toggle:hover .card-chevron {
  color: var(--accent);
}

.card-head-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.card-head-summary {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--muted);
  white-space: nowrap;
}

.card-chevron {
  width: 16px;
  height: 16px;
  color: var(--muted);
  flex-shrink: 0;
  transition: transform 0.18s ease;
}

.card-chevron.open {
  transform: rotate(180deg);
}

.card-state {
  margin: 0 16px 16px;
  padding: 12px;
  border-radius: 8px;
  border: 1px dashed rgba(37, 99, 235, 0.34);
  color: var(--muted);
  background: var(--panel-soft);
  line-height: 1.45;
  font-size: 0.84rem;
}

.card-state.error {
  border-style: solid;
  border-color: var(--status-danger-border);
  color: var(--status-danger-ink);
  background: var(--status-danger-bg);
}

.progress-body {
  display: grid;
  grid-template-columns: 82px 1fr;
  align-items: center;
  gap: 14px;
  padding: 2px 16px 16px;
}

.progress-visual {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.progress-ring {
  width: 78px;
  height: 78px;
  border-radius: 50%;
  display: grid;
  place-items: center;
}

.progress-ring-inner {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: var(--panel);
  display: grid;
  place-items: center;
  box-shadow: inset 0 0 0 1px var(--line);
}

.progress-ring-inner span {
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0;
  color: var(--ink);
}

.progress-caption {
  margin: 0;
  color: var(--muted);
  font-size: 0.7rem;
  font-weight: 700;
}

.progress-meta {
  display: grid;
  gap: 6px;
}

.progress-actions {
  padding: 0 14px 14px;
  display: grid;
  gap: 7px;
}

.generate-prd-btn {
  width: 100%;
  min-height: 38px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px 12px;
  background: var(--panel);
  color: var(--accent-strong);
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.generate-prd-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: rgba(0, 94, 184, 0.28);
  box-shadow: 0 6px 14px rgba(38, 55, 70, 0.08);
}

.generate-prd-btn.ready {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  box-shadow: 0 6px 14px rgba(0, 94, 184, 0.16);
}

.generate-prd-btn.secondary {
  background: var(--panel);
  color: var(--accent-strong);
  box-shadow: none;
}

.generate-prd-btn:disabled {
  border-color: #d9e1e7;
  background: #eef2f7;
  color: #94a3b8;
  opacity: 1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.go-coding-btn {
  width: 100%;
  min-height: 38px;
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 9px 12px;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  box-shadow: 0 6px 14px rgba(0, 94, 184, 0.16);
}

.go-coding-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: var(--accent-strong);
  box-shadow: 0 8px 18px rgba(0, 94, 184, 0.2);
}

.go-coding-btn:disabled {
  border-color: #d9e1e7;
  background: #eef2f7;
  color: #94a3b8;
  opacity: 1;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 0.78rem;
}

.progress-row strong {
  color: var(--ink);
  font-size: 0.86rem;
}

.methodology-card {
  order: 5;
  flex: 0 0 auto;
  width: 100%;
}

.ic-evidence-card {
  order: 4;
  flex: 0 0 auto;
  width: 100%;
}

.document-qa-card {
  order: 3;
  flex: 0 0 auto;
  width: 100%;
}

.document-qa-source {
  flex-shrink: 0;
  padding: 4px 7px;
  border-radius: 8px;
  background: var(--panel-soft);
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 800;
  line-height: 1;
}

.document-qa-summary {
  padding: 0 16px 10px;
  display: grid;
  gap: 0;
}

.document-qa-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  padding: 7px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
  font-size: 0.78rem;
}

.document-qa-row:first-child {
  border-top: 0;
}

.document-qa-row span {
  color: var(--muted);
}

.document-qa-row strong {
  min-width: 0;
  color: var(--ink);
  font-size: 0.78rem;
  text-align: right;
  overflow-wrap: anywhere;
}

.document-qa-status.blocked {
  color: var(--status-danger-ink);
}

.document-qa-status.review {
  color: var(--status-warning-ink);
}

.document-qa-status.ready {
  color: var(--status-success-ink);
}

.document-qa-note {
  margin: 0 16px 12px;
  padding: 9px 10px;
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 750;
  line-height: 1.35;
}

.document-qa-note.blocked {
  background: var(--status-danger-bg);
  color: var(--status-danger-ink);
}

.document-qa-note.review,
.document-qa-note.unknown {
  background: var(--status-warning-bg);
  color: var(--status-warning-ink);
}

.document-qa-note.ready {
  background: var(--status-success-bg);
  color: var(--status-success-ink);
}

.document-qa-blockers {
  margin: 0 16px 16px;
  padding-top: 10px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.document-qa-blockers > span {
  display: block;
  margin-bottom: 6px;
  color: var(--muted);
  font-size: 0.68rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0;
}

.document-qa-blockers ul {
  margin: 0;
  padding-left: 16px;
  display: grid;
  gap: 5px;
}

.document-qa-blockers li {
  color: var(--ink);
  font-size: 0.74rem;
  line-height: 1.35;
}

.methodology-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
  padding: 0 14px 10px;
}

.methodology-summary div {
  min-width: 0;
  padding: 9px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel-soft);
}

.methodology-summary span,
.methodology-question span {
  display: block;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1.25;
}

.methodology-summary strong {
  display: block;
  margin-top: 5px;
  color: var(--ink);
  font-size: 1rem;
  line-height: 1.2;
  overflow-wrap: anywhere;
}

.ic-context-strip {
  display: grid;
  gap: 8px;
  padding: 0 16px 12px;
}

.ic-context-strip div {
  min-width: 0;
  padding: 9px 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel-soft);
}

.ic-context-strip span {
  display: block;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1.25;
}

.ic-context-strip strong {
  display: block;
  margin-top: 4px;
  color: var(--ink);
  font-size: 0.8rem;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.methodology-list {
  display: grid;
  gap: 8px;
  padding: 0 14px 14px;
}

.methodology-item {
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
}

.methodology-item.missing {
  border-color: var(--status-warning-border);
  background: var(--status-warning-bg);
}

.methodology-item.partial {
  border-color: var(--status-info-border);
  background: var(--status-info-bg);
}

.methodology-item.ready {
  border-color: var(--status-success-border);
  background: var(--status-success-bg);
}

.methodology-item.conflict {
  border-color: var(--status-danger-border);
  background: var(--status-danger-bg);
}

.methodology-item-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.methodology-item-head h4 {
  margin: 0;
  color: var(--ink);
  font-size: 0.86rem;
  line-height: 1.35;
}

.methodology-item-head p,
.methodology-evidence,
.methodology-question p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.methodology-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 58px;
  padding: 5px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

.methodology-status.missing {
  background: var(--status-warning-bg);
  color: var(--status-warning-ink);
}

.methodology-status.partial {
  background: var(--status-info-bg);
  color: var(--status-info-ink);
}

.methodology-status.ready {
  background: var(--status-success-bg);
  color: var(--status-success-ink);
}

.methodology-status.conflict {
  background: var(--status-danger-bg);
  color: var(--status-danger-ink);
}

.methodology-question {
  margin-top: 9px;
  padding: 9px 10px;
  border: 1px solid var(--status-warning-border);
  border-radius: 8px;
  background: var(--status-warning-bg);
}

.ic-evidence-item .methodology-evidence {
  color: var(--ink);
}

.card-list-shell {
  flex: 0 0 auto;
  min-height: auto;
  overflow: visible;
  padding: 0 14px 14px;
}

.requirement-list {
  display: grid;
  gap: 8px;
}

.requirement-item-card {
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.requirement-item-card.missing {
  background: var(--panel);
}

.requirement-item-card.captured {
  border-color: var(--status-info-border);
  background: var(--status-info-bg);
}

.requirement-item-card.pending {
  border-color: var(--status-warning-border);
  background: var(--status-warning-bg);
}

.requirement-item-card.confirmed {
  border-color: var(--status-success-border);
  background: var(--status-success-bg);
}

.requirement-item-card.conflict {
  border-color: var(--status-danger-border);
  background: var(--status-danger-bg);
}

.requirement-item-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.requirement-item-head h4 {
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.35;
  color: var(--ink);
}

.requirement-item-content {
  margin: 8px 0 0;
  color: var(--ink);
  line-height: 1.55;
  font-size: 0.8rem;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.requirement-item-notes {
  display: grid;
  gap: 8px;
  margin-top: 8px;
}

.requirement-note {
  padding: 9px 10px;
  border-radius: 8px;
  background: var(--panel-soft);
  border: 1px solid var(--line);
}

.requirement-note.question {
  background: var(--status-warning-bg);
  border-color: var(--status-warning-border);
}

.requirement-note-label {
  display: inline-block;
  margin-bottom: 5px;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
}

.requirement-note p {
  margin: 0;
  color: var(--ink);
  line-height: 1.5;
  font-size: 0.8rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 58px;
  padding: 4px 7px;
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-pill.missing {
  background: var(--status-muted-bg);
  color: var(--status-muted-ink);
}

.status-pill.captured {
  background: var(--status-info-bg);
  color: var(--status-info-ink);
}

.status-pill.pending {
  background: var(--status-warning-bg);
  color: var(--status-warning-ink);
}

.status-pill.confirmed {
  background: var(--status-success-bg);
  color: var(--status-success-ink);
}

.status-pill.conflict {
  background: var(--status-danger-bg);
  color: var(--status-danger-ink);
}

:global(.app-shell[data-theme='dark']) .requirement-card,
:global(.app-shell[data-theme='dark']) .methodology-item,
:global(.app-shell[data-theme='dark']) .requirement-item-card,
:global(.app-shell[data-theme='dark']) .methodology-summary div,
:global(.app-shell[data-theme='dark']) .ic-context-strip div,
:global(.app-shell[data-theme='dark']) .requirement-note {
  background: var(--panel);
  border-color: var(--line);
  color: var(--ink);
}

:global(.app-shell[data-theme='dark']) .card-state,
:global(.app-shell[data-theme='dark']) .progress-ring-inner {
  background: var(--panel-strong);
  border-color: var(--line);
  color: var(--ink);
}

:global(.app-shell[data-theme='dark']) .requirement-item-card.captured,
:global(.app-shell[data-theme='dark']) .methodology-item.partial {
  background: var(--status-info-bg);
  border-color: var(--status-info-border);
}

:global(.app-shell[data-theme='dark']) .requirement-item-card.confirmed,
:global(.app-shell[data-theme='dark']) .methodology-item.ready {
  background: var(--status-success-bg);
  border-color: var(--status-success-border);
}

:global(.app-shell[data-theme='dark']) .requirement-item-card.pending,
:global(.app-shell[data-theme='dark']) .methodology-item.missing,
:global(.app-shell[data-theme='dark']) .methodology-question,
:global(.app-shell[data-theme='dark']) .requirement-note.question {
  background: var(--status-warning-bg);
  border-color: var(--status-warning-border);
}

:global(.app-shell[data-theme='dark']) .requirement-item-card.conflict,
:global(.app-shell[data-theme='dark']) .methodology-item.conflict {
  background: var(--status-danger-bg);
  border-color: var(--status-danger-border);
}

:global(.app-shell[data-theme='dark']) .card-title h3,
:global(.app-shell[data-theme='dark']) .progress-ring-inner span,
:global(.app-shell[data-theme='dark']) .progress-row strong,
:global(.app-shell[data-theme='dark']) .methodology-summary strong,
:global(.app-shell[data-theme='dark']) .ic-context-strip strong,
:global(.app-shell[data-theme='dark']) .methodology-item-head h4,
:global(.app-shell[data-theme='dark']) .requirement-item-head h4,
:global(.app-shell[data-theme='dark']) .requirement-item-content,
:global(.app-shell[data-theme='dark']) .requirement-note p,
:global(.app-shell[data-theme='dark']) .ic-evidence-item .methodology-evidence {
  color: var(--ink);
}

:global(.app-shell[data-theme='dark']) .progress-caption,
:global(.app-shell[data-theme='dark']) .progress-row,
:global(.app-shell[data-theme='dark']) .methodology-summary span,
:global(.app-shell[data-theme='dark']) .methodology-question span,
:global(.app-shell[data-theme='dark']) .ic-context-strip span,
:global(.app-shell[data-theme='dark']) .methodology-item-head p,
:global(.app-shell[data-theme='dark']) .methodology-evidence,
:global(.app-shell[data-theme='dark']) .methodology-question p,
:global(.app-shell[data-theme='dark']) .requirement-note-label {
  color: var(--muted);
}

:global(.app-shell[data-theme='dark']) .generate-prd-btn.secondary {
  background: var(--panel-strong);
  border-color: var(--line);
  color: var(--accent-strong);
}

:global(.app-shell[data-theme='dark']) .generate-prd-btn:disabled,
:global(.app-shell[data-theme='dark']) .go-coding-btn:disabled {
  background: #1a2736;
  border-color: #2d4054;
  color: #6f8296;
}

@media (max-width: 1200px) {
  .progress-body {
    grid-template-columns: 1fr;
    justify-items: center;
  }

  .progress-meta {
    width: 100%;
  }

  .methodology-summary {
    grid-template-columns: 1fr;
  }

  .ic-context-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .requirement-panel-stack {
    height: auto;
    min-height: 0;
    overflow: visible;
  }
}

@keyframes syncPulse {
  0%,
  100% {
    opacity: 0.35;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
