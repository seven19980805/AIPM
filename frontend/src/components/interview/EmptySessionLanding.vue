<script setup lang="ts">
import { computed } from 'vue'

import type {
  BusinessRoute,
  LanguageCode,
  SessionLaunchSuggestion,
} from '../../types/session'

type BusinessRouteOption = {
  id: BusinessRoute
  label: string
  text: string
}

const props = withDefaults(
  defineProps<{
    language: LanguageCode
    routes: BusinessRouteOption[]
    selectedRoute: BusinessRoute | ''
    starters: SessionLaunchSuggestion[]
    busy?: boolean
  }>(),
  {
    busy: false,
  },
)

const emit = defineEmits<{
  selectRoute: [route: BusinessRoute]
  selectStarter: [text: string]
}>()

const copyByLanguage = {
  en: {
    routeEyebrow: 'New requirement',
    routeTitle: 'Choose a business route',
    routeDescription: 'This selects the right expert context. It does not prefill or confirm any requirement.',
    eyebrow: 'Start with one sentence',
    title: 'What are you trying to improve?',
    description: 'Describe the user, the work, or the problem. AI PM will shape the rest and only follow up where evidence is missing.',
    starters: 'Or start with an example',
  },
  zh: {
    routeEyebrow: '新需求',
    routeTitle: '先选择业务链路',
    routeDescription: '只用于切换对应的专家上下文，不会预填或自动确认任何需求。',
    eyebrow: '先说一句就够了',
    title: '你想解决什么问题？',
    description: '说清用户、工作或问题中的任意一个即可。AI PM 会帮你补齐其余内容，只追问真正缺失的证据。',
    starters: '也可以从一个例子开始',
  },
  de: {
    routeEyebrow: 'Neue Anforderung',
    routeTitle: 'Geschaeftsroute waehlen',
    routeDescription: 'Damit wird nur der passende Expertenkontext gewaehlt. Keine Anforderung wird vorbefuellt oder bestaetigt.',
    eyebrow: 'Ein Satz genuegt',
    title: 'Was moechtest du verbessern?',
    description: 'Beschreibe Nutzer, Arbeit oder Problem. AI PM strukturiert den Rest und fragt nur bei fehlenden Nachweisen nach.',
    starters: 'Oder mit einem Beispiel beginnen',
  },
  ms: {
    routeEyebrow: 'Requirement baharu',
    routeTitle: 'Pilih laluan perniagaan',
    routeDescription: 'Ini hanya memilih konteks pakar yang betul. Tiada requirement diisi atau disahkan secara automatik.',
    eyebrow: 'Mulakan dengan satu ayat',
    title: 'Apa yang anda mahu perbaiki?',
    description: 'Terangkan pengguna, kerja atau masalah. AI PM akan melengkapkan selebihnya dan hanya bertanya apabila bukti masih kurang.',
    starters: 'Atau mulakan dengan contoh',
  },
} satisfies Record<LanguageCode, Record<string, string>>

const copy = computed(() => copyByLanguage[props.language] ?? copyByLanguage.en)
const visibleStarters = computed(() => props.starters.slice(0, 3))
const selectedRouteLabel = computed(
  () => props.routes.find((route) => route.id === props.selectedRoute)?.label || props.selectedRoute.toUpperCase(),
)
</script>

<template>
  <section class="empty-session-landing">
    <div class="empty-session-copy">
      <span v-if="selectedRoute">{{ selectedRouteLabel }} · {{ copy.eyebrow }}</span>
      <span v-else>{{ copy.routeEyebrow }}</span>
      <h1>{{ selectedRoute ? copy.title : copy.routeTitle }}</h1>
      <p>{{ selectedRoute ? copy.description : copy.routeDescription }}</p>
    </div>

    <div v-if="!selectedRoute" class="empty-session-routes" aria-live="polite">
      <button
        v-for="route in routes"
        :key="route.id"
        type="button"
        :disabled="busy"
        @click="emit('selectRoute', route.id)"
      >
        <span class="route-marker" aria-hidden="true"></span>
        <span class="route-copy">
          <strong>{{ route.label }}</strong>
          <small>{{ route.text }}</small>
        </span>
        <span class="route-arrow" aria-hidden="true">→</span>
      </button>
    </div>

    <div v-if="selectedRoute && visibleStarters.length" class="empty-session-starters">
      <p>{{ copy.starters }}</p>
      <div class="empty-session-starter-list">
        <button
          v-for="starter in visibleStarters"
          :key="starter.id"
          type="button"
          :disabled="busy"
          @click="emit('selectStarter', starter.text)"
        >
          <strong>{{ starter.label }}</strong>
          <span>{{ starter.text }}</span>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.empty-session-landing {
  width: min(100%, 760px);
  display: grid;
  gap: 22px;
  color: var(--ink);
}

.empty-session-copy {
  display: grid;
  gap: 9px;
  text-align: center;
}

.empty-session-copy > span {
  color: var(--accent-strong);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.empty-session-copy h1 {
  margin: 0;
  font-size: clamp(1.9rem, 3.4vw, 2.7rem);
  line-height: 1.08;
  letter-spacing: -0.035em;
}

.empty-session-copy p {
  max-width: 620px;
  margin: 0 auto;
  color: var(--muted);
  font-size: 0.96rem;
  line-height: 1.6;
}

.empty-session-routes {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.empty-session-routes button {
  min-width: 0;
  min-height: 74px;
  display: grid;
  grid-template-columns: 4px minmax(0, 1fr) auto;
  align-items: center;
  gap: 11px;
  padding: 13px 13px 13px 10px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--panel) 94%, transparent);
  color: var(--ink);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
}

.empty-session-routes button:hover:not(:disabled),
.empty-session-routes button:focus-visible {
  border-color: color-mix(in srgb, var(--accent) 48%, var(--line));
  box-shadow: 0 10px 24px rgba(31, 80, 145, 0.1);
  transform: translateY(-1px);
}

.empty-session-routes button:focus-visible,
.empty-session-starter-list button:focus-visible {
  outline: 3px solid color-mix(in srgb, var(--accent) 24%, transparent);
  outline-offset: 2px;
}

.empty-session-routes button:disabled,
.empty-session-starter-list button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.route-marker {
  width: 4px;
  height: 34px;
  border-radius: 999px;
  background: var(--accent);
}

.route-copy {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.route-copy strong {
  font-size: 0.9rem;
  line-height: 1.2;
}

.route-copy small {
  display: -webkit-box;
  overflow: hidden;
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.35;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.route-arrow {
  color: var(--accent-strong);
  font-size: 1rem;
  font-weight: 800;
}

.empty-session-starters {
  display: grid;
  gap: 10px;
}

.empty-session-starters > p {
  margin: 0;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-align: center;
}

.empty-session-starter-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.empty-session-starter-list button {
  min-width: 0;
  min-height: 76px;
  display: grid;
  align-content: start;
  gap: 5px;
  padding: 13px 14px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--panel) 90%, transparent);
  color: var(--ink);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    transform 160ms ease;
}

.empty-session-starter-list button:hover:not(:disabled),
.empty-session-starter-list button:focus-visible {
  border-color: color-mix(in srgb, var(--accent) 45%, var(--line));
  box-shadow: 0 10px 24px rgba(31, 80, 145, 0.1);
  transform: translateY(-1px);
}

.empty-session-starter-list strong {
  color: var(--accent-strong);
  font-size: 0.85rem;
  line-height: 1.25;
}

.empty-session-starter-list span {
  display: -webkit-box;
  overflow: hidden;
  color: var(--muted);
  font-size: 0.76rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

@media (max-width: 720px) {
  .empty-session-landing {
    gap: 18px;
  }

  .empty-session-copy {
    text-align: left;
  }

  .empty-session-copy h1 {
    font-size: clamp(1.75rem, 8.5vw, 2.35rem);
  }

  .empty-session-copy p,
  .empty-session-starters > p {
    margin: 0;
    text-align: left;
  }

  .empty-session-routes,
  .empty-session-starter-list {
    grid-template-columns: 1fr;
  }

  .empty-session-routes button,
  .empty-session-starter-list button {
    min-height: 62px;
  }
}
</style>
