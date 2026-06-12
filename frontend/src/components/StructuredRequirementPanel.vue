<script setup lang="ts">
import { computed } from 'vue'

import { structuredRequirementPanelCopy } from './structuredRequirementCopy'
import { computeStructuredRequirementProgress } from '../lib/structuredRequirementProgress'
import type { LanguageCode } from '../types/session'
import type {
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
    loading?: boolean
    syncing?: boolean
    generatingDocuments?: boolean
    openingGoCoding?: boolean
    generationDisabled?: boolean
    hasPrdDocument?: boolean
    hasDesignDocument?: boolean
    error?: string
  }>(),
  {
    loading: false,
    syncing: false,
    generatingDocuments: false,
    openingGoCoding: false,
    generationDisabled: false,
    hasPrdDocument: false,
    hasDesignDocument: false,
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

const progressStyle = computed(() => {
  const progressValue = progress.value.readinessPercentage * 3.6
  return {
    background: `conic-gradient(var(--accent) 0deg ${progressValue}deg, #e7eefb ${progressValue}deg 360deg)`,
  }
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
          <h3>{{ copy.progressTitle }}</h3>
        </div>
        <span v-if="syncing" class="sync-badge">{{ copy.syncing }}</span>
      </header>

      <div class="progress-body">
        <div class="progress-visual">
          <div class="progress-ring" :style="progressStyle">
            <div class="progress-ring-inner">
              <span>{{ progress.readinessPercentage }}%</span>
            </div>
          </div>
          <p class="progress-caption">{{ copy.progressLabels.readiness }}</p>
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
            <span>{{ copy.progressLabels.conflict }}</span>
            <strong>{{ progress.conflictCount }}</strong>
          </div>
        </div>
      </div>

      <div class="progress-actions">
        <button
          class="generate-prd-btn"
          :class="{ ready: progress.readyToGenerate }"
          type="button"
          :disabled="loading || generatingDocuments || generationDisabled"
          @click="emit('generate-documents')"
        >
          {{ generatingDocuments ? copy.generatingDocuments : copy.generateDocuments }}
        </button>
        <div v-if="hasPrdDocument && hasDesignDocument" class="document-ready-actions">
          <button
            class="go-coding-btn"
            type="button"
            :disabled="generationDisabled || openingGoCoding"
            @click="emit('go-coding')"
          >
            {{ openingGoCoding ? copy.openingGoCoding : copy.goCoding }}
          </button>
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
  gap: 12px;
  overflow: visible;
}

.requirement-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #ffffff;
  box-shadow: var(--shadow-soft, 0 8px 22px rgba(38, 55, 70, 0.08));
  overflow: hidden;
  height: auto;
}

.table-card {
  flex: 0 0 auto;
  width: 100%;
  min-height: 0;
  height: auto;
  display: flex;
  flex-direction: column;
}

.progress-card {
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
  padding-bottom: 6px;
}

.card-title {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title h3 {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.25;
  overflow-wrap: break-word;
}

.sync-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.12);
  color: #173f9f;
  font-size: 0.76rem;
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
  width: 22px;
  height: 22px;
  color: var(--accent-strong);
  flex-shrink: 0;
}

.card-state {
  margin: 0 16px 16px;
  padding: 12px;
  border-radius: 8px;
  border: 1px dashed rgba(37, 99, 235, 0.34);
  color: var(--muted);
  background: #fbfdfe;
  line-height: 1.45;
  font-size: 0.84rem;
}

.card-state.error {
  border-style: solid;
  border-color: rgba(220, 38, 38, 0.38);
  color: #991b1b;
  background: rgba(220, 38, 38, 0.13);
}

.progress-body {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 12px;
  padding: 0 16px 16px;
}

.progress-visual {
  display: grid;
  justify-items: center;
  gap: 10px;
}

.progress-ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  display: grid;
  place-items: center;
}

.progress-ring-inner {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  background: #fff;
  display: grid;
  place-items: center;
  box-shadow: inset 0 0 0 1px var(--line);
}

.progress-ring-inner span {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: 0;
  color: var(--ink);
}

.progress-caption {
  margin: 0;
  color: var(--muted);
  font-size: 0.76rem;
  font-weight: 700;
}

.progress-meta {
  display: grid;
  gap: 8px;
}

.progress-actions {
  padding: 0 16px 16px;
}

.generate-prd-btn {
  width: 100%;
  min-height: 40px;
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 8px;
  padding: 11px 14px;
  background: #ffffff;
  color: var(--accent-strong);
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

.generate-prd-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: rgba(37, 99, 235, 0.34);
  box-shadow: 0 10px 18px rgba(38, 55, 70, 0.08);
}

.generate-prd-btn.ready {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.22);
}

.generate-prd-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.document-ready-actions {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.go-coding-btn {
  width: 100%;
  min-height: 40px;
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 10px 12px;
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.22);
}

.go-coding-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: var(--accent-strong);
  box-shadow: 0 14px 28px rgba(37, 99, 235, 0.24);
}

.go-coding-btn:disabled {
  opacity: 0.72;
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
  font-size: 0.84rem;
}

.progress-row strong {
  color: var(--ink);
  font-size: 0.92rem;
}

.card-list-shell {
  flex: 0 0 auto;
  min-height: auto;
  overflow: visible;
  padding: 0 16px 16px;
}

.requirement-list {
  display: grid;
  gap: 10px;
}

.requirement-item-card {
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #ffffff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.requirement-item-card.missing {
  background: #ffffff;
}

.requirement-item-card.captured {
  border-color: rgba(37, 99, 235, 0.34);
  background: rgba(37, 99, 235, 0.05);
}

.requirement-item-card.pending {
  border-color: #eadfb9;
  background: rgba(178, 122, 0, 0.08);
}

.requirement-item-card.confirmed {
  border-color: rgba(37, 99, 235, 0.42);
  background: rgba(37, 99, 235, 0.08);
}

.requirement-item-card.conflict {
  border-color: #efc7c7;
  background: rgba(220, 38, 38, 0.06);
}

.requirement-item-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.requirement-item-head h4 {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.35;
  color: var(--ink);
}

.requirement-item-content {
  margin: 10px 0 0;
  color: var(--ink);
  line-height: 1.55;
  font-size: 0.84rem;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.requirement-item-notes {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.requirement-note {
  padding: 9px 10px;
  border-radius: 8px;
  background: #fbfdfe;
  border: 1px solid var(--line);
}

.requirement-note.question {
  background: rgba(178, 122, 0, 0.08);
  border-color: #eadfb9;
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
  min-width: 62px;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-pill.missing {
  background: #f0f3f8;
  color: #647280;
}

.status-pill.captured {
  background: rgba(59, 130, 246, 0.14);
  color: #1e40af;
}

.status-pill.pending {
  background: rgba(178, 122, 0, 0.16);
  color: #674300;
}

.status-pill.confirmed {
  background: rgba(37, 99, 235, 0.16);
  color: #1d4ed8;
}

.status-pill.conflict {
  background: rgba(220, 38, 38, 0.13);
  color: #991b1b;
}

@media (max-width: 1200px) {
  .progress-body {
    grid-template-columns: 1fr;
    justify-items: center;
  }

  .progress-meta {
    width: 100%;
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
