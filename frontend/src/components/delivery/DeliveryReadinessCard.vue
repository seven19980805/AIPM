<script setup lang="ts">
import { computed } from 'vue'

import type { LanguageCode } from '../../types/session'
import type { InterviewStage, InterviewStateV2 } from '../../types/interviewState'

type DeliveryCopy = {
  title: string
  stage: string
  quickDecisions: string
  assumptions: string
  strictReview: string
  remaining: string
  manual: string
  complete: string
  document: string
  documentStatuses: Record<string, string>
  stages: Record<InterviewStage, string>
  syncing: string
  generating: string
  opening: string
  generate: string
  generateDraft: string
  refresh: string
  goCoding: string
}

const props = withDefaults(
  defineProps<{
    language: LanguageCode
    interviewState: InterviewStateV2 | null
    loading?: boolean
    syncing?: boolean
    generatingDocuments?: boolean
    openingGoCoding?: boolean
    generationDisabled?: boolean
    generationLabel?: string
  }>(),
  {
    loading: false,
    syncing: false,
    generatingDocuments: false,
    openingGoCoding: false,
    generationDisabled: false,
    generationLabel: '',
  },
)

const emit = defineEmits<{
  generateDocuments: []
  goCoding: []
}>()

const copyByLanguage: Record<LanguageCode, DeliveryCopy> = {
  en: {
    title: 'Delivery status',
    stage: 'Current stage',
    quickDecisions: 'Core evidence',
    assumptions: 'Open TBDs',
    strictReview: 'Strict review',
    remaining: 'remaining',
    manual: 'checklist only',
    complete: 'Complete',
    document: 'Build Brief',
    documentStatuses: { missing: 'Not generated', current: 'Current', stale: 'Needs refresh' },
    stages: {
      brief_discovery: 'Collect five core evidence areas',
      brief_ready: 'Ready to generate Build Brief',
      strict_review: 'Strict delivery review',
      refresh_brief: 'Refresh the Build Brief',
      handoff_ready: 'Ready for Go Coding',
    },
    syncing: 'Syncing',
    generating: 'Generating...',
    opening: 'Opening...',
    generate: 'Generate Build Brief',
    generateDraft: 'Generate draft with TBDs',
    refresh: 'Refresh Build Brief',
    goCoding: 'Open Go Coding',
  },
  zh: {
    title: '交付状态',
    stage: '当前阶段',
    quickDecisions: '核心证据',
    assumptions: '待确认项',
    strictReview: '严格审查',
    remaining: '项待确认',
    manual: '仅保留清单',
    complete: '已完成',
    document: '开发简报',
    documentStatuses: { missing: '尚未生成', current: '当前版本', stale: '需要刷新' },
    stages: {
      brief_discovery: '补齐 5 类核心证据',
      brief_ready: '可以生成开发简报',
      strict_review: '严格交付审查',
      refresh_brief: '刷新开发简报',
      handoff_ready: '可以进入 Go Coding',
    },
    syncing: '同步中',
    generating: '生成中...',
    opening: '正在打开...',
    generate: '生成开发简报',
    generateDraft: '生成含待确认项的草稿',
    refresh: '刷新开发简报',
    goCoding: '打开 Go Coding',
  },
  de: {
    title: 'Lieferstatus',
    stage: 'Aktuelle Phase',
    quickDecisions: 'Kernevidenz',
    assumptions: 'Offene TBDs',
    strictReview: 'Strenge Pruefung',
    remaining: 'offen',
    manual: 'nur Checkliste',
    complete: 'Abgeschlossen',
    document: 'Build Brief',
    documentStatuses: { missing: 'Nicht erzeugt', current: 'Aktuell', stale: 'Zu erneuern' },
    stages: {
      brief_discovery: 'Fuenf Kernevidenzbereiche erfassen',
      brief_ready: 'Build Brief kann erzeugt werden',
      strict_review: 'Strenge Lieferpruefung',
      refresh_brief: 'Build Brief erneuern',
      handoff_ready: 'Bereit fuer Go Coding',
    },
    syncing: 'Synchronisiert',
    generating: 'Wird erzeugt...',
    opening: 'Wird geoeffnet...',
    generate: 'Build Brief erzeugen',
    generateDraft: 'Entwurf mit TBDs erzeugen',
    refresh: 'Build Brief erneuern',
    goCoding: 'Go Coding oeffnen',
  },
  ms: {
    title: 'Status penghantaran',
    stage: 'Peringkat semasa',
    quickDecisions: 'Bukti teras',
    assumptions: 'TBD terbuka',
    strictReview: 'Semakan ketat',
    remaining: 'belum selesai',
    manual: 'senarai semak sahaja',
    complete: 'Selesai',
    document: 'Build Brief',
    documentStatuses: { missing: 'Belum dijana', current: 'Semasa', stale: 'Perlu dikemas kini' },
    stages: {
      brief_discovery: 'Kumpulkan lima bidang bukti teras',
      brief_ready: 'Sedia jana Build Brief',
      strict_review: 'Semakan penghantaran ketat',
      refresh_brief: 'Kemas kini Build Brief',
      handoff_ready: 'Sedia untuk Go Coding',
    },
    syncing: 'Menyegerak',
    generating: 'Menjana...',
    opening: 'Membuka...',
    generate: 'Jana Build Brief',
    generateDraft: 'Jana draf dengan TBD',
    refresh: 'Kemas kini Build Brief',
    goCoding: 'Buka Go Coding',
  },
}

const copy = computed(() => copyByLanguage[props.language] ?? copyByLanguage.en)
const stageLabel = computed(() => {
  const stage = props.interviewState?.stage ?? 'brief_discovery'
  return copy.value.stages[stage]
})
const reviewLabel = computed(() => {
  if (props.interviewState?.review.ready) return copy.value.complete
  const remaining = `${props.interviewState?.review.remaining_count ?? 0} ${copy.value.remaining}`
  return props.interviewState?.review.input_mode === 'manual'
    ? `${remaining} · ${copy.value.manual}`
    : remaining
})
const showStrictReview = computed(() =>
  ['strict_review', 'refresh_brief', 'handoff_ready'].includes(
    props.interviewState?.stage ?? 'brief_discovery',
  ),
)
const documentStatusLabel = computed(() => {
  const status = props.interviewState?.brief.document_status ?? 'missing'
  return copy.value.documentStatuses[status] ?? status
})
const actionLocked = computed(
  () =>
    props.loading ||
    props.generatingDocuments ||
    props.openingGoCoding ||
    props.generationDisabled,
)
const canGenerate = computed(() => Boolean(props.interviewState?.actions.can_generate_brief))
const canHandoff = computed(() => Boolean(props.interviewState?.actions.can_handoff))
const generateLabel = computed(() => {
  if (props.generatingDocuments) return copy.value.generating
  if (props.generationLabel) return props.generationLabel
  if (props.interviewState?.brief.document_status === 'stale') return copy.value.refresh
  return (props.interviewState?.brief.assumption_count ?? 0) > 0
    ? copy.value.generateDraft
    : copy.value.generate
})
</script>

<template>
  <section class="delivery-card">
    <header class="delivery-head">
      <div>
        <span>{{ copy.stage }}</span>
        <h3>{{ copy.title }}</h3>
      </div>
      <span v-if="syncing" class="sync-label">{{ copy.syncing }}</span>
    </header>

    <div class="delivery-stage">
      <span class="stage-marker" aria-hidden="true"></span>
      <strong>{{ stageLabel }}</strong>
    </div>

    <dl class="delivery-facts">
      <div>
        <dt>{{ copy.quickDecisions }}</dt>
        <dd>
          {{ interviewState?.brief.confirmed_decisions ?? 0 }}/{{ interviewState?.brief.total_decisions ?? 5 }}
        </dd>
      </div>
      <div v-if="(interviewState?.brief.assumption_count ?? 0) > 0">
        <dt>{{ copy.assumptions }}</dt>
        <dd>{{ interviewState?.brief.assumption_count ?? 0 }}</dd>
      </div>
      <div v-if="showStrictReview">
        <dt>{{ copy.strictReview }}</dt>
        <dd>{{ reviewLabel }}</dd>
      </div>
      <div :class="{ stale: interviewState?.brief.document_status === 'stale' }">
        <dt>{{ copy.document }}</dt>
        <dd>{{ documentStatusLabel }}</dd>
      </div>
    </dl>

    <div class="delivery-actions">
      <button
        v-if="canHandoff"
        type="button"
        class="primary-action"
        :disabled="actionLocked"
        @click="emit('goCoding')"
      >
        {{ openingGoCoding ? copy.opening : copy.goCoding }}
      </button>
      <button
        v-else
        type="button"
        class="primary-action"
        :disabled="actionLocked || !canGenerate"
        @click="emit('generateDocuments')"
      >
        {{ generateLabel }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.delivery-card {
  order: 1;
  display: grid;
  gap: 12px;
  width: 100%;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: var(--shadow-soft);
}

.delivery-head,
.delivery-stage,
.delivery-facts div,
.delivery-actions {
  display: flex;
  align-items: center;
}

.delivery-head {
  justify-content: space-between;
  gap: 12px;
}

.delivery-head span,
.delivery-facts dt {
  color: var(--muted);
  font-size: 0.7rem;
  font-weight: 750;
}

.delivery-head h3 {
  margin: 3px 0 0;
  color: var(--ink);
  font-size: 1rem;
}

.sync-label {
  color: var(--accent-strong) !important;
}

.delivery-stage {
  gap: 9px;
  padding: 10px 11px;
  border-radius: 8px;
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.stage-marker {
  width: 9px;
  height: 9px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: currentColor;
}

.delivery-stage strong {
  font-size: 0.85rem;
  line-height: 1.35;
}

.delivery-facts {
  display: grid;
  gap: 1px;
  margin: 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--line);
}

.delivery-facts div {
  justify-content: space-between;
  gap: 12px;
  padding: 9px 10px;
  background: var(--panel);
}

.delivery-facts dd {
  margin: 0;
  color: var(--ink);
  font-size: 0.78rem;
  font-weight: 800;
  text-align: right;
}

.delivery-facts .stale dd {
  color: var(--status-warning-ink);
}

.delivery-actions {
  justify-content: stretch;
}

.primary-action {
  width: 100%;
  min-height: 42px;
  border: 1px solid var(--accent);
  border-radius: 8px;
  background: var(--accent);
  color: white;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 800;
  cursor: pointer;
}

.primary-action:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

.primary-action:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

:global(.app-shell[data-theme='dark'] .delivery-card) {
  background: rgba(15, 27, 40, 0.82);
}
</style>
