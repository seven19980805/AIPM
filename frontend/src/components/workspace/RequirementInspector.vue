<script setup lang="ts">
import StructuredRequirementPanel from '../StructuredRequirementPanel.vue'
import type { LanguageCode } from '../../types/session'
import type { InterviewStateV2 } from '../../types/interviewState'
import type {
  ICSubstrateEvidenceState,
  PMMethodologyState,
  StructuredRequirementModel,
} from '../../types/structuredRequirement'

defineProps<{
  open: boolean
  title: string
  closeLabel: string
  interviewState: InterviewStateV2 | null
  language: LanguageCode
  model: StructuredRequirementModel
  pmMethodologyState: PMMethodologyState
  icSubstrateEvidenceState: ICSubstrateEvidenceState
  loading: boolean
  syncing: boolean
  generatingDocuments: boolean
  openingGoCoding: boolean
  generationDisabled: boolean
  generationLabel: string
  error: string
}>()

const emit = defineEmits<{
  close: []
  generateDocuments: []
  goCoding: []
}>()
</script>

<template>
  <aside class="workspace-side" :class="{ 'mobile-open': open }">
    <div class="workspace-side-mobile-head">
      <div>
        <span>{{ title }}</span>
        <strong>
          {{ interviewState?.brief.confirmed_decisions ?? 0 }}/{{ interviewState?.brief.total_decisions ?? 5 }}
        </strong>
      </div>
      <button
        type="button"
        :aria-label="closeLabel"
        :title="closeLabel"
        @click="emit('close')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
    <div class="workspace-side-scroll">
      <StructuredRequirementPanel
        :language="language"
        :interview-state="interviewState"
        :model="model"
        :pm-methodology-state="pmMethodologyState"
        :ic-substrate-evidence-state="icSubstrateEvidenceState"
        :loading="loading"
        :syncing="syncing"
        :generating-documents="generatingDocuments"
        :opening-go-coding="openingGoCoding"
        :generation-disabled="generationDisabled"
        :generation-label="generationLabel"
        :error="error"
        @generate-documents="emit('generateDocuments')"
        @go-coding="emit('goCoding')"
      />
    </div>
  </aside>
</template>
