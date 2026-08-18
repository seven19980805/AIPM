<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  filterTemplateCatalog,
  templateCatalogDomains,
} from '../features/templates/templateCatalog'
import type { BusinessTemplateSummary } from '../types/businessTemplate'
import type { LanguageCode } from '../types/session'


const props = defineProps<{
  templates: BusinessTemplateSummary[]
  language: LanguageCode
  loading?: boolean
  disabled?: boolean
  applyingTemplateId?: string
}>()

const emit = defineEmits<{
  viewDetails: [templateId: string]
  start: [templateId: string]
}>()

const query = ref('')
const selectedDomain = ref('')

const copy = computed(() => ({
  en: {
    eyebrow: 'Business template catalog',
    title: 'Template Library',
    description: 'Find a proven requirement structure, inspect its coverage, and start a guided interview.',
    search: 'Search name, scenario, tag, or section',
    clear: 'Clear search',
    all: 'All',
    result: 'template',
    results: 'templates',
    sections: 'sections',
    details: 'Details',
    start: 'Start interview',
    starting: 'Starting',
    emptyTitle: 'No matching templates',
    emptyDescription: 'Try another keyword or business domain.',
  },
  zh: {
    eyebrow: '业务模板目录',
    title: '模板库',
    description: '查找成熟的需求结构，先看覆盖范围，再启动引导式采访。',
    search: '搜索名称、场景、标签或章节',
    clear: '清除搜索',
    all: '全部',
    result: '个模板',
    results: '个模板',
    sections: '个章节',
    details: '查看详情',
    start: '开始采访',
    starting: '启动中',
    emptyTitle: '没有匹配的模板',
    emptyDescription: '换一个关键词或业务域试试。',
  },
  de: {
    eyebrow: 'Katalog fuer Business-Vorlagen',
    title: 'Vorlagenbibliothek',
    description: 'Bewaehrte Anforderungsstruktur finden, Abdeckung pruefen und ein gefuehrtes Interview starten.',
    search: 'Name, Szenario, Tag oder Abschnitt suchen',
    clear: 'Suche leeren',
    all: 'Alle',
    result: 'Vorlage',
    results: 'Vorlagen',
    sections: 'Abschnitte',
    details: 'Details',
    start: 'Interview starten',
    starting: 'Wird gestartet',
    emptyTitle: 'Keine passende Vorlage',
    emptyDescription: 'Versuche ein anderes Stichwort oder eine andere Domaene.',
  },
  ms: {
    eyebrow: 'Katalog templat perniagaan',
    title: 'Pustaka Templat',
    description: 'Cari struktur requirement yang terbukti, semak liputan dan mula temu bual berpandu.',
    search: 'Cari nama, senario, tag atau seksyen',
    clear: 'Kosongkan carian',
    all: 'Semua',
    result: 'templat',
    results: 'templat',
    sections: 'seksyen',
    details: 'Butiran',
    start: 'Mula temu bual',
    starting: 'Sedang mula',
    emptyTitle: 'Tiada templat sepadan',
    emptyDescription: 'Cuba kata kunci atau domain lain.',
  },
}[props.language]))

const domains = computed(() => templateCatalogDomains(props.templates))
const filteredTemplates = computed(() => filterTemplateCatalog(props.templates, {
  query: query.value,
  domain: selectedDomain.value,
}))
const resultLabel = computed(() => (
  filteredTemplates.value.length === 1 ? copy.value.result : copy.value.results
))

watch(domains, (availableDomains) => {
  if (
    selectedDomain.value
    && !availableDomains.some((domain) => domain.id === selectedDomain.value)
  ) {
    selectedDomain.value = ''
  }
})

function clearSearch() {
  query.value = ''
}

function displayFacet(value: string): string {
  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}
</script>

<template>
  <section class="template-catalog">
    <header class="catalog-header">
      <div>
        <p>{{ copy.eyebrow }}</p>
        <h1>{{ copy.title }}</h1>
        <span>{{ copy.description }}</span>
      </div>
      <strong>{{ filteredTemplates.length }} {{ resultLabel }}</strong>
    </header>

    <div class="catalog-toolbar">
      <label class="catalog-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <circle cx="11" cy="11" r="7"/>
          <path d="m20 20-4-4"/>
        </svg>
        <input v-model="query" type="search" :placeholder="copy.search" />
        <button
          v-if="query"
          type="button"
          :aria-label="copy.clear"
          :title="copy.clear"
          @click="clearSearch"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </label>

      <div class="catalog-domains" role="tablist" :aria-label="copy.eyebrow">
        <button
          type="button"
          role="tab"
          :aria-selected="!selectedDomain"
          :class="{ active: !selectedDomain }"
          @click="selectedDomain = ''"
        >
          {{ copy.all }}
          <span>{{ templates.length }}</span>
        </button>
        <button
          v-for="domain in domains"
          :key="domain.id"
          type="button"
          role="tab"
          :aria-selected="selectedDomain === domain.id"
          :class="{ active: selectedDomain === domain.id }"
          @click="selectedDomain = domain.id"
        >
          {{ displayFacet(domain.label) }}
          <span>{{ domain.count }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="catalog-loading" aria-busy="true">
      <span v-for="index in 6" :key="index"></span>
    </div>

    <div v-else-if="filteredTemplates.length" class="catalog-grid">
      <article
        v-for="template in filteredTemplates"
        :key="template.template_id"
        class="catalog-item"
      >
        <div class="catalog-item-main">
          <div class="catalog-item-meta">
            <span>{{ displayFacet(template.business_domain || template.template_category) }}</span>
            <span v-if="template.version">v{{ template.version }}</span>
          </div>
          <h2>{{ template.template_name }}</h2>
          <p>{{ template.description }}</p>
          <div class="catalog-item-coverage">
            <strong>{{ template.section_count }} {{ copy.sections }}</strong>
            <span
              v-for="tag in template.tags.slice(0, 3)"
              :key="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="catalog-item-actions">
          <button
            type="button"
            class="catalog-details"
            :disabled="disabled"
            @click="emit('viewDetails', template.template_id)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="3"/>
              <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/>
            </svg>
            {{ copy.details }}
          </button>
          <button
            type="button"
            class="catalog-start"
            :disabled="disabled || Boolean(applyingTemplateId)"
            @click="emit('start', template.template_id)"
          >
            <span
              v-if="applyingTemplateId === template.template_id"
              class="catalog-spinner"
              aria-hidden="true"
            ></span>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M5 12h14"/>
              <path d="m13 6 6 6-6 6"/>
            </svg>
            {{ applyingTemplateId === template.template_id ? copy.starting : copy.start }}
          </button>
        </div>
      </article>
    </div>

    <div v-else class="catalog-empty">
      <strong>{{ copy.emptyTitle }}</strong>
      <span>{{ copy.emptyDescription }}</span>
    </div>
  </section>
</template>

<style scoped>
.template-catalog {
  display: grid;
  align-content: start;
  gap: 18px;
  height: 100%;
  min-height: 0;
  padding: 10px 8px 18px 0;
  overflow: auto;
  color: var(--ink);
}

.catalog-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding: 12px 4px 4px;
}

.catalog-header p {
  margin: 0 0 6px;
  color: var(--accent-strong);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.catalog-header h1 {
  margin: 0;
  font-size: clamp(26px, 3vw, 38px);
  line-height: 1.08;
  letter-spacing: 0;
}

.catalog-header div > span {
  display: block;
  max-width: 700px;
  margin-top: 8px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

.catalog-header > strong {
  flex: 0 0 auto;
  color: var(--muted);
  font-size: 12px;
}

.catalog-toolbar {
  position: sticky;
  top: 0;
  z-index: 4;
  display: grid;
  grid-template-columns: minmax(240px, 360px) minmax(0, 1fr);
  gap: 14px;
  padding: 10px 4px;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: color-mix(in srgb, var(--panel) 88%, transparent);
  backdrop-filter: blur(12px);
}

.catalog-search {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr) 28px;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  border: 1px solid var(--line-strong);
  border-radius: 6px;
  background: var(--panel);
  padding: 0 8px 0 12px;
}

.catalog-search > svg,
.catalog-search button svg,
.catalog-item-actions svg {
  width: 17px;
  height: 17px;
}

.catalog-search > svg {
  color: var(--muted);
}

.catalog-search input {
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--ink);
  font: inherit;
  font-size: 13px;
}

.catalog-search input::placeholder {
  color: var(--muted);
}

.catalog-search button {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border: 0;
  border-radius: 4px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
}

.catalog-search:focus-within {
  border-color: var(--accent);
  box-shadow: var(--focus-ring);
}

.catalog-domains {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.catalog-domains::-webkit-scrollbar {
  display: none;
}

.catalog-domains button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto;
  min-height: 34px;
  border: 1px solid transparent;
  border-radius: 5px;
  background: transparent;
  color: var(--muted);
  padding: 0 9px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.catalog-domains button span {
  color: inherit;
  font-size: 10px;
  opacity: 0.72;
}

.catalog-domains button.active {
  border-color: var(--line-strong);
  background: var(--panel);
  color: var(--accent-strong);
}

.catalog-grid,
.catalog-loading {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 0 4px;
}

.catalog-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 142px;
  min-height: 178px;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: color-mix(in srgb, var(--panel) 92%, transparent);
  overflow: hidden;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}

.catalog-item:hover {
  border-color: var(--line-strong);
  box-shadow: var(--shadow-soft);
}

.catalog-item-main {
  min-width: 0;
  padding: 16px;
}

.catalog-item-meta,
.catalog-item-coverage {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 9px;
}

.catalog-item-meta {
  color: var(--accent-strong);
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
}

.catalog-item-meta span:last-child {
  color: #7d5a00;
}

.catalog-item h2 {
  margin: 8px 0 6px;
  font-size: 17px;
  line-height: 1.25;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

.catalog-item p {
  display: -webkit-box;
  min-height: 40px;
  margin: 0;
  overflow: hidden;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.catalog-item-coverage {
  margin-top: 14px;
  color: var(--muted);
  font-size: 10px;
}

.catalog-item-coverage strong {
  color: var(--ink);
}

.catalog-item-coverage span {
  padding-left: 8px;
  border-left: 1px solid var(--line);
}

.catalog-item-actions {
  display: grid;
  align-content: center;
  gap: 8px;
  border-left: 1px solid var(--line);
  background: color-mix(in srgb, var(--panel-soft) 72%, transparent);
  padding: 12px;
}

.catalog-item-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 38px;
  border-radius: 5px;
  padding: 0 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
}

.catalog-details {
  border: 1px solid var(--line-strong);
  background: var(--panel);
  color: var(--ink);
}

.catalog-start {
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
}

.catalog-item-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.catalog-spinner {
  width: 15px;
  height: 15px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: catalog-spin 700ms linear infinite;
}

.catalog-loading span {
  min-height: 178px;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: linear-gradient(90deg, var(--panel) 20%, var(--panel-soft) 45%, var(--panel) 70%);
  background-size: 240% 100%;
  animation: catalog-loading 1.4s ease infinite;
}

.catalog-empty {
  display: grid;
  justify-items: center;
  gap: 6px;
  padding: 64px 20px;
  color: var(--muted);
  text-align: center;
}

.catalog-empty strong {
  color: var(--ink);
}

@keyframes catalog-spin {
  to { transform: rotate(360deg); }
}

@keyframes catalog-loading {
  to { background-position: -140% 0; }
}

@media (max-width: 920px) {
  .catalog-toolbar,
  .catalog-grid,
  .catalog-loading {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .template-catalog {
    padding-right: 0;
  }

  .catalog-header {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }

  .catalog-item {
    grid-template-columns: 1fr;
  }

  .catalog-item-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    border-top: 1px solid var(--line);
    border-left: 0;
  }
}
</style>
