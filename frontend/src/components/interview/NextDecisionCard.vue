<script setup lang="ts">
import { computed } from 'vue'

import type { LanguageCode } from '../../types/session'
import type {
  InterviewReplyContext,
  InterviewStateV2,
} from '../../types/interviewState'

const props = withDefaults(
  defineProps<{
    language: LanguageCode
    interviewState: InterviewStateV2 | null
    disabled?: boolean
  }>(),
  {
    disabled: false,
  },
)

const emit = defineEmits<{
  reply: [context: InterviewReplyContext]
  focusInput: []
  editProposal: [text: string]
  selectOption: [text: string]
}>()

const copyByLanguage = {
  en: {
    eyebrow: 'Next decision',
    example: 'Use an example',
    answer: 'Write my answer',
    accept: 'Adopt this proposal',
    edit: 'Edit it first',
    proposal: 'Proposed answer',
    defer: 'Mark as TBD & continue',
    choices: 'Choose the closest answer',
    choiceHelp: 'Clicking an answer sends it directly. You can also write your own.',
    pace: 'One reply can cover several decisions. If something is still unclear, mark it TBD and move on.',
  },
  zh: {
    eyebrow: '下一项决策',
    example: '给我一个例子',
    answer: '我自己回答',
    accept: '采用这个提案',
    edit: '先修改再提交',
    proposal: '单项提案',
    defer: '标为待确认，继续',
    choices: '选择最接近的答案',
    choiceHelp: '点击后会直接作为你的回答发送；也可以自己输入。',
    pace: '一条回复可以覆盖多个决策点；仍不确定的内容可先标为待确认。',
  },
  de: {
    eyebrow: 'Naechste Entscheidung',
    example: 'Beispiel anzeigen',
    answer: 'Selbst antworten',
    accept: 'Vorschlag uebernehmen',
    edit: 'Zuerst bearbeiten',
    proposal: 'Vorgeschlagene Antwort',
    defer: 'Als TBD markieren',
    choices: 'Passende Antwort wählen',
    choiceHelp: 'Ein Klick sendet die Antwort direkt. Du kannst auch selbst schreiben.',
    pace: 'Eine Antwort kann mehrere Entscheidungen abdecken. Unklares kann als TBD markiert werden.',
  },
  ms: {
    eyebrow: 'Keputusan seterusnya',
    example: 'Tunjuk contoh',
    answer: 'Tulis jawapan saya',
    accept: 'Guna cadangan ini',
    edit: 'Edit dahulu',
    proposal: 'Jawapan dicadangkan',
    defer: 'Tanda sebagai TBD',
    choices: 'Pilih jawapan paling hampir',
    choiceHelp: 'Klik menghantar jawapan terus. Anda juga boleh menulis jawapan sendiri.',
    pace: 'Satu jawapan boleh merangkumi beberapa keputusan. Perkara yang belum jelas boleh ditanda sebagai TBD.',
  },
} satisfies Record<LanguageCode, Record<string, string>>

const copy = computed(() => copyByLanguage[props.language] ?? copyByLanguage.en)
const decision = computed(() => props.interviewState?.next_decision ?? null)
const proposal = computed(() => decision.value?.proposal ?? null)

function requestExample() {
  if (!decision.value) return
  emit('reply', {
    decision_id: decision.value.decision_id,
    action: 'request_example',
  })
}

function acceptProposal() {
  if (!decision.value || !proposal.value) return
  emit('reply', {
    decision_id: decision.value.decision_id,
    action: 'accept_proposal',
    proposal_id: proposal.value.proposal_id,
  })
}

function deferDecision() {
  if (!decision.value?.can_defer) return
  emit('reply', {
    decision_id: decision.value.decision_id,
    action: 'defer_decision',
  })
}
</script>

<template>
  <section
    v-if="decision"
    class="next-decision-card"
    :data-decision-id="decision.decision_id"
    aria-live="polite"
  >
    <div class="next-decision-head">
      <span>{{ copy.eyebrow }}</span>
    </div>

    <div class="next-decision-copy">
      <p v-if="decision.label" class="next-decision-label">{{ decision.label }}</p>
      <h3>{{ decision.question }}</h3>
      <p v-if="decision.hint && !decision.options.length" class="next-decision-hint">{{ decision.hint }}</p>
      <p v-if="!proposal && !decision.options.length" class="next-decision-pace">{{ copy.pace }}</p>
    </div>

    <div v-if="!proposal && decision.options.length" class="next-decision-options">
      <div class="next-decision-options-head">
        <strong>{{ copy.choices }}</strong>
        <span>{{ copy.choiceHelp }}</span>
      </div>
      <button
        v-for="(option, index) in decision.options"
        :key="option.option_id"
        type="button"
        :disabled="disabled"
        :title="option.text"
        @click="emit('selectOption', option.text)"
      >
        <span aria-hidden="true">{{ String.fromCharCode(65 + index) }}</span>
        <strong>{{ option.label || option.text }}</strong>
        <span class="option-arrow" aria-hidden="true">→</span>
      </button>
    </div>

    <div v-if="proposal" class="next-decision-proposal">
      <span>{{ copy.proposal }}</span>
      <p>{{ proposal.text }}</p>
    </div>

    <div class="next-decision-actions">
      <template v-if="proposal">
        <button
          type="button"
          class="next-decision-primary"
          :disabled="disabled"
          @click="acceptProposal"
        >
          {{ copy.accept }}
        </button>
        <button
          type="button"
          class="next-decision-secondary"
          :disabled="disabled"
          @click="emit('editProposal', proposal.text)"
        >
          {{ copy.edit }}
        </button>
      </template>
      <template v-else-if="!decision.options.length">
        <button
          type="button"
          class="next-decision-secondary"
          :disabled="disabled"
          @click="requestExample"
        >
          {{ copy.example }}
        </button>
        <button
          type="button"
          class="next-decision-primary"
          :disabled="disabled"
          @click="emit('focusInput')"
        >
          {{ copy.answer }}
        </button>
      </template>
      <button
        v-else
        type="button"
        class="next-decision-secondary"
        :disabled="disabled"
        @click="emit('focusInput')"
      >
        {{ copy.answer }}
      </button>
      <button
        v-if="decision.can_defer"
        type="button"
        class="next-decision-tertiary"
        :disabled="disabled"
        @click="deferDecision"
      >
        {{ copy.defer }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.next-decision-card {
  display: grid;
  gap: 12px;
  padding: 15px 17px;
  border: 1px solid color-mix(in srgb, var(--accent) 30%, var(--line));
  border-left: 4px solid var(--accent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--panel) 92%, var(--accent-soft));
  box-shadow: var(--shadow-soft);
}

.next-decision-head,
.next-decision-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.next-decision-head span,
.next-decision-label,
.next-decision-proposal > span {
  margin: 0;
  color: var(--accent-strong);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.next-decision-copy {
  display: grid;
  gap: 5px;
}

.next-decision-copy h3 {
  margin: 0;
  color: var(--ink);
  font-size: clamp(1rem, 1.4vw, 1.16rem);
  line-height: 1.4;
}

.next-decision-hint,
.next-decision-pace,
.next-decision-proposal p {
  margin: 0;
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.5;
}

.next-decision-pace {
  font-size: 0.76rem;
}

.next-decision-proposal {
  display: grid;
  gap: 5px;
  padding: 11px 12px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--panel);
}

.next-decision-options {
  display: grid;
  gap: 8px;
}

.next-decision-options-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.next-decision-options-head strong {
  color: var(--ink);
  font-size: 0.8rem;
}

.next-decision-options-head span {
  color: var(--muted);
  font-size: 0.72rem;
}

.next-decision-options > button {
  min-width: 0;
  display: grid;
  grid-template-columns: 26px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--panel);
  color: var(--ink);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 150ms ease,
    background 150ms ease,
    transform 150ms ease;
}

.next-decision-options > button > span:first-child {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 7px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 0.72rem;
  font-weight: 850;
}

.next-decision-options > button > strong {
  font-size: 0.82rem;
  font-weight: 650;
  line-height: 1.45;
}

.next-decision-options > button:hover:not(:disabled),
.next-decision-options > button:focus-visible {
  border-color: color-mix(in srgb, var(--accent) 52%, var(--line));
  background: color-mix(in srgb, var(--panel) 94%, var(--accent-soft));
  transform: translateY(-1px);
}

.option-arrow {
  color: var(--accent-strong);
  font-weight: 800;
}

.next-decision-proposal p {
  color: var(--ink);
}

.next-decision-actions {
  justify-content: flex-end;
}

.next-decision-actions button {
  min-height: 38px;
  padding: 8px 13px;
  border-radius: 8px;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 750;
  cursor: pointer;
}

.next-decision-primary {
  border: 1px solid var(--accent);
  background: var(--accent);
  color: white;
}

.next-decision-secondary {
  border: 1px solid var(--line-strong, var(--line));
  background: var(--panel);
  color: var(--ink);
}

.next-decision-tertiary {
  border: 0;
  background: transparent;
  color: var(--muted);
}

.next-decision-actions button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.next-decision-options > button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.next-decision-options > button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.next-decision-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

@media (max-width: 640px) {
  .next-decision-head,
  .next-decision-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .next-decision-actions button {
    min-height: 44px;
    width: 100%;
  }

  .next-decision-options-head {
    align-items: flex-start;
    flex-direction: column;
    gap: 3px;
  }
}
</style>
