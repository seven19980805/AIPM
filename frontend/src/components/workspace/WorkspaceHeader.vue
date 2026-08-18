<script setup lang="ts">
import { ref } from 'vue'

import type { LanguageCode } from '../../types/session'

type ThemeMode = 'light' | 'dark'

defineProps<{
  language: LanguageCode
  languageOptions: Array<{ code: LanguageCode; label: string }>
  themeMode: ThemeMode
  themeToggleLabel: string
  themeToggleValue: string
  tagline: string
  navigationLabel: string
  navigationExpanded: boolean
  languageLabel: string
  requirementsLabel: string
  briefProgressLabel: string
  inspectorOpen: boolean
  showInspector: boolean
}>()

const emit = defineEmits<{
  toggleNavigation: []
  toggleInspector: []
  toggleTheme: []
  selectLanguage: [language: LanguageCode]
}>()

const languageMenuRef = ref<HTMLDetailsElement | null>(null)

function chooseLanguage(language: LanguageCode) {
  emit('selectLanguage', language)
  if (languageMenuRef.value) {
    languageMenuRef.value.open = false
  }
}
</script>

<template>
  <header class="main-topbar">
    <button
      class="mobile-nav-trigger"
      type="button"
      :aria-label="navigationLabel"
      :title="navigationLabel"
      :aria-expanded="navigationExpanded"
      @click="emit('toggleNavigation')"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="4" y1="7" x2="20" y2="7"/>
        <line x1="4" y1="12" x2="20" y2="12"/>
        <line x1="4" y1="17" x2="20" y2="17"/>
      </svg>
    </button>

    <div class="ats-lockup" aria-label="AT&S AI Platform">
      <img class="ats-lockup-logo" src="../../logo.svg" alt="AT&S AI Platform" />
    </div>

    <p class="main-topbar-tagline">{{ tagline }}</p>

    <div class="main-topbar-actions">
      <button
        v-if="showInspector"
        class="mobile-inspector-trigger"
        type="button"
        :aria-label="requirementsLabel"
        :title="requirementsLabel"
        :aria-expanded="inspectorOpen"
        @click="emit('toggleInspector')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 5h10"/>
          <path d="M9 12h10"/>
          <path d="M9 19h10"/>
          <path d="m3 5 1 1 2-2"/>
          <path d="m3 12 1 1 2-2"/>
          <path d="m3 19 1 1 2-2"/>
        </svg>
        <span>{{ briefProgressLabel }}</span>
      </button>

      <button
        class="theme-toggle"
        type="button"
        :aria-label="themeToggleLabel"
        :title="themeToggleLabel"
        @click="emit('toggleTheme')"
      >
        <span class="theme-toggle-icon" aria-hidden="true">
          <svg
            v-if="themeMode === 'dark'"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="4"/>
            <path d="M12 2v2"/>
            <path d="M12 20v2"/>
            <path d="m4.93 4.93 1.41 1.41"/>
            <path d="m17.66 17.66 1.41 1.41"/>
            <path d="M2 12h2"/>
            <path d="M20 12h2"/>
            <path d="m6.34 17.66-1.41 1.41"/>
            <path d="m19.07 4.93-1.41 1.41"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.7 6.7 0 0 0 9.8 9.8Z"/>
          </svg>
        </span>
        <span>{{ themeToggleValue }}</span>
      </button>

      <details ref="languageMenuRef" class="language-switcher">
        <summary>
          <span class="language-switcher-label">{{ languageLabel }}</span>
          <span class="language-switcher-value">
            {{ languageOptions.find((option) => option.code === language)?.label ?? language }}
          </span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </summary>

        <div class="language-switcher-menu">
          <button
            v-for="option in languageOptions"
            :key="option.code"
            type="button"
            class="language-switcher-option"
            :class="{ active: language === option.code }"
            @click="chooseLanguage(option.code)"
          >
            {{ option.label }}
          </button>
        </div>
      </details>
    </div>
  </header>
</template>
