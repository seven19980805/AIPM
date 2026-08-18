import type {
  LanguageCode,
  SessionDetail,
  SessionLaunchContext,
  SessionLaunchMode,
  SessionLaunchSource,
  SessionLaunchStage,
  SessionLaunchStatus,
  SessionLaunchSuggestion,
} from '../../types/session'


const fallbackCopy = {
  en: {
    title: 'Start with the business decision',
    description: 'Describe the action to improve. AI PM will turn it into a focused interview and a build-ready requirement.',
    templateDescription: 'This template is active and will guide the interview without treating its content as confirmed.',
    draftDescription: 'The draft is the starting evidence. AI PM will ask only about blocking gaps or conflicts.',
    question: 'What business action should improve, who owns it, and what evidence proves success?',
    suggestions: [
      ['Business outcome', 'The first release should improve [business action] for [primary user], measured by [success evidence].'],
      ['Connected data', 'The source of truth is [SQL Server or SAP], with [table/report] as the business reference.'],
      ['Manual upload', 'Users may upload [Excel/CSV] when connected data is unavailable; validation and owner are [details].'],
    ],
  },
  zh: {
    title: '先说清要改善的业务动作',
    description: '描述首版要改善的动作，AI PM 会把它拆成聚焦采访，并逐步形成可交付需求。',
    templateDescription: '模板已启用；它只负责引导采访，在你确认之前不会被当成真实需求。',
    draftDescription: '草稿是起始证据；AI PM 只追问阻断交付的缺口或冲突。',
    question: '首版要改善什么业务动作、由谁负责、用什么证据证明成功？',
    suggestions: [
      ['业务结果', '首版要为[主要用户]改善[业务动作]，并用[成功证据]衡量。'],
      ['连接数据', 'source of truth 是[SQL Server 或 SAP]，业务口径来自[表/报表]。'],
      ['人工上传', '连接数据不可用时，用户可以上传[Excel/CSV]；校验规则和 owner 是[说明]。'],
    ],
  },
  de: {
    title: 'Mit der Geschaeftsentscheidung beginnen',
    description: 'Beschreibe die Aktion. AI PM macht daraus ein fokussiertes Interview und eine umsetzbare Anforderung.',
    templateDescription: 'Die Vorlage ist aktiv und fuehrt das Interview, ohne Inhalte vorab als bestaetigt zu behandeln.',
    draftDescription: 'Der Draft ist die Ausgangsbasis. AI PM fragt nur nach blockierenden Luecken oder Konflikten.',
    question: 'Welche Geschaeftsaktion soll besser werden, wer verantwortet sie und welcher Nachweis belegt den Erfolg?',
    suggestions: [
      ['Geschaeftsergebnis', 'Das erste Release verbessert [Aktion] fuer [Hauptnutzer], gemessen durch [Nachweis].'],
      ['Verbundene Daten', 'Source of Truth ist [SQL Server oder SAP], fachliche Referenz ist [Tabelle/Report].'],
      ['Manueller Upload', 'Falls verbundene Daten fehlen, kann [Excel/CSV] hochgeladen werden; Validierung und Owner sind [Details].'],
    ],
  },
  ms: {
    title: 'Mulakan dengan keputusan perniagaan',
    description: 'Terangkan tindakan yang perlu diperbaiki. AI PM akan membentuk temu bual fokus dan requirement sedia bina.',
    templateDescription: 'Templat aktif dan membimbing temu bual tanpa menganggap kandungannya sudah disahkan.',
    draftDescription: 'Draft ialah bukti permulaan. AI PM hanya bertanya gap atau konflik yang menghalang delivery.',
    question: 'Tindakan perniagaan apa perlu diperbaiki, siapa owner, dan bukti apa mengesahkan kejayaan?',
    suggestions: [
      ['Hasil perniagaan', 'Release pertama memperbaiki [tindakan] untuk [pengguna], diukur dengan [bukti].'],
      ['Data bersambung', 'Source of truth ialah [SQL Server atau SAP], dengan [jadual/laporan] sebagai rujukan.'],
      ['Muat naik manual', 'Jika data sambungan tiada, pengguna boleh muat naik [Excel/CSV]; validasi dan owner ialah [butiran].'],
    ],
  },
} satisfies Record<LanguageCode, {
  title: string
  description: string
  templateDescription: string
  draftDescription: string
  question: string
  suggestions: string[][]
}>


export function extractSessionLaunchContext(
  session: SessionDetail,
  language: LanguageCode,
): SessionLaunchContext {
  const copy = fallbackCopy[language] ?? fallbackCopy.en
  const rawContext = asRecord(session.launch_context)
  const chain = session.conversation_chain_state
  const fallbackMode: SessionLaunchMode = session.intake_mode
    || (session.applied_template_id
    ? 'template'
    : session.start_function === 'improve_draft'
      ? 'draft'
      : 'scratch')
  const mode = normalizeMode(rawContext?.mode, fallbackMode)
  const status = normalizeStatus(
    rawContext?.status,
    chain?.status,
    session.messages.length > 0 ? 'in_progress' : 'not_started',
  )
  const title = text(rawContext?.title)
    || (mode === 'template' ? session.applied_template_name : '')
    || session.title
    || copy.title
  const description = text(rawContext?.description)
    || (mode === 'template'
      ? copy.templateDescription
      : mode === 'draft'
        ? copy.draftDescription
        : copy.description)
  const question = text(rawContext?.question)
    || chain?.current_node_label?.trim()
    || copy.question

  return {
    version: 2,
    mode,
    business_route: text(rawContext?.business_route) || session.business_route || '',
    status,
    title,
    description,
    question,
    stages: normalizeStages(rawContext?.stages, chain?.nodes),
    suggestions: normalizeSuggestions(rawContext?.suggestions, copy.suggestions),
    question_budget: normalizeQuestionBudget(rawContext?.question_budget, session.messages),
    source: normalizeSource(rawContext?.source, session, language, mode),
  }
}

export function shouldResetSessionWorkspace(
  currentSessionId: string,
  nextSessionId: string,
): boolean {
  return !currentSessionId || currentSessionId !== nextSessionId
}


function normalizeMode(value: unknown, fallback: SessionLaunchMode): SessionLaunchMode {
  if (value === 'template' || value === 'draft' || value === 'scratch') {
    return value
  }
  if (value === 'conversation' || value === 'department') {
    return fallback === 'draft' ? 'draft' : 'scratch'
  }
  return fallback
}


function normalizeStatus(
  ...values: unknown[]
): SessionLaunchStatus {
  for (const value of values) {
    if (value === 'not_started' || value === 'in_progress' || value === 'complete') {
      return value
    }
  }
  return 'not_started'
}


function normalizeStages(
  value: unknown,
  fallback: SessionDetail['conversation_chain_state'] extends infer _State
    ? NonNullable<SessionDetail['conversation_chain_state']>['nodes']
    : never,
): SessionLaunchStage[] {
  const candidates = Array.isArray(value) ? value : fallback ?? []
  return candidates.flatMap((candidate) => {
    const item = asRecord(candidate)
    const key = text(item?.key) || text(item?.node)
    const label = text(item?.label)
    if (!key || !label) {
      return []
    }
    const rawStatus = text(item?.status)
    const status: SessionLaunchStage['status'] = (
      rawStatus === 'current' || rawStatus === 'complete' || rawStatus === 'pending'
    )
      ? rawStatus
      : 'pending'
    return [{
      key,
      track: text(item?.track),
      label,
      status,
    }]
  })
}


function normalizeSuggestions(
  value: unknown,
  fallback: string[][],
): SessionLaunchSuggestion[] {
  const normalized = Array.isArray(value)
    ? value.flatMap((candidate) => {
      const item = asRecord(candidate)
      const id = text(item?.id)
      const label = text(item?.label)
      const suggestionText = text(item?.text)
      return id && label && suggestionText
        ? [{ id, label, text: suggestionText }]
        : []
    })
    : []

  if (normalized.length > 0) {
    return normalized
  }
  return fallback.map(([label = '', suggestionText = ''], index) => ({
    id: `starter-${index + 1}`,
    label,
    text: suggestionText,
  }))
}


function normalizeSource(
  value: unknown,
  session: SessionDetail,
  language: LanguageCode,
  mode: SessionLaunchMode,
): SessionLaunchSource {
  const item = asRecord(value)
  const rawType = text(item?.type)
  const sourceType: SessionLaunchSource['type'] = (
    rawType === 'template' || rawType === 'draft' || rawType === 'scratch'
  )
    ? rawType
    : mode

  return {
    type: sourceType,
    id: text(item?.id) || session.applied_template_id,
    name: text(item?.name) || session.applied_template_name,
    version: text(item?.version),
    language: text(item?.language) || language,
    start_function: text(item?.start_function) || session.start_function || 'from_scratch',
    business_route: text(item?.business_route) || session.business_route || '',
  }
}


function normalizeQuestionBudget(
  value: unknown,
  messages: SessionDetail['messages'],
): SessionLaunchContext['question_budget'] {
  const item = asRecord(value)
  const askedFallback = messages.filter((message) => message.role === 'user').length
  const target = positiveInteger(item?.target, 5)
  const maximum = positiveInteger(item?.maximum, 7)
  const asked = Math.max(0, integer(item?.asked, askedFallback))
  return {
    target,
    maximum,
    asked,
    remaining: Math.max(0, integer(item?.remaining, maximum - asked)),
  }
}


function positiveInteger(value: unknown, fallback: number): number {
  const parsed = integer(value, fallback)
  return parsed > 0 ? parsed : fallback
}


function integer(value: unknown, fallback: number): number {
  return typeof value === 'number' && Number.isFinite(value)
    ? Math.trunc(value)
    : fallback
}


function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null
}


function text(value: unknown): string {
  return typeof value === 'string' ? value.trim() : ''
}
