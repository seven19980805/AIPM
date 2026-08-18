<script setup lang="ts">
import { computed } from 'vue'

import type { SessionLaunchContext } from '../types/session'


const props = defineProps<{
  context: SessionLaunchContext
  busy?: boolean
}>()

const emit = defineEmits<{
  selectSuggestion: [text: string]
}>()

const language = computed(() => {
  const value = props.context.source.language.toLowerCase()
  if (value.startsWith('zh')) {
    return 'zh'
  }
  if (value === 'de' || value === 'ms') {
    return value
  }
  return 'en'
})

const copy = computed(() => ({
  en: {
    template: 'Template interview',
    draft: 'Draft completion',
    scratch: 'Scratch interview',
    firstDecision: 'Next decision',
    route: 'Delivery path',
    starters: 'Reply starters',
    source: 'Source',
    stageCount: 'stages',
    more: 'more',
  },
  zh: {
    template: '模板采访',
    draft: '草稿补全',
    scratch: '空白访谈',
    firstDecision: '下一个决策',
    route: '交付路径',
    starters: '回答起点',
    source: '来源',
    stageCount: '个阶段',
    more: '项待展开',
  },
  de: {
    template: 'Vorlageninterview',
    draft: 'Draft vervollstaendigen',
    scratch: 'Scratch Interview',
    firstDecision: 'Naechste Entscheidung',
    route: 'Delivery-Pfad',
    starters: 'Antwortstarter',
    source: 'Quelle',
    stageCount: 'Schritte',
    more: 'weitere',
  },
  ms: {
    template: 'Temu bual templat',
    draft: 'Lengkapkan draft',
    scratch: 'Temu bual scratch',
    firstDecision: 'Keputusan seterusnya',
    route: 'Laluan delivery',
    starters: 'Permulaan jawapan',
    source: 'Sumber',
    stageCount: 'peringkat',
    more: 'lagi',
  },
}[language.value]))

const modeLabel = computed(() => copy.value[props.context.mode])
const currentStageIndex = computed(() => {
  const index = props.context.stages.findIndex((stage) => stage.status === 'current')
  return index >= 0 ? index : 0
})
const visibleStages = computed(() => {
  const stages = props.context.stages
  if (stages.length <= 6) {
    return stages
  }
  const start = Math.max(0, Math.min(currentStageIndex.value - 1, stages.length - 6))
  return stages.slice(start, start + 6)
})
const hiddenStageCount = computed(() => props.context.stages.length - visibleStages.value.length)
const progressLabel = computed(() => {
  const budget = props.context.question_budget
  return budget ? `Q ${budget.asked}/${budget.maximum}` : ''
})
</script>

<template>
  <section class="launch-workspace" :data-mode="context.mode">
    <header class="launch-heading">
      <div class="launch-identity">
        <span class="launch-mode">{{ modeLabel }}</span>
        <span v-if="context.business_route" class="launch-route-label">{{ context.business_route }}</span>
        <span v-if="context.source.version" class="launch-version">v{{ context.source.version }}</span>
      </div>
      <h1>{{ context.title }}</h1>
      <p>{{ context.description }}</p>
    </header>

    <div class="launch-body">
      <div class="launch-decision">
        <div class="launch-section-label">
          <span>{{ copy.firstDecision }}</span>
          <span v-if="progressLabel" class="launch-progress">{{ progressLabel }}</span>
        </div>
        <h2>{{ context.question }}</h2>

        <div v-if="context.suggestions.length" class="launch-suggestions">
          <span class="launch-suggestions-label">{{ copy.starters }}</span>
          <div class="launch-suggestion-list">
            <button
              v-for="(suggestion, index) in context.suggestions"
              :key="suggestion.id"
              type="button"
              class="launch-suggestion"
              :disabled="busy"
              @click="emit('selectSuggestion', suggestion.text)"
            >
              <span>{{ index + 1 }}</span>
              <strong>{{ suggestion.label }}</strong>
            </button>
          </div>
        </div>
      </div>

      <aside v-if="context.stages.length" class="launch-route">
        <div class="launch-section-label">
          <span>{{ copy.route }}</span>
          <span>{{ context.stages.length }} {{ copy.stageCount }}</span>
        </div>
        <ol>
          <li
            v-for="stage in visibleStages"
            :key="stage.key"
            :class="stage.status"
          >
            <span class="stage-marker" aria-hidden="true"></span>
            <div>
              <small>{{ stage.track }}</small>
              <span>{{ stage.label }}</span>
            </div>
          </li>
        </ol>
        <p v-if="hiddenStageCount > 0" class="launch-more">
          +{{ hiddenStageCount }} {{ copy.more }}
        </p>
      </aside>
    </div>

    <footer v-if="context.source.type === 'template'" class="launch-source">
      <span>{{ copy.source }}</span>
      <strong>{{ context.source.name || context.source.id }}</strong>
    </footer>
  </section>
</template>

<style scoped>
.launch-workspace {
  container-name: launch-panel;
  container-type: inline-size;
  width: min(100%, 980px);
  margin: 0 auto;
  padding: clamp(24px, 4vh, 38px) clamp(20px, 3vw, 36px) 22px;
  color: var(--ink, #132238);
}

.launch-heading {
  max-width: 820px;
}

.launch-identity,
.launch-section-label,
.launch-source {
  display: flex;
  align-items: center;
  gap: 10px;
}

.launch-mode {
  color: #0b62b8;
  font-size: 12px;
  font-weight: 750;
  text-transform: uppercase;
}

.launch-version {
  color: #7d5a00;
  font-size: 11px;
  font-weight: 700;
}

.launch-route-label {
  color: var(--muted, #52637a);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.launch-heading h1 {
  max-width: 780px;
  margin: 10px 0 8px;
  color: inherit;
  font-size: clamp(23px, 2.5vw, 30px);
  line-height: 1.18;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

.launch-heading > p {
  max-width: 760px;
  margin: 0;
  color: var(--muted, #52637a);
  font-size: 14px;
  line-height: 1.65;
}

.launch-body {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(260px, 0.8fr);
  gap: clamp(30px, 5vw, 64px);
  margin-top: clamp(22px, 3vh, 30px);
  border-top: 1px solid var(--line, #dce4ee);
  padding-top: 18px;
}

.launch-decision {
  min-width: 0;
  border-left: 4px solid #0b6fc2;
  padding-left: 22px;
}

.launch-section-label {
  justify-content: space-between;
  color: var(--muted, #6b7b90);
  font-size: 11px;
  font-weight: 750;
  text-transform: uppercase;
}

.launch-progress {
  color: #0b62b8;
}

.launch-decision h2 {
  margin: 8px 0 16px;
  color: inherit;
  font-size: clamp(18px, 2vw, 24px);
  line-height: 1.35;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

.launch-suggestions-label {
  display: block;
  margin-bottom: 9px;
  color: var(--muted, #6b7b90);
  font-size: 12px;
  font-weight: 700;
}

.launch-suggestion-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.launch-suggestion {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr);
  align-items: center;
  min-height: 42px;
  border: 1px solid var(--line, #d7e0eb);
  border-radius: 6px;
  background: var(--panel, rgba(255, 255, 255, 0.82));
  color: var(--ink, #132238);
  padding: 7px 10px;
  text-align: left;
  cursor: pointer;
  transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
}

.launch-suggestion:hover:not(:disabled) {
  border-color: #2f81ca;
  background: var(--panel-soft, rgba(229, 242, 252, 0.92));
  transform: translateY(-1px);
}

.launch-suggestion:focus-visible {
  outline: 3px solid rgba(11, 111, 194, 0.2);
  outline-offset: 2px;
}

.launch-suggestion:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.launch-suggestion > span {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border-radius: 50%;
  background: #e5f2fc;
  color: #0b62b8;
  font-size: 11px;
  font-weight: 800;
}

.launch-suggestion strong {
  min-width: 0;
  font-size: 12px;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.launch-route {
  min-width: 0;
}

.launch-route ol {
  display: grid;
  gap: 0;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.launch-route li {
  position: relative;
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 9px;
  min-height: 48px;
  color: var(--muted, #52637a);
}

.launch-route li:not(:last-child)::after {
  position: absolute;
  top: 16px;
  bottom: -1px;
  left: 5px;
  width: 1px;
  background: var(--line, #d7e0eb);
  content: '';
}

.stage-marker {
  position: relative;
  z-index: 1;
  width: 11px;
  height: 11px;
  margin-top: 3px;
  border: 2px solid #a8b5c4;
  border-radius: 50%;
  background: var(--panel, #fff);
}

.launch-route li.current .stage-marker {
  border-color: #0b6fc2;
  background: #0b6fc2;
  box-shadow: 0 0 0 4px rgba(11, 111, 194, 0.12);
}

.launch-route li.complete .stage-marker {
  border-color: #23815a;
  background: #23815a;
}

.launch-route li small,
.launch-route li span {
  display: block;
}

.launch-route li small {
  margin-bottom: 2px;
  color: var(--muted, #7b899a);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
}

.launch-route li span {
  font-size: 12px;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.launch-route li.current span {
  color: var(--ink, #132238);
  font-weight: 720;
}

.launch-more {
  margin: 0 0 0 27px;
  color: var(--muted, #7b899a);
  font-size: 11px;
}

.launch-source {
  margin-top: 24px;
  border-top: 1px solid var(--line, #dce4ee);
  padding-top: 14px;
  color: var(--muted, #6b7b90);
  font-size: 11px;
}

.launch-source strong {
  min-width: 0;
  color: #7d5a00;
  overflow-wrap: anywhere;
}

@media (max-width: 760px) {
  .launch-workspace {
    padding: 24px 16px 20px;
  }
}

@container launch-panel (max-width: 760px) {
  .launch-body {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .launch-suggestion-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .launch-decision {
    padding-left: 16px;
  }

  .launch-route ol {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    column-gap: 18px;
  }

  .launch-route li {
    min-height: 42px;
  }

  .launch-route li::after {
    display: none;
  }

  .launch-more {
    margin-left: 0;
  }
}

@container launch-panel (max-width: 430px) {
  .launch-workspace {
    padding-top: 18px;
  }

  .launch-heading > p {
    display: -webkit-box;
    overflow: hidden;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 4;
  }

  .launch-suggestion-list,
  .launch-route ol {
    grid-template-columns: 1fr;
  }
}
</style>
