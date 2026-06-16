<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'

import type { BusinessTemplateDetail, BusinessTemplateSummary } from './types/businessTemplate'
import MarkdownRenderer from './components/MarkdownRenderer.vue'
import RequirementMarkdownPreview from './components/RequirementMarkdownPreview.vue'
import StructuredRequirementPanel from './components/StructuredRequirementPanel.vue'
import { computeStructuredRequirementProgress } from './lib/structuredRequirementProgress'
import type {
  ChatMessage,
  ChatMessagePayload,
  CodingHandoffCreateResponse,
  GeneratedDocumentResponse,
  LanguageCode,
  MessageResponse,
  PromptTemplate,
  SessionDetail,
  SessionSummary,
} from './types/session'
import {
  createEmptyConversationChainState,
  createEmptyStructuredRequirementModel,
  extractConversationChainState,
  extractStructuredRequirementModel,
  hasStructuredRequirementContent,
  type ConversationChainState,
  type StructuredRequirementModel,
  type StructuredRequirementResponse,
} from './types/structuredRequirement'

type AttachmentExtractionResponse = {
  filename: string
  size: number
  kind: string
  text: string
  truncated: boolean
  multimodal?: boolean
  visual_count?: number
}

type PendingAttachment = {
  filename: string
  kind: string
  size: number
  context: string
  multimodal: boolean
  visualCount: number
}

const sessionId = ref('')
const sessions = ref<SessionSummary[]>([])
const businessTemplates = ref<BusinessTemplateSummary[]>([])
const businessTemplateDetails = ref<Record<string, BusinessTemplateDetail>>({})
const sessionPromptTemplate = ref<PromptTemplate>('personal_project')
const inputText = ref('')
const pendingAttachment = ref<PendingAttachment | null>(null)
const messages = ref<ChatMessage[]>([])
const chatList = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const attachmentInputRef = ref<HTMLInputElement | null>(null)
const languageMenuRef = ref<HTMLDetailsElement | null>(null)

const SESSION_TITLE_MAX_CHARS = 10
const SESSION_TITLE_MAX_ENGLISH_WORDS = 5
const SESSION_TITLE_ELLIPSIS = '...'
const SESSION_TITLE_CJK_PATTERN = /[\u3400-\u9fff]/
const SESSION_TITLE_LATIN_PATTERN = /[A-Za-z]/

const loadingSession = ref(false)
const loadingHistory = ref(false)
const loadingTemplates = ref(false)
const switchingSession = ref(false)
const deletingSessionId = ref('')
const applyingTemplateId = ref('')
const generatingDocuments = ref(false)
const openingGoCoding = ref(false)
const uploadingAttachment = ref(false)
const globalError = ref('')
const loadingStructuredRequirement = ref(false)
const structuredRequirementError = ref('')
const structuredRequirementModel = ref<StructuredRequirementModel>(createEmptyStructuredRequirementModel())
const conversationChainState = ref<ConversationChainState>(createEmptyConversationChainState())
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const GO_CODING_URL = resolveExternalUrl(import.meta.env.VITE_GO_CODING_URL, 'http://localhost:8888')
let structuredRequirementRequestToken = 0
const activeReplyCount = ref(0)
const activeMessagePipelineCount = ref(0)
const activeStructuredRequirementSyncCount = ref(0)
const templateDialogOpen = ref(false)
const loadingTemplateDetail = ref(false)
const templateDialogError = ref('')
const selectedBusinessTemplateId = ref('')
const previewPanelOpen = ref(false)
const documentGenerationConfirmOpen = ref(false)
const documentGenerationConfirmMessage = ref('')
const deleteSessionConfirmOpen = ref(false)
const deleteSessionConfirmTargetId = ref('')
const currentWorkspaceView = ref<'chat' | 'templates'>('chat')
const newChatChooserOpen = ref(false)


// 鐟滅増娲熼悡鍫曟儎缁嬪灝褰犻柛娆愶耿閸?
const recording = ref(false)
const audioBuffer = ref<Float32Array[]>([])
const audioContext = ref<AudioContext | null>(null)
const scriptProcessor = ref<ScriptProcessorNode | null>(null)

const hasSession = computed(() => Boolean(sessionId.value))
const currentLanguage = ref<LanguageCode>('en')
const sidebarCollapsed = ref(false)
const sending = computed(() => activeReplyCount.value > 0)
const messagePipelineActive = computed(() => activeMessagePipelineCount.value > 0)
const syncingStructuredRequirement = computed(() => activeStructuredRequirementSyncCount.value > 0)
const canSendComposerMessage = computed(() =>
  Boolean(inputText.value.trim() || pendingAttachment.value) &&
  !sending.value &&
  !generatingDocuments.value &&
  !switchingSession.value,
)
const structuredRequirementProgress = computed(() =>
  computeStructuredRequirementProgress(structuredRequirementModel.value),
)

const translations = {
  en: {
    title: 'AI PM',
    subtitle: 'From requirement interview to build spec',
    languageSection: 'Language',
    conversation: 'Conversation',
    history: 'History',
    historyLoading: 'Loading history...',
    historyEmpty: 'No conversation history yet',
    untitledChat: 'New Chat',
    newChat: 'New Chat',
    generatePrd: 'Generate Documents',
    generatingPrd: 'Generating documents...',
    sending: 'Sending...',
    send: 'Send',
    recording: 'Recording',
    stopRecording: 'Stop Recording',
    startRecording: 'Start Recording',
    attachFile: 'Attach file',
    uploadingAttachment: 'Reading attachment...',
    attachmentReady: 'Attachment ready',
    attachmentVisuals: 'visual items',
    removeAttachment: 'Remove attachment',
    attachmentOnlyPrompt: 'Please use the attached file to continue requirement discovery.',
    loading: 'Loading...',
    creating: 'Creating...',
    startConversation: 'Start a conversation',
    startConversationDesc: 'Describe your project requirements and AI PM will help you collect and refine them.',
    describeRequirements: 'Describe your requirements...',
    error: 'Error',
    failedToSend: 'Failed to send message',
    failedToCreate: 'Failed to create session',
    failedToLoadHistory: 'Failed to load conversation history',
    failedToLoadSession: 'Failed to load session',
    failedToGenerate: 'Failed to generate documents',
    microphoneAccessError: 'Unable to access microphone',
    speechRecognitionError: 'Speech recognition failed',
    attachmentUploadError: 'Failed to read attachment',
    prdDocLabel: 'Requirements Doc',
    designDocLabel: 'Design Doc',
    downloadMarkdown: 'Download DOCX',
    streamingError: 'Streaming response error',
    browserNotSupport: 'Browser does not support streaming responses',
    requestFailed: 'Request failed',
    close: 'Close',
    viewReasoning: 'View reasoning',
    you: 'You',
    pmAssistant: 'AI PM',
    justNow: 'Just now',
    messagesLabel: 'messages',
    sessionsLabel: 'sessions',
    templatesLabel: 'templates',
    failedToDeleteSession: 'Failed to delete session',
    delete: 'Delete',
    deleteSession: 'Delete session',
    deleteSessionConfirm: 'Delete this conversation?',
    templateLabel: 'Session Template',
    templateLockedHint: 'Locked after first user message',
    personalProjectTemplate: 'Quick',
    standardTemplate: 'Expert',
    expandSidebar: 'Expand sidebar',
    collapseSidebar: 'Collapse sidebar',
    historyExpand: 'Expand history',
    historyCollapse: 'Collapse history',
    templateLibraryExpand: 'Expand template library',
    templateLibraryCollapse: 'Collapse template library',
    templateLibrary: 'Template Library',
    templateLibraryLoading: 'Loading templates...',
    templateLibraryEmpty: 'No templates available yet',
    templateLibraryHint: 'Choose a business template to start a structured session faster.',
    templateOpen: 'View details',
    templateApply: 'Use this template',
    templateApplyGuided: 'Guided start',
    templateApplyExample: 'Start from example',
    templateCancel: 'Cancel',
    templateDetail: 'Template Details',
    templateScenarios: 'Applicable scenarios',
    templateSections: 'Template sections',
    templateSectionsShort: 'sections',
    templateTags: 'Tags',
    templateFieldCount: 'fields',
    templateApplyHint: 'Use guided start to collect requirements section by section, or start from the example and revise it.',
    templatePromptManagedHint: 'A business template is active. Generic quick/expert prompting is disabled for this session.',
    templateSessionBadge: 'Template session',
    failedToLoadTemplates: 'Failed to load template library',
    failedToOpenGoCoding: 'Failed to open coding workspace',
    newChatStartTitle: 'Start new chat',
    newChatStartSubtitle: 'Choose the right discovery path before the first message.',
    newChatGeneralTitle: 'General requirement',
    newChatGeneralDesc: 'Use the normal Quick/Expert interview for non-manufacturing apps.',
    newChatIcSubstrateTitle: 'IC Substrate professional chain',
    newChatIcSubstrateDesc: 'Use peer department-first questioning for IC Substrate business owners.',
    newChatChooseDepartment: 'Choose a starting department',
    newChatTemplateLibrary: 'Browse template library',
  },
  de: {
    title: 'AI PM',
    subtitle: 'Vom Anforderungsdialog zur Entwicklungsspezifikation',
    languageSection: 'Sprache',
    conversation: 'Konversation',
    history: 'Verlauf',
    historyLoading: 'Verlauf wird geladen...',
    historyEmpty: 'Noch kein Verlauf vorhanden',
    untitledChat: 'Neuer Chat',
    newChat: 'Neuer Chat',
    generatePrd: 'Dokumente erzeugen',
    generatingPrd: 'Dokumente werden erzeugt...',
    sending: 'Wird gesendet...',
    send: 'Senden',
    recording: 'Aufnahme',
    stopRecording: 'Aufnahme stoppen',
    startRecording: 'Aufnahme starten',
    attachFile: 'Datei anhaengen',
    uploadingAttachment: 'Anhang wird gelesen...',
    attachmentReady: 'Anhang bereit',
    attachmentVisuals: 'visuelle Elemente',
    removeAttachment: 'Anhang entfernen',
    attachmentOnlyPrompt: 'Bitte nutze die angehaengte Datei, um die Anforderung weiter zu klaeren.',
    loading: 'Laedt...',
    creating: 'Wird erstellt...',
    startConversation: 'Konversation starten',
    startConversationDesc: 'Beschreibe deine Projektanforderungen, und AI PM hilft beim Sammeln und Strukturieren.',
    describeRequirements: 'Beschreibe deine Anforderungen...',
    error: 'Fehler',
    failedToSend: 'Senden der Nachricht fehlgeschlagen',
    failedToCreate: 'Chat konnte nicht erstellt werden',
    failedToLoadHistory: 'Verlauf konnte nicht geladen werden',
    failedToLoadSession: 'Chat konnte nicht geladen werden',
    failedToGenerate: 'Dokumente konnten nicht erstellt werden',
    microphoneAccessError: 'Kein Zugriff auf das Mikrofon',
    speechRecognitionError: 'Spracherkennung fehlgeschlagen',
    attachmentUploadError: 'Anhang konnte nicht gelesen werden',
    prdDocLabel: 'Anforderungsdokument',
    designDocLabel: 'Design-Dokument',
    downloadMarkdown: 'DOCX herunterladen',
    streamingError: 'Fehler bei der Streaming-Antwort',
    browserNotSupport: 'Der Browser unterstuetzt keine Streaming-Antworten',
    requestFailed: 'Anfrage fehlgeschlagen',
    close: 'Schliessen',
    viewReasoning: 'Denkprozess anzeigen',
    you: 'Du',
    pmAssistant: 'AI PM',
    justNow: 'Gerade eben',
    messagesLabel: 'Nachrichten',
    sessionsLabel: 'Chats',
    templatesLabel: 'Vorlagen',
    failedToDeleteSession: 'Chat konnte nicht geloescht werden',
    delete: 'Loeschen',
    deleteSession: 'Chat loeschen',
    deleteSessionConfirm: 'Diesen Chat wirklich loeschen?',
    templateLabel: 'Sitzungsvorlage',
    templateLockedHint: 'Nach der ersten Nutzernachricht gesperrt',
    personalProjectTemplate: 'Schnell',
    standardTemplate: 'Experte',
    expandSidebar: 'Seitenleiste ausklappen',
    collapseSidebar: 'Seitenleiste einklappen',
    historyExpand: 'Verlauf ausklappen',
    historyCollapse: 'Verlauf einklappen',
    templateLibraryExpand: 'Vorlagenbibliothek ausklappen',
    templateLibraryCollapse: 'Vorlagenbibliothek einklappen',
    templateLibrary: 'Vorlagenbibliothek',
    templateLibraryLoading: 'Vorlagen werden geladen...',
    templateLibraryEmpty: 'Noch keine Vorlagen verfuegbar',
    templateLibraryHint: 'Waehle eine Fachvorlage, um schneller in eine strukturierte Sitzung zu starten.',
    templateOpen: 'Details ansehen',
    templateApply: 'Vorlage verwenden',
    templateApplyGuided: 'Gefuehrt starten',
    templateApplyExample: 'Mit Beispiel starten',
    templateCancel: 'Abbrechen',
    templateDetail: 'Vorlagendetails',
    templateScenarios: 'Geeignete Szenarien',
    templateSections: 'Vorlagenabschnitte',
    templateSectionsShort: 'Abschnitte',
    templateTags: 'Tags',
    templateFieldCount: 'Felder',
    templateApplyHint: 'Gefuehrt starten sammelt Anforderungen Abschnitt fuer Abschnitt; mit Beispiel starten erzeugt eine vorbefuellte Sitzung.',
    templatePromptManagedHint: 'Diese Sitzung wird von einer Fachvorlage gesteuert. Die generischen Schnell/Experte-Prompts sind deaktiviert.',
    templateSessionBadge: 'Vorlagen-Sitzung',
    failedToLoadTemplates: 'Vorlagenbibliothek konnte nicht geladen werden',
    failedToOpenGoCoding: 'Coding-Workspace konnte nicht geoeffnet werden',
    newChatStartTitle: 'Neuen Chat starten',
    newChatStartSubtitle: 'Waehle vor der ersten Nachricht den passenden Erfassungsweg.',
    newChatGeneralTitle: 'Allgemeine Anforderung',
    newChatGeneralDesc: 'Normaler Schnell/Experten-Dialog fuer Apps ausserhalb der Fertigung.',
    newChatIcSubstrateTitle: 'IC-Substrate Fachkette',
    newChatIcSubstrateDesc: 'Gleichrangige abteilungsorientierte Fragen fuer IC-Substrate Business Owner.',
    newChatChooseDepartment: 'Startabteilung waehlen',
    newChatTemplateLibrary: 'Vorlagenbibliothek anzeigen',
  },
  zh: {
    title: 'AI PM',
    subtitle: '需求访谈到开发规格',
    languageSection: '语言',
    conversation: '对话',
    history: '历史会话',
    historyLoading: '加载历史中...',
    historyEmpty: '还没有历史会话',
    untitledChat: '新建对话',
    newChat: '新建对话',
    generatePrd: '生成文档',
    generatingPrd: '正在生成文档...',
    sending: '发送中...',
    send: '发送',
    recording: '录音中',
    stopRecording: '停止录音',
    startRecording: '开始录音',
    attachFile: '上传附件',
    uploadingAttachment: '正在读取附件...',
    attachmentReady: '附件已就绪',
    attachmentVisuals: '个图表/图片',
    removeAttachment: '移除附件',
    attachmentOnlyPrompt: '请结合附件继续梳理需求。',
    loading: '加载中...',
    creating: '创建中...',
    startConversation: '开始对话',
    startConversationDesc: '描述您的项目需求，AI PM 会帮助您收集并整理成开发规格。',
    describeRequirements: '描述您的需求...',
    error: '错误',
    failedToSend: '发送失败',
    failedToCreate: '创建对话失败',
    failedToLoadHistory: '加载历史会话失败',
    failedToLoadSession: '加载会话失败',
    failedToGenerate: '生成文档失败',
    microphoneAccessError: '无法访问麦克风',
    speechRecognitionError: '语音识别失败',
    attachmentUploadError: '附件读取失败',
    prdDocLabel: '需求文档',
    designDocLabel: '设计文档',
    downloadMarkdown: '下载 DOCX',
    streamingError: '流式响应错误',
    browserNotSupport: '浏览器不支持流式响应',
    requestFailed: '请求失败',
    close: '关闭',
    viewReasoning: '查看思考过程',
    you: '你',
    pmAssistant: 'AI PM',
    justNow: '刚刚',
    messagesLabel: '条消息',
    sessionsLabel: '个会话',
    templatesLabel: '个模板',
    failedToDeleteSession: '删除会话失败',
    delete: '删除',
    deleteSession: '删除会话',
    deleteSessionConfirm: '确认删除这条历史会话吗？',
    templateLabel: '会话模板',
    templateLockedHint: '首条用户消息后锁定',
    personalProjectTemplate: '快速',
    standardTemplate: '专家',
    expandSidebar: '展开侧边栏',
    collapseSidebar: '收起侧边栏',
    historyExpand: '展开历史会话',
    historyCollapse: '收起历史会话',
    templateLibraryExpand: '展开模板库',
    templateLibraryCollapse: '收起模板库',
    templateLibrary: '模板库',
    templateLibraryLoading: '模板加载中...',
    templateLibraryEmpty: '还没有可用模板',
    templateLibraryHint: '选择一个业务模板，更快开始结构化需求会话。',
    templateOpen: '查看详情',
    templateApply: '使用该模板',
    templateApplyGuided: '引导式开始',
    templateApplyExample: '填充式开始',
    templateCancel: '取消',
    templateDetail: '模板详情',
    templateScenarios: '适用场景',
    templateSections: '模板章节',
    templateSectionsShort: '章节',
    templateTags: '标签',
    templateFieldCount: '个字段',
    templateApplyHint: '可以引导式逐步采集，也可以基于示例业务先生成再修改。',
    templatePromptManagedHint: '当前会话已启用业务模板，通用的“快速/专家”提问策略已停用。',
    templateSessionBadge: '模板会话',
    failedToLoadTemplates: '加载模板库失败',
    failedToOpenGoCoding: '打开 Coding 工作区失败',
    newChatStartTitle: '开始新对话',
    newChatStartSubtitle: '在第一句话前先选对需求采集链路。',
    newChatGeneralTitle: '普通需求',
    newChatGeneralDesc: '适合非制造业务，用通用 Quick/Expert 访谈。',
    newChatIcSubstrateTitle: 'IC Substrate 专业链路',
    newChatIcSubstrateDesc: '适合 IC Substrate 各业务部门，所有部门平级，先按部门/owner 路由。',
    newChatChooseDepartment: '选择起始部门',
    newChatTemplateLibrary: '浏览模板库',
  },  ms: {
    title: 'AI PM',
    subtitle: 'Daripada temubual ke spesifikasi pembangunan',
    languageSection: 'Bahasa',
    conversation: 'Perbualan',
    history: 'Sejarah',
    historyLoading: 'Memuatkan sejarah...',
    historyEmpty: 'Belum ada sejarah perbualan',
    untitledChat: 'Sembang Baharu',
    newChat: 'Sembang Baharu',
    generatePrd: 'Jana Dokumen',
    generatingPrd: 'Sedang menjana dokumen...',
    sending: 'Menghantar...',
    send: 'Hantar',
    recording: 'Merakam',
    stopRecording: 'Henti Rakaman',
    startRecording: 'Mula Merakam',
    attachFile: 'Lampirkan fail',
    uploadingAttachment: 'Membaca lampiran...',
    attachmentReady: 'Lampiran sedia',
    attachmentVisuals: 'item visual',
    removeAttachment: 'Alih keluar lampiran',
    attachmentOnlyPrompt: 'Sila gunakan fail lampiran untuk meneruskan penemuan keperluan.',
    loading: 'Memuatkan...',
    creating: 'Mencipta...',
    startConversation: 'Mulakan perbualan',
    startConversationDesc: 'Terangkan keperluan projek anda, dan AI PM akan membantu mengumpul serta menyusunnya.',
    describeRequirements: 'Terangkan keperluan anda...',
    error: 'Ralat',
    failedToSend: 'Gagal menghantar mesej',
    failedToCreate: 'Gagal mencipta sesi',
    failedToLoadHistory: 'Gagal memuatkan sejarah perbualan',
    failedToLoadSession: 'Gagal memuatkan sesi',
    failedToGenerate: 'Gagal menjana dokumen',
    microphoneAccessError: 'Tidak dapat mengakses mikrofon',
    speechRecognitionError: 'Pengecaman suara gagal',
    attachmentUploadError: 'Gagal membaca lampiran',
    prdDocLabel: 'Dokumen Keperluan',
    designDocLabel: 'Dokumen Reka Bentuk',
    downloadMarkdown: 'Muat Turun DOCX',
    streamingError: 'Ralat respons penstriman',
    browserNotSupport: 'Pelayar tidak menyokong respons penstriman',
    requestFailed: 'Permintaan gagal',
    close: 'Tutup',
    viewReasoning: 'Lihat proses penaakulan',
    you: 'Anda',
    pmAssistant: 'AI PM',
    justNow: 'Baru sahaja',
    messagesLabel: 'mesej',
    sessionsLabel: 'sesi',
    templatesLabel: 'templat',
    failedToDeleteSession: 'Gagal memadam sesi',
    delete: 'Padam',
    deleteSession: 'Padam sesi',
    deleteSessionConfirm: 'Padam perbualan ini?',
    templateLabel: 'Templat Sesi',
    templateLockedHint: 'Dikunci selepas mesej pengguna pertama',
    personalProjectTemplate: 'Pantas',
    standardTemplate: 'Pakar',
    expandSidebar: 'Kembangkan bar sisi',
    collapseSidebar: 'Runtuhkan bar sisi',
    historyExpand: 'Kembangkan sejarah',
    historyCollapse: 'Runtuhkan sejarah',
    templateLibraryExpand: 'Kembangkan pustaka templat',
    templateLibraryCollapse: 'Runtuhkan pustaka templat',
    templateLibrary: 'Pustaka Templat',
    templateLibraryLoading: 'Memuatkan templat...',
    templateLibraryEmpty: 'Belum ada templat tersedia',
    templateLibraryHint: 'Pilih templat perniagaan untuk memulakan sesi berstruktur dengan lebih pantas.',
    templateOpen: 'Lihat butiran',
    templateApply: 'Guna templat ini',
    templateApplyGuided: 'Mula berpandu',
    templateApplyExample: 'Mula daripada contoh',
    templateCancel: 'Batal',
    templateDetail: 'Butiran Templat',
    templateScenarios: 'Senario sesuai',
    templateSections: 'Bahagian templat',
    templateSectionsShort: 'bahagian',
    templateTags: 'Tag',
    templateFieldCount: 'medan',
    templateApplyHint: 'Mula berpandu mengumpul keperluan langkah demi langkah; mula daripada contoh mencipta sesi yang telah diisi.',
    templatePromptManagedHint: 'Sesi ini dikawal oleh templat perniagaan. Mod prompt umum Pantas/Pakar dimatikan.',
    templateSessionBadge: 'Sesi templat',
    failedToLoadTemplates: 'Gagal memuatkan pustaka templat',
    failedToOpenGoCoding: 'Gagal membuka workspace coding',
    newChatStartTitle: 'Mulakan sembang baharu',
    newChatStartSubtitle: 'Pilih laluan penemuan yang sesuai sebelum mesej pertama.',
    newChatGeneralTitle: 'Keperluan umum',
    newChatGeneralDesc: 'Gunakan temubual Pantas/Pakar biasa untuk aplikasi bukan pembuatan.',
    newChatIcSubstrateTitle: 'Rantaian profesional IC Substrate',
    newChatIcSubstrateDesc: 'Soalan jabatan setara untuk business owner IC Substrate.',
    newChatChooseDepartment: 'Pilih jabatan mula',
    newChatTemplateLibrary: 'Lihat pustaka templat',
  },
} satisfies Record<LanguageCode, Record<string, string>>

const shellCopy = {
  en: {
    heroTag: 'AT&S requirement workspace',
    heroLead: 'Hello,',
    heroAccent: 'AI PM',
    heroQuestion: 'Tell me what you need and I will help you turn it into a complete requirement document.',
    assistantIntro: 'Hello, I am AIPM. You can ask directly, paste context, or choose a template to start.',
    composerPlaceholder: 'Ask AIPM anything',
    footerNotice: 'AIPM may make mistakes. Please verify important information.',
    footerBrand: 'BUME QDM | AI transformation club',
    recent: 'Recent',
    promptModes: 'Conversation strategy',
    currentConversation: 'Current conversation',
    currentConversationEmpty: 'The active session summary will appear here once the conversation starts.',
    activeSession: 'Active topic',
    messageCountLabel: 'Messages',
  },
  de: {
    heroTag: 'AT&S Anforderungs-Workspace',
    heroLead: 'Hallo,',
    heroAccent: 'AI PM',
    heroQuestion: 'Erzaehle mir deine Anforderungen und ich helfe dir, ein vollstaendiges Anforderungsdokument zu erstellen.',
    assistantIntro: 'Hallo, ich bin AIPM. Du kannst direkt fragen, Kontext einfuegen oder mit einer Vorlage starten.',
    composerPlaceholder: 'Stelle AIPM eine Frage',
    footerNotice: 'AIPM kann Fehler machen. Bitte pruefe wichtige Informationen.',
    footerBrand: 'BUME QDM | AI transformation club',
    recent: 'Neueste',
    promptModes: 'Dialogstrategie',
    currentConversation: 'Aktive Konversation',
    currentConversationEmpty: 'Sobald die Unterhaltung startet, erscheint hier eine Zusammenfassung der aktiven Sitzung.',
    activeSession: 'Aktives Thema',
    messageCountLabel: 'Nachrichten',
  },
  zh: {
    heroTag: 'AT&S 需求工作台',
    heroLead: '',
    heroAccent: '',
    heroQuestion: '',
    assistantIntro: '你好，我是 AIPM。你可以直接提问、粘贴上下文，或选择一个模板开始。',
    composerPlaceholder: '问AIPM任何问题',
    footerNotice: 'AIPM 可能会出错，请核对重要信息。',
    footerBrand: 'BUME QDM | AI transformation club',
    recent: '最近',
    promptModes: '提问策略',
    currentConversation: '当前会话',
    currentConversationEmpty: '系统将自动记录当前对话，并支持会话追溯。',
    activeSession: '当前主题',
    messageCountLabel: '消息数',
  },  ms: {
    heroTag: 'Ruang kerja keperluan AT&S',
    heroLead: 'Halo,',
    heroAccent: 'AI PM',
    heroQuestion: 'Beritahu keperluan anda dan saya akan bantu melengkapkan dokumen keperluan.',
    assistantIntro: 'Halo, saya AIPM. Anda boleh terus bertanya, tampal konteks, atau pilih templat untuk bermula.',
    composerPlaceholder: 'Tanya apa sahaja kepada AIPM',
    footerNotice: 'AIPM mungkin membuat kesilapan. Sila semak maklumat penting.',
    footerBrand: 'BUME QDM | AI transformation club',
    recent: 'Terkini',
    promptModes: 'Strategi perbualan',
    currentConversation: 'Perbualan semasa',
    currentConversationEmpty: 'Ringkasan sesi aktif akan muncul di sini sebaik sahaja perbualan bermula.',
    activeSession: 'Topik aktif',
    messageCountLabel: 'Mesej',
  },
} satisfies Record<
  LanguageCode,
  {
    heroTag: string
    heroLead: string
    heroAccent: string
    heroQuestion: string
    assistantIntro: string
    composerPlaceholder: string
    footerNotice: string
    footerBrand: string
    recent: string
    promptModes: string
    currentConversation: string
    currentConversationEmpty: string
    activeSession: string
    messageCountLabel: string
  }
>

const t = computed(() => translations[currentLanguage.value])
const shellText = computed(() => shellCopy[currentLanguage.value] ?? shellCopy.en)
const activeSessionSummary = computed(() => sessions.value.find((item) => item.session_id === sessionId.value) || null)
const activeSessionTitle = computed(() => sessionTitle(activeSessionSummary.value?.title || ''))
const activeBusinessTemplateName = computed(() => {
  const appliedTemplateId = activeSessionSummary.value?.applied_template_id || ''
  return (
    resolveLocalizedBusinessTemplateSummary(appliedTemplateId)?.template_name ||
    activeSessionSummary.value?.applied_template_name?.trim() ||
    ''
  )
})
const templateDrivenSession = computed(() => Boolean(activeSessionSummary.value?.applied_template_id))
const hasUserMessage = computed(() => messages.value.some((item) => item.role === 'user'))
const latestPrdDocument = computed(() => findLatestDocumentMessage('prd_doc'))
const latestDesignDocument = computed(() => findLatestDocumentMessage('design_doc'))
const selectedBusinessTemplate = computed<BusinessTemplateDetail | null>(() => {
  const templateId = selectedBusinessTemplateId.value
  if (!templateId) {
    return null
  }
  return businessTemplateDetails.value[templateId] ?? null
})
let documentGenerationConfirmResolver: ((confirmed: boolean) => void) | null = null
let deleteSessionConfirmResolver: ((confirmed: boolean) => void) | null = null
const languageOptions: Array<{ code: LanguageCode; label: string }> = [
  { code: 'en', label: 'English' },
  { code: 'de', label: 'Deutsch' },
  { code: 'zh', label: '中文' },
  { code: 'ms', label: 'Bahasa Melayu' },
]
const icSubstrateStartDepartments = [
  'Production',
  'Quality',
  'TDI',
]
const sidebarToggleAriaLabel = computed(() =>
  sidebarCollapsed.value ? t.value.expandSidebar : t.value.collapseSidebar,
)
const newChatActionDisabled = computed(
  () =>
    loadingSession.value ||
    sending.value ||
    generatingDocuments.value ||
    switchingSession.value ||
    Boolean(deletingSessionId.value) ||
    Boolean(applyingTemplateId.value),
)

const canChangePromptTemplate = computed(
  () =>
    hasSession.value &&
    !templateDrivenSession.value &&
    !hasUserMessage.value &&
    !messagePipelineActive.value &&
    !generatingDocuments.value &&
    !switchingSession.value &&
    !loadingSession.value,
)
const promptTemplateOptions = computed<{ value: PromptTemplate; label: string }[]>(() => [
  { value: 'personal_project', label: t.value.personalProjectTemplate },
  { value: 'standard', label: t.value.standardTemplate },
])
const currentLanguageLabel = computed(
  () => languageOptions.find((option) => option.code === currentLanguage.value)?.label || languageOptions[0].label,
)
const localizedBusinessTemplates = computed(() => {
  const byTemplateKey = new Map<string, BusinessTemplateSummary>()

  for (const templateItem of businessTemplates.value) {
    const groupingKey = templateItem.template_key || templateItem.template_id
    const currentItem = byTemplateKey.get(groupingKey)

    if (!currentItem) {
      byTemplateKey.set(groupingKey, templateItem)
      continue
    }

    const currentMatches = templateMatchesLanguage(currentItem, currentLanguage.value)
    const nextMatches = templateMatchesLanguage(templateItem, currentLanguage.value)
    if (nextMatches && !currentMatches) {
      byTemplateKey.set(groupingKey, templateItem)
    }
  }

  return Array.from(byTemplateKey.values())
})
const templateShelfItems = computed(() => localizedBusinessTemplates.value.slice(0, 6))
const recentSessions = computed(() => sessions.value.slice(0, 6))
const activeMessageCountLabel = computed(() => `${messages.value.length} ${t.value.messagesLabel}`)
const messageRenderSignature = computed(() =>
  messages.value
    .map((message, index) =>
      [
        index,
        message.role,
        message.kind || 'chat',
        message.content.length,
        message.thinking?.length ?? 0,
        message.downloadUrl ? 1 : 0,
      ].join(':'),
    )
    .join('|'),
)
const sessionCountLabel = computed(() => `${sessions.value.length} ${t.value.sessionsLabel}`)
const templateCountLabel = computed(() => `${localizedBusinessTemplates.value.length} ${t.value.templatesLabel}`)
const isChatView = computed(() => currentWorkspaceView.value === 'chat')
const isTemplateLibraryView = computed(() => currentWorkspaceView.value === 'templates')
const previewToggleLabel = computed(() => {
  if (currentLanguage.value === 'zh') {
    return previewPanelOpen.value ? '收起预览' : '预览文档'
  }
  if (currentLanguage.value === 'de') {
    return previewPanelOpen.value ? 'Vorschau schliessen' : 'Vorschau oeffnen'
  }
  if (currentLanguage.value === 'ms') {
    return previewPanelOpen.value ? 'Tutup pratonton' : 'Buka pratonton'
  }
  return previewPanelOpen.value ? 'Hide Preview' : 'Open Preview'
})
const conversationChainVisible = computed(() => Boolean(conversationChainState.value.enabled))
const conversationChainModeLabel = computed(() => {
  const mode = conversationChainState.value.mode || 'template'
  if (mode === 'ic_substrate') {
    return 'IC Substrate'
  }
  if (currentLanguage.value === 'zh') {
    return '模板链路'
  }
  if (currentLanguage.value === 'de') {
    return 'Vorlagenkette'
  }
  if (currentLanguage.value === 'ms') {
    return 'Rantaian templat'
  }
  return 'Template chain'
})
const conversationChainStatusLabel = computed(() => {
  const status = conversationChainState.value.status || ''
  if (currentLanguage.value === 'zh') {
    if (status === 'complete') return '已完成'
    if (status === 'in_progress') return '进行中'
    return '未开始'
  }
  if (currentLanguage.value === 'de') {
    if (status === 'complete') return 'Fertig'
    if (status === 'in_progress') return 'Aktiv'
    return 'Noch nicht gestartet'
  }
  if (currentLanguage.value === 'ms') {
    if (status === 'complete') return 'Selesai'
    if (status === 'in_progress') return 'Aktif'
    return 'Belum bermula'
  }
  if (status === 'complete') return 'Complete'
  if (status === 'in_progress') return 'In progress'
  return 'Not started'
})
const conversationChainProgressLabel = computed(() => {
  const current = conversationChainState.value.current_step_index || 0
  const total = conversationChainState.value.total_steps || 0
  if (!current || !total) {
    return ''
  }
  return `${current}/${total}`
})
const conversationChainNodeLabel = computed(() => {
  const track = conversationChainState.value.current_track || ''
  const node = conversationChainState.value.current_node_label || ''
  if (track && node) {
    return `${track} · ${node}`
  }
  return track || node
})
const previewDialogCopy = computed(() => {
  if (currentLanguage.value === 'zh') {
    return {
      eyebrow: '文档预览',
      title: '需求文档预览',
      description: '查看当前结构化需求生成的 PRD 与技术方案草稿。',
    }
  }
  if (currentLanguage.value === 'de') {
    return {
      eyebrow: 'Dokumentvorschau',
      title: 'Anforderungsvorschau',
      description: 'Sieh dir den aktuellen PRD-Entwurf und den technischen Entwurf aus dem strukturierten Anforderungsmodell an.',
    }
  }
  if (currentLanguage.value === 'ms') {
    return {
      eyebrow: 'Pratonton Dokumen',
      title: 'Pratonton Dokumen Keperluan',
      description: 'Lihat draf PRD dan draf teknikal yang dijana daripada model keperluan berstruktur semasa.',
    }
  }
  return {
    eyebrow: 'Document Preview',
    title: 'Requirement Document Preview',
    description: 'Review the current PRD draft and technical draft generated from the structured requirement model.',
  }
})
const templateFacetLabels: Record<string, Record<LanguageCode, string>> = {
  business_requirement: {
    en: 'Business Requirement',
    de: 'Business Requirement',
    zh: '业务需求',
    ms: 'Keperluan Perniagaan',
  },
  finance_management: {
    en: 'Finance Management',
    de: 'Finanzmanagement',
    zh: '财务管理',
    ms: 'Pengurusan Kewangan',
  },
  human_resource_management: {
    en: 'Human Resources',
    de: 'Personalmanagement',
    zh: '人力资源',
    ms: 'Sumber Manusia',
  },
  training_system: {
    en: 'Training System',
    de: 'Schulungssystem',
    zh: '培训系统',
    ms: 'Sistem Latihan',
  },
  forum_community: {
    en: 'Forum Community',
    de: 'Forum Community',
    zh: '论坛社区',
    ms: 'Komuniti Forum',
  },
  shopping_mall: {
    en: 'Shopping Mall',
    de: 'Online-Shop',
    zh: '购物商城',
    ms: 'Pusat Beli-belah',
  },
  logistics_warehouse: {
    en: 'Logistics & Warehouse',
    de: 'Logistik und Lager',
    zh: '物流仓储',
    ms: 'Logistik dan Gudang',
  },
  business_process: {
    en: 'Business Process',
    de: 'Geschaeftsprozess',
    zh: '业务流程',
    ms: 'Proses Perniagaan',
  },
  data_visualization: {
    en: 'Data Visualization',
    de: 'Datenvisualisierung',
    zh: '数据可视化',
    ms: 'Visualisasi Data',
  },
}
const templateTagLabels: Record<string, Record<LanguageCode, string>> = {
  finance: {
    en: 'Finance',
    de: 'Finanzen',
    zh: '财务',
    ms: 'Kewangan',
  },
  budget: {
    en: 'Budget',
    de: 'Budget',
    zh: '预算',
    ms: 'Bajet',
  },
  expense: {
    en: 'Expense',
    de: 'Ausgaben',
    zh: '费用',
    ms: 'Perbelanjaan',
  },
  payment: {
    en: 'Payment',
    de: 'Zahlung',
    zh: '付款',
    ms: 'Bayaran',
  },
  invoice: {
    en: 'Invoice',
    de: 'Rechnung',
    zh: '发票',
    ms: 'Invois',
  },
  reporting: {
    en: 'Reporting',
    de: 'Reporting',
    zh: '报表',
    ms: 'Pelaporan',
  },
  hr: {
    en: 'HR',
    de: 'HR',
    zh: '人力',
    ms: 'HR',
  },
  employee: {
    en: 'Employee',
    de: 'Mitarbeitende',
    zh: '员工',
    ms: 'Pekerja',
  },
  recruitment: {
    en: 'Recruitment',
    de: 'Recruiting',
    zh: '招聘',
    ms: 'Pengambilan',
  },
  attendance: {
    en: 'Attendance',
    de: 'Anwesenheit',
    zh: '考勤',
    ms: 'Kehadiran',
  },
  payroll: {
    en: 'Payroll',
    de: 'Payroll',
    zh: '薪酬',
    ms: 'Gaji',
  },
  performance: {
    en: 'Performance',
    de: 'Performance',
    zh: '绩效',
    ms: 'Prestasi',
  },
  training: {
    en: 'Training',
    de: 'Schulung',
    zh: '培训',
    ms: 'Latihan',
  },
  course: {
    en: 'Course',
    de: 'Kurs',
    zh: '课程',
    ms: 'Kursus',
  },
  learning: {
    en: 'Learning',
    de: 'Lernen',
    zh: '学习',
    ms: 'Pembelajaran',
  },
  exam: {
    en: 'Exam',
    de: 'Pruefung',
    zh: '考试',
    ms: 'Peperiksaan',
  },
  certificate: {
    en: 'Certificate',
    de: 'Zertifikat',
    zh: '证书',
    ms: 'Sijil',
  },
  enrollment: {
    en: 'Enrollment',
    de: 'Anmeldung',
    zh: '报名',
    ms: 'Pendaftaran',
  },
  forum: {
    en: 'Forum',
    de: 'Forum',
    zh: '论坛',
    ms: 'Forum',
  },
  community: {
    en: 'Community',
    de: 'Community',
    zh: '社区',
    ms: 'Komuniti',
  },
  thread: {
    en: 'Thread',
    de: 'Thread',
    zh: '主题帖',
    ms: 'Thread',
  },
  post: {
    en: 'Post',
    de: 'Beitrag',
    zh: '帖子',
    ms: 'Siaran',
  },
  comment: {
    en: 'Comment',
    de: 'Kommentar',
    zh: '评论',
    ms: 'Komen',
  },
  moderation: {
    en: 'Moderation',
    de: 'Moderation',
    zh: '审核',
    ms: 'Moderasi',
  },
  ecommerce: {
    en: 'E-commerce',
    de: 'E-Commerce',
    zh: '电商',
    ms: 'E-dagang',
  },
  product: {
    en: 'Product',
    de: 'Produkt',
    zh: '商品',
    ms: 'Produk',
  },
  order: {
    en: 'Order',
    de: 'Bestellung',
    zh: '订单',
    ms: 'Pesanan',
  },
  cart: {
    en: 'Cart',
    de: 'Warenkorb',
    zh: '购物车',
    ms: 'Troli',
  },
  promotion: {
    en: 'Promotion',
    de: 'Aktion',
    zh: '促销',
    ms: 'Promosi',
  },
  customer: {
    en: 'Customer',
    de: 'Kunde',
    zh: '客户',
    ms: 'Pelanggan',
  },
  logistics: {
    en: 'Logistics',
    de: 'Logistik',
    zh: '物流',
    ms: 'Logistik',
  },
  warehouse: {
    en: 'Warehouse',
    de: 'Lager',
    zh: '仓储',
    ms: 'Gudang',
  },
  inventory: {
    en: 'Inventory',
    de: 'Bestand',
    zh: '库存',
    ms: 'Inventori',
  },
  inbound: {
    en: 'Inbound',
    de: 'Inbound',
    zh: '入库',
    ms: 'Inbound',
  },
  outbound: {
    en: 'Outbound',
    de: 'Outbound',
    zh: '出库',
    ms: 'Outbound',
  },
  shipment: {
    en: 'Shipment',
    de: 'Sendung',
    zh: '配送',
    ms: 'Penghantaran',
  },
  'business-process': {
    en: 'Business Process',
    de: 'Geschaeftsprozess',
    zh: '业务流程',
    ms: 'Proses Perniagaan',
  },
  workflow: {
    en: 'Workflow',
    de: 'Workflow',
    zh: '工作流',
    ms: 'Workflow',
  },
  approval: {
    en: 'Approval',
    de: 'Genehmigung',
    zh: '审批',
    ms: 'Kelulusan',
  },
  permissions: {
    en: 'Permissions',
    de: 'Berechtigungen',
    zh: '权限',
    ms: 'Kebenaran',
  },
  audit: {
    en: 'Audit',
    de: 'Audit',
    zh: '审计',
    ms: 'Audit',
  },
  uat: {
    en: 'UAT',
    de: 'UAT',
    zh: '用户验收测试',
    ms: 'UAT',
  },
  chart: {
    en: 'Chart',
    de: 'Diagramm',
    zh: '图表',
    ms: 'Carta',
  },
  dashboard: {
    en: 'Dashboard',
    de: 'Dashboard',
    zh: '看板',
    ms: 'Dashboard',
  },
  visualization: {
    en: 'Visualization',
    de: 'Visualisierung',
    zh: '可视化',
    ms: 'Visualisasi',
  },
  'data-contract': {
    en: 'Data Contract',
    de: 'Datenvertrag',
    zh: '数据契约',
    ms: 'Kontrak Data',
  },
  'multiple-charts': {
    en: 'Multiple Charts',
    de: 'Mehrfachcharts',
    zh: '多图表',
    ms: 'Pelbagai Carta',
  },
  'drill-down': {
    en: 'Drill-down',
    de: 'Drill-down',
    zh: '下钻',
    ms: 'Drill-down',
  },
}
function selectLanguage(lang: LanguageCode) {
  currentLanguage.value = lang
  if (languageMenuRef.value) {
    languageMenuRef.value.open = false
  }
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function togglePreviewPanel() {
  previewPanelOpen.value = !previewPanelOpen.value
}

function closePreviewPanel() {
  previewPanelOpen.value = false
}

function openChatView() {
  currentWorkspaceView.value = 'chat'
}

function openTemplateLibraryView() {
  closePreviewPanel()
  currentWorkspaceView.value = 'templates'
}

function clearError() {
  globalError.value = ''
}

function formatError(error: unknown, fallback: string): string {
  if (error instanceof Error) {
    return error.message
  }
  return fallback
}

function normalizeLanguageToken(language: string): string {
  const normalized = String(language || '').trim().toLowerCase().replace('_', '-')
  if (normalized === 'zh' || normalized.startsWith('zh-')) {
    return 'zh'
  }
  return normalized
}

function templateMatchesLanguage(templateItem: BusinessTemplateSummary, language: string): boolean {
  return normalizeLanguageToken(templateItem.language) === normalizeLanguageToken(language)
}

function resolveLocalizedBusinessTemplateSummary(templateId: string): BusinessTemplateSummary | null {
  if (!templateId) {
    return null
  }

  const sourceTemplate = businessTemplates.value.find((item) => item.template_id === templateId)
  if (!sourceTemplate) {
    return null
  }

  const groupingKey = sourceTemplate.template_key || sourceTemplate.template_id
  return (
    businessTemplates.value.find(
      (item) =>
        (item.template_key || item.template_id) === groupingKey &&
        templateMatchesLanguage(item, currentLanguage.value),
    ) ||
    sourceTemplate ||
    null
  )
}

function sessionTemplateName(session: SessionSummary): string {
  return (
    resolveLocalizedBusinessTemplateSummary(session.applied_template_id)?.template_name ||
    session.applied_template_name?.trim() ||
    ''
  )
}

function apiUrl(path: string): string {
  if (!API_BASE_URL) {
    return path
  }
  return `${API_BASE_URL}${path}`
}

function absoluteApiUrl(path: string): string {
  return new URL(apiUrl(path), window.location.origin).toString()
}

function pmApiBaseUrlForExternalHandoff(): string {
  return absoluteApiUrl('/api').replace(/\/api\/?$/, '')
}

function resolveExternalUrl(rawValue: unknown, fallback: string): string {
  const candidate = String(rawValue || '').trim() || fallback
  try {
    return new URL(candidate).toString()
  } catch {
    return new URL(`http://${candidate}`).toString()
  }
}

function localeCode() {
  if (currentLanguage.value === 'zh') {
    return 'zh-CN'
  }
  if (currentLanguage.value === 'de') {
    return 'de-DE'
  }
  if (currentLanguage.value === 'ms') {
    return 'ms-MY'
  }
  return 'en-US'
}

function parseThinkContent(raw: string): { content: string; thinking: string } {
  const thinkRegex = /<think>([\s\S]*?)<\/think>/gi
  const thinkingParts: string[] = []
  let plain = raw
  let match = thinkRegex.exec(raw)

  while (match) {
    if (match[1]?.trim()) {
      thinkingParts.push(match[1].trim())
    }
    match = thinkRegex.exec(raw)
  }

  plain = plain.replace(thinkRegex, '').trim()
  return { content: plain, thinking: thinkingParts.join('\n\n') }
}

function normalizeMessageKind(kind?: string): ChatMessage['kind'] {
  if (kind === 'prd_doc' || kind === 'design_doc') {
    return kind
  }
  return 'chat'
}

function normalizeMessages(rawMessages: ChatMessagePayload[]): ChatMessage[] {
  return rawMessages.map((item) => {
    const normalizedKind = normalizeMessageKind(item.kind)
    const displayContent = item.display_content?.trim() || item.content
    if (item.role !== 'assistant') {
      return {
        role: item.role,
        content: displayContent,
        createdAt: item.created_at,
        kind: normalizedKind,
        downloadUrl: item.download_url,
        downloadFilename: item.download_filename,
      }
    }

    const parsed = parseThinkContent(displayContent)
    return {
      role: item.role,
      content: parsed.content,
      thinking: item.thinking || parsed.thinking,
      createdAt: item.created_at,
      kind: normalizedKind,
      downloadUrl: item.download_url,
      downloadFilename: item.download_filename,
    }
  })
}

function normalizePromptTemplate(value?: string): PromptTemplate {
  return value === 'standard' ? 'standard' : 'personal_project'
}

function humanizeTemplateFacet(value: string): string {
  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

function formatTemplateFacet(value: string): string {
  const normalized = value.trim().toLowerCase()
  if (!normalized) {
    return ''
  }
  return templateFacetLabels[normalized]?.[currentLanguage.value] || humanizeTemplateFacet(normalized)
}

function formatTemplateTag(value: string): string {
  const normalized = value.trim().toLowerCase()
  if (!normalized) {
    return ''
  }
  return templateTagLabels[normalized]?.[currentLanguage.value] || humanizeTemplateFacet(normalized)
}

function resetStructuredRequirementState() {
  structuredRequirementModel.value = createEmptyStructuredRequirementModel()
  conversationChainState.value = createEmptyConversationChainState()
  structuredRequirementError.value = ''
  loadingStructuredRequirement.value = false
  activeStructuredRequirementSyncCount.value = 0
}

function applyStructuredRequirementPayload(payload: unknown) {
  const chainState = extractConversationChainState(payload)
  if (chainState) {
    conversationChainState.value = chainState
  }

  const model = extractStructuredRequirementModel(payload)
  if (model) {
    structuredRequirementModel.value = model
    structuredRequirementError.value = ''
    loadingStructuredRequirement.value = false
  }
}

function beginStructuredRequirementSync() {
  activeStructuredRequirementSyncCount.value += 1
}

function endStructuredRequirementSync() {
  activeStructuredRequirementSyncCount.value = Math.max(0, activeStructuredRequirementSyncCount.value - 1)
}

function createMessagePipelineState() {
  activeReplyCount.value += 1
  activeMessagePipelineCount.value += 1
  return {
    replyReleased: false,
    syncStarted: false,
  }
}

function releaseMessageReplyPhase(state: { replyReleased: boolean }) {
  if (state.replyReleased) {
    return
  }
  state.replyReleased = true
  activeReplyCount.value = Math.max(0, activeReplyCount.value - 1)
}

function startMessageSyncPhase(state: { syncStarted: boolean }) {
  if (state.syncStarted) {
    return
  }
  state.syncStarted = true
  beginStructuredRequirementSync()
}

function finishMessageSyncPhase(state: { syncStarted: boolean }) {
  if (!state.syncStarted) {
    return
  }
  state.syncStarted = false
  endStructuredRequirementSync()
}

function completeMessagePipeline(state: { replyReleased: boolean; syncStarted: boolean }) {
  releaseMessageReplyPhase(state)
  finishMessageSyncPhase(state)
  activeMessagePipelineCount.value = Math.max(0, activeMessagePipelineCount.value - 1)
}

function shouldRefreshStructuredRequirement(syncStatus?: string): boolean {
  return syncStatus === 'stale' || syncStatus === 'missing'
}

function sessionTitle(rawTitle: string): string {
  const title = rawTitle.trim()
  if (!title) {
    return t.value.untitledChat
  }

  if (SESSION_TITLE_LATIN_PATTERN.test(title) && !SESSION_TITLE_CJK_PATTERN.test(title)) {
    const words = title.split(/\s+/)
    if (words.length <= SESSION_TITLE_MAX_ENGLISH_WORDS) {
      return title
    }

    return `${words.slice(0, SESSION_TITLE_MAX_ENGLISH_WORDS).join(' ').trimEnd()}${SESSION_TITLE_ELLIPSIS}`
  }

  const titleChars = Array.from(title)
  if (titleChars.length <= SESSION_TITLE_MAX_CHARS) {
    return title
  }

  return `${titleChars.slice(0, SESSION_TITLE_MAX_CHARS).join('').trimEnd()}${SESSION_TITLE_ELLIPSIS}`
}

function sessionPreview(session: SessionSummary): string {
  return session.last_message_preview?.trim() || t.value.startConversationDesc
}

function canMutateHistory(): boolean {
  return !messagePipelineActive.value && !generatingDocuments.value && !loadingSession.value && !switchingSession.value
}

function formatSessionTime(timestamp?: string): string {
  if (!timestamp) {
    return t.value.justNow
  }

  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return t.value.justNow
  }

  const now = new Date()
  const sameDay = date.toDateString() === now.toDateString()
  const formatter = new Intl.DateTimeFormat(
    localeCode(),
    sameDay
      ? { hour: '2-digit', minute: '2-digit' }
      : { month: 'short', day: 'numeric' },
  )

  return formatter.format(date)
}

function formatMessageTime(timestamp?: string): string {
  if (!timestamp) {
    return ''
  }

  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return ''
  }

  return new Intl.DateTimeFormat(localeCode(), {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

async function apiJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  })

  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const errorMessage = typeof data?.error === 'string' ? data.error : `Request failed: ${response.status}`
    throw new Error(errorMessage)
  }
  return data as T
}

function attachmentContextText(payload: AttachmentExtractionResponse): string {
  const truncatedNote = payload.truncated
    ? currentLanguage.value === 'zh'
      ? '\n（内容较长，已截取前半部分。）'
      : '\n(Content is long; only the first part was extracted.)'
    : ''
  if (currentLanguage.value === 'zh') {
    return `[附件：${payload.filename}]\n以下是从附件中提取的内容，请结合它继续梳理需求：${truncatedNote}\n\n${payload.text}`
  }
  if (currentLanguage.value === 'de') {
    return `[Attachment: ${payload.filename}]\nExtracted content from the attachment; use it to continue requirement discovery:${truncatedNote}\n\n${payload.text}`
  }
  if (currentLanguage.value === 'ms') {
    return `[Lampiran: ${payload.filename}]\nKandungan yang diekstrak daripada lampiran; gunakan untuk meneruskan penemuan keperluan:${truncatedNote}\n\n${payload.text}`
  }
  return `[Attachment: ${payload.filename}]\nExtracted content from the attachment; use it to continue requirement discovery:${truncatedNote}\n\n${payload.text}`
}

function attachmentDisplayLine(attachment: PendingAttachment): string {
  if (currentLanguage.value === 'zh') {
    return `[附件：${attachment.filename}]`
  }
  if (currentLanguage.value === 'de') {
    return `[Anhang: ${attachment.filename}]`
  }
  if (currentLanguage.value === 'ms') {
    return `[Lampiran: ${attachment.filename}]`
  }
  return `[Attachment: ${attachment.filename}]`
}

function attachmentDisplayMessage(typedMessage: string, attachment: PendingAttachment | null): string {
  const baseMessage = typedMessage || t.value.attachmentOnlyPrompt
  if (!attachment) {
    return baseMessage
  }
  return `${baseMessage}\n\n${attachmentDisplayLine(attachment)}`
}

function attachmentModelMessage(displayMessage: string, attachment: PendingAttachment | null): string {
  if (!attachment) {
    return displayMessage
  }
  return `${displayMessage}\n\n${attachment.context}`
}

function pendingAttachmentMeta(attachment: PendingAttachment): string {
  const parts = [attachment.kind.toUpperCase()]
  if (attachment.visualCount > 0) {
    parts.push(`${attachment.visualCount} ${t.value.attachmentVisuals}`)
  }
  return parts.join(' / ')
}

function removePendingAttachment() {
  pendingAttachment.value = null
}

function openAttachmentPicker() {
  if (uploadingAttachment.value || sending.value || generatingDocuments.value || switchingSession.value) {
    return
  }
  attachmentInputRef.value?.click()
}

async function handleAttachmentSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) {
    return
  }

  uploadingAttachment.value = true
  globalError.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file, file.name)
    const response = await fetch(apiUrl('/api/attachments/analyze'), {
      method: 'POST',
      body: formData,
    })
    const data = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(typeof data?.error === 'string' ? data.error : `Request failed: ${response.status}`)
    }
    const attachmentPayload = data as AttachmentExtractionResponse
    pendingAttachment.value = {
      filename: attachmentPayload.filename,
      kind: attachmentPayload.kind,
      size: attachmentPayload.size,
      context: attachmentContextText(attachmentPayload),
      multimodal: Boolean(attachmentPayload.multimodal),
      visualCount: Number(attachmentPayload.visual_count || 0),
    }
    await nextTick()
    autoResizeTextarea()
    textareaRef.value?.focus()
  } catch (error) {
    globalError.value = formatError(error, t.value.attachmentUploadError)
  } finally {
    uploadingAttachment.value = false
  }
}

function isGeneratedDocumentMessage(message: ChatMessage): boolean {
  return message.kind === 'design_doc' || message.kind === 'prd_doc'
}

function findLatestDocumentMessage(kind: NonNullable<ChatMessage['kind']>): ChatMessage | null {
  for (let index = messages.value.length - 1; index >= 0; index -= 1) {
    const message = messages.value[index]
    if (message.kind === kind && message.downloadUrl) {
      return message
    }
  }
  return null
}

function documentBadgeLabel(message: ChatMessage): string {
  if (message.kind === 'prd_doc') {
    return t.value.prdDocLabel
  }
  return t.value.designDocLabel
}

function documentDownloadPath(path: string): string {
  const separator = path.includes('?') ? '&' : '?'
  return `${path}${separator}format=docx`
}

function docxDownloadFilename(filename?: string): string | undefined {
  if (!filename) {
    return undefined
  }
  return filename.replace(/\.md$/i, '.docx')
}

function triggerDocumentDownload(path: string, filename?: string) {
  const link = document.createElement('a')
  link.href = apiUrl(documentDownloadPath(path))
  const docxFilename = docxDownloadFilename(filename)
  if (docxFilename) {
    link.download = docxFilename
  }
  link.rel = 'noopener'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function downloadLatestGeneratedDocument(kind: 'prd' | 'design') {
  const target = kind === 'prd' ? latestPrdDocument.value : latestDesignDocument.value
  if (!target?.downloadUrl) {
    return
  }
  triggerDocumentDownload(target.downloadUrl, target.downloadFilename)
}

function redirectToGoCoding(token: string) {
  const targetUrl = new URL(GO_CODING_URL)
  targetUrl.searchParams.set('source', 'rqmd')
  targetUrl.searchParams.set('handoff_token', token)
  targetUrl.searchParams.set('pm_api_base_url', pmApiBaseUrlForExternalHandoff())
  window.location.assign(targetUrl.toString())
}

async function openGoCoding() {
  if (
    !sessionId.value ||
    openingGoCoding.value ||
    generatingDocuments.value ||
    messagePipelineActive.value ||
    switchingSession.value ||
    !latestPrdDocument.value ||
    !latestDesignDocument.value
  ) {
    return
  }

  clearError()
  openingGoCoding.value = true

  try {
    const payload = await apiJson<CodingHandoffCreateResponse>(
      `/api/sessions/${sessionId.value}/coding-handoff?language=${encodeURIComponent(currentLanguage.value)}`,
      {
        method: 'POST',
      },
    )
    redirectToGoCoding(payload.handoff_token)
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToOpenGoCoding)
  } finally {
    openingGoCoding.value = false
  }
}

async function loadSessions() {
  const data = await apiJson<{ sessions: SessionSummary[] }>('/api/sessions')
  sessions.value = (data.sessions ?? []).map((item) => ({
    ...item,
    prompt_template: normalizePromptTemplate(item.prompt_template),
    applied_template_id: item.applied_template_id || '',
    applied_template_name: item.applied_template_name || '',
  }))
}

async function loadBusinessTemplates() {
  const data = await apiJson<{ templates: BusinessTemplateSummary[] }>('/api/templates')
  businessTemplates.value = data.templates ?? []
}

async function ensureBusinessTemplateDetail(templateId: string): Promise<BusinessTemplateDetail> {
  const cached = businessTemplateDetails.value[templateId]
  if (cached) {
    return cached
  }

  const detail = await apiJson<BusinessTemplateDetail>(`/api/templates/${templateId}`)
  businessTemplateDetails.value = {
    ...businessTemplateDetails.value,
    [templateId]: detail,
  }
  return detail
}

function buildDocumentGenerationConfirmMessage(): string {
  const progress = structuredRequirementProgress.value
  if (currentLanguage.value === 'zh') {
    return `当前文档就绪度为 ${progress.readinessPercentage}%，收集覆盖率为 ${progress.collectionCoveragePercentage}%，确认完成度为 ${progress.confirmationPercentage}%。生成文档至少需要覆盖率 100%、核心项已确认、确认完成度 75%、文档就绪度 80%，且无冲突。请先补齐右侧关键待确认项。`
  }
  if (currentLanguage.value === 'de') {
    return `Die Dokumentreife liegt bei ${progress.readinessPercentage}%, die Erfassungsquote bei ${progress.collectionCoveragePercentage}% und der Bestaetigungsstand bei ${progress.confirmationPercentage}%. Fuer die Dokumenterzeugung sind mindestens 100% Erfassungsquote, bestaetigte Kernpunkte, 75% Bestaetigung, 80% Dokumentreife und keine Konflikte erforderlich. Bitte zuerst die kritischen offenen Punkte klaeren.`
  }
  if (currentLanguage.value === 'ms') {
    return `Kesediaan dokumen kini ${progress.readinessPercentage}%, liputan kutipan ${progress.collectionCoveragePercentage}% dan kemajuan pengesahan ${progress.confirmationPercentage}%. Penjanaan dokumen memerlukan sekurang-kurangnya 100% liputan, item teras disahkan, 75% pengesahan, 80% kesediaan dokumen dan tiada konflik. Sila sahkan item kritikal dahulu.`
  }
  return `Document readiness is ${progress.readinessPercentage}%, collection coverage is ${progress.collectionCoveragePercentage}%, and confirmation progress is ${progress.confirmationPercentage}%. Document generation requires 100% coverage, confirmed core items, 75% confirmation, 80% readiness, and no conflicts. Please resolve the key pending items first.`
}

function requestDocumentGenerationConfirm(): Promise<boolean> {
  if (documentGenerationConfirmResolver) {
    documentGenerationConfirmResolver(false)
  }

  documentGenerationConfirmMessage.value = buildDocumentGenerationConfirmMessage()
  documentGenerationConfirmOpen.value = true

  return new Promise((resolve) => {
    documentGenerationConfirmResolver = resolve
  })
}

function resolveDocumentGenerationConfirm(confirmed: boolean) {
  documentGenerationConfirmOpen.value = false
  documentGenerationConfirmMessage.value = ''
  const resolver = documentGenerationConfirmResolver
  documentGenerationConfirmResolver = null
  resolver?.(confirmed)
}

function requestDeleteSessionConfirm(targetSessionId: string): Promise<boolean> {
  if (deleteSessionConfirmResolver) {
    deleteSessionConfirmResolver(false)
  }

  deleteSessionConfirmTargetId.value = targetSessionId
  deleteSessionConfirmOpen.value = true

  return new Promise((resolve) => {
    deleteSessionConfirmResolver = resolve
  })
}

function resolveDeleteSessionConfirm(confirmed: boolean) {
  deleteSessionConfirmOpen.value = false
  deleteSessionConfirmTargetId.value = ''
  const resolver = deleteSessionConfirmResolver
  deleteSessionConfirmResolver = null
  resolver?.(confirmed)
}
async function loadStructuredRequirement(
  targetSessionId: string,
  options: { background?: boolean } = {},
) {
  if (!targetSessionId) {
    resetStructuredRequirementState()
    return
  }

  const requestToken = ++structuredRequirementRequestToken
  structuredRequirementError.value = ''
  const useBackgroundSync =
    Boolean(options.background) || hasStructuredRequirementContent(structuredRequirementModel.value)

  if (useBackgroundSync) {
    beginStructuredRequirementSync()
  } else {
    loadingStructuredRequirement.value = true
  }

  try {
    const data = await apiJson<StructuredRequirementResponse>(
      `/api/sessions/${targetSessionId}/structured-requirement?language=${encodeURIComponent(currentLanguage.value)}`,
    )
    if (requestToken !== structuredRequirementRequestToken || sessionId.value !== targetSessionId) {
      return
    }
    applyStructuredRequirementPayload(data)
  } catch (error) {
    if (requestToken !== structuredRequirementRequestToken || sessionId.value !== targetSessionId) {
      return
    }
    structuredRequirementError.value = formatError(error, t.value.requestFailed)
    if (!useBackgroundSync) {
      structuredRequirementModel.value = createEmptyStructuredRequirementModel()
    }
  } finally {
    if (useBackgroundSync) {
      endStructuredRequirementSync()
    } else if (requestToken === structuredRequirementRequestToken && sessionId.value === targetSessionId) {
      loadingStructuredRequirement.value = false
    }
  }
}

async function loadSession(targetSessionId: string) {
  if (!targetSessionId) {
    return
  }

  clearError()
  switchingSession.value = true

  try {
    const data = await apiJson<SessionDetail>(
      `/api/sessions/${targetSessionId}?language=${encodeURIComponent(currentLanguage.value)}`,
    )
    applySessionDetail(data)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToLoadSession)
  } finally {
    switchingSession.value = false
  }
}

function applySessionDetail(data: SessionDetail) {
  sessionId.value = data.session_id
  sessionPromptTemplate.value = normalizePromptTemplate(data.prompt_template)
  messages.value = normalizeMessages(data.messages ?? [])
  structuredRequirementError.value = ''
  applyStructuredRequirementPayload(data)
  if (shouldRefreshStructuredRequirement(data.structured_requirement_sync_status)) {
    void loadStructuredRequirement(
      data.session_id,
      { background: hasStructuredRequirementContent(structuredRequirementModel.value) },
    )
  } else {
    loadingStructuredRequirement.value = false
  }
}

async function syncCurrentSessionDetail(targetSessionId: string) {
  if (!targetSessionId) {
    return
  }

  try {
    const data = await apiJson<SessionDetail>(
      `/api/sessions/${targetSessionId}?language=${encodeURIComponent(currentLanguage.value)}`,
    )
    if (sessionId.value !== targetSessionId) {
      return
    }
    applySessionDetail(data)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToLoadSession)
  }
}

async function createSession(
  options: { templateId?: string; templateStartMode?: 'guided' | 'example'; starterDepartment?: string } = {},
) {
  if (messagePipelineActive.value || generatingDocuments.value || loadingSession.value) {
    return
  }

  clearError()
  loadingSession.value = true
  currentWorkspaceView.value = 'chat'

  try {
    const data = await apiJson<SessionDetail>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({
        language: currentLanguage.value,
        ...(options.templateId ? { template_id: options.templateId } : {}),
        ...(options.templateStartMode ? { template_start_mode: options.templateStartMode } : {}),
        ...(options.starterDepartment ? { starter_department: options.starterDepartment } : {}),
      }),
    })

    sessionId.value = data.session_id
    sessionPromptTemplate.value = normalizePromptTemplate(data.prompt_template)
    messages.value = normalizeMessages(data.messages ?? [])
    resetStructuredRequirementState()
    applyStructuredRequirementPayload(data)
    await loadSessions()
    await nextTick()
    scrollToBottom()
    return data
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToCreate)
    return null
  } finally {
    loadingSession.value = false
  }
}

function openNewChatChooser() {
  if (newChatActionDisabled.value) {
    return
  }
  newChatChooserOpen.value = true
}

function closeNewChatChooser() {
  newChatChooserOpen.value = false
}

function findIcSubstrateStarterTemplate(): BusinessTemplateSummary | null {
  const candidates = localizedBusinessTemplates.value
    .filter((templateItem) => {
      const searchable = [
        templateItem.template_id,
        templateItem.template_key,
        templateItem.template_name,
        templateItem.business_domain,
        templateItem.description,
        templateItem.tags.join(' '),
      ]
        .join(' ')
        .toLowerCase()
      return (
        searchable.includes('qdm') ||
        searchable.includes('finished lot') ||
        searchable.includes('ic substrate') ||
        searchable.includes('abf') ||
        searchable.includes('yield') ||
        searchable.includes('良率') ||
        searchable.includes('载板') ||
        searchable.includes('基板')
      )
    })
    .sort((first, second) => {
      const firstId = `${first.template_id} ${first.template_key}`.toLowerCase()
      const secondId = `${second.template_id} ${second.template_key}`.toLowerCase()
      const firstScore = firstId.includes('qdm') ? 0 : 1
      const secondScore = secondId.includes('qdm') ? 0 : 1
      return firstScore - secondScore
    })

  return candidates[0] ?? null
}

async function ensureIcSubstrateStarterTemplate(): Promise<BusinessTemplateSummary | null> {
  let templateItem = findIcSubstrateStarterTemplate()
  if (templateItem || loadingTemplates.value) {
    return templateItem
  }

  loadingTemplates.value = true
  try {
    await loadBusinessTemplates()
    templateItem = findIcSubstrateStarterTemplate()
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToLoadTemplates)
  } finally {
    loadingTemplates.value = false
  }
  return templateItem
}

function starterDepartmentDraft(department: string): string {
  if (!department) {
    return ''
  }
  if (currentLanguage.value === 'zh') {
    return `${department} 想做：`
  }
  if (currentLanguage.value === 'de') {
    return `${department} moechte bauen: `
  }
  if (currentLanguage.value === 'ms') {
    return `${department} mahu bina: `
  }
  return `${department} wants to build: `
}

async function startGeneralNewChat() {
  closeNewChatChooser()
  await createSession()
}

async function startIcSubstrateNewChat(department = '') {
  const templateItem = await ensureIcSubstrateStarterTemplate()
  if (!templateItem) {
    closeNewChatChooser()
    openTemplateLibraryView()
    return
  }

  closeNewChatChooser()
  const created = await launchBusinessTemplateSession(templateItem.template_id, {
    startMode: 'guided',
    starterDepartment: department,
  })
  if (created && department) {
    inputText.value = starterDepartmentDraft(department)
    await nextTick()
    textareaRef.value?.focus()
  }
}

function openTemplateLibraryFromNewChatChooser() {
  closeNewChatChooser()
  openTemplateLibraryView()
}

async function bootstrapSessions() {
  clearError()
  loadingHistory.value = true

  try {
    await loadSessions()
    if (sessions.value.length > 0) {
      await loadSession(sessions.value[0].session_id)
    } else {
      await createSession()
    }
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToLoadHistory)
  } finally {
    loadingHistory.value = false
  }
}

async function refreshHistory() {
  try {
    await loadSessions()
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToLoadHistory)
  }
}

async function openBusinessTemplate(templateId: string) {
  if (
    !templateId ||
    loadingSession.value ||
    switchingSession.value ||
    deletingSessionId.value ||
    messagePipelineActive.value ||
    generatingDocuments.value
  ) {
    return
  }

  selectedBusinessTemplateId.value = templateId
  templateDialogOpen.value = true
  templateDialogError.value = ''
  loadingTemplateDetail.value = true

  try {
    await ensureBusinessTemplateDetail(templateId)
  } catch (error) {
    templateDialogError.value = formatError(error, t.value.failedToLoadTemplates)
  } finally {
    loadingTemplateDetail.value = false
  }
}

function closeBusinessTemplateDialog() {
  templateDialogOpen.value = false
  loadingTemplateDetail.value = false
  templateDialogError.value = ''
  selectedBusinessTemplateId.value = ''
}

async function launchBusinessTemplateSession(
  templateId: string,
  options: { closeDialog?: boolean; startMode?: 'guided' | 'example'; starterDepartment?: string } = {},
) {
  if (
    !templateId ||
    applyingTemplateId.value ||
    loadingSession.value ||
    switchingSession.value ||
    deletingSessionId.value ||
    messagePipelineActive.value ||
    generatingDocuments.value
  ) {
    return
  }

  applyingTemplateId.value = templateId
  templateDialogError.value = ''

  try {
    const created = await createSession({
      templateId,
      templateStartMode: options.startMode ?? 'guided',
      starterDepartment: options.starterDepartment,
    })
    if (created) {
      currentWorkspaceView.value = 'chat'
      if (options.closeDialog) {
        closeBusinessTemplateDialog()
      }
    }
    return created
  } catch (error) {
    templateDialogError.value = formatError(error, t.value.failedToCreate)
    return null
  } finally {
    applyingTemplateId.value = ''
  }
}

async function applyBusinessTemplate() {
  const detail = selectedBusinessTemplate.value
  if (
    !detail ||
    applyingTemplateId.value ||
    loadingSession.value ||
    switchingSession.value ||
    deletingSessionId.value ||
    messagePipelineActive.value ||
    generatingDocuments.value
  ) {
    return
  }
  await launchBusinessTemplateSession(detail.template_id, { closeDialog: true })
}

async function applyBusinessTemplateExample() {
  const detail = selectedBusinessTemplate.value
  if (
    !detail ||
    !detail.has_example_model ||
    applyingTemplateId.value ||
    loadingSession.value ||
    switchingSession.value ||
    deletingSessionId.value ||
    messagePipelineActive.value ||
    generatingDocuments.value
  ) {
    return
  }
  await launchBusinessTemplateSession(detail.template_id, { closeDialog: true, startMode: 'example' })
}

async function updatePromptTemplate(template: PromptTemplate) {
  if (!sessionId.value || !canChangePromptTemplate.value || sessionPromptTemplate.value === template) {
    return
  }

  clearError()

  try {
    const data = await apiJson<SessionDetail>(`/api/sessions/${sessionId.value}/prompt-template`, {
      method: 'POST',
      body: JSON.stringify({ prompt_template: template }),
    })

    const normalizedTemplate = normalizePromptTemplate(data.prompt_template)
    sessionPromptTemplate.value = normalizedTemplate
    sessions.value = sessions.value.map((item) =>
      item.session_id === data.session_id
        ? { ...item, prompt_template: normalizedTemplate }
        : item,
    )
  } catch (error) {
    globalError.value = formatError(error, t.value.requestFailed)
  }
}

async function selectSession(targetSessionId: string) {
  if (
    !targetSessionId ||
    targetSessionId === sessionId.value ||
    messagePipelineActive.value ||
    generatingDocuments.value ||
    loadingSession.value ||
    deletingSessionId.value
  ) {
    return
  }
  currentWorkspaceView.value = 'chat'
  await loadSession(targetSessionId)
}

async function deleteSession(targetSessionId: string) {
  if (!targetSessionId || !canMutateHistory() || deletingSessionId.value || deleteSessionConfirmOpen.value) {
    return
  }

  const confirmed = await requestDeleteSessionConfirm(targetSessionId)
  if (!confirmed) {
    return
  }

  clearError()
  deletingSessionId.value = targetSessionId

  try {
    await apiJson<Record<string, never>>(`/api/sessions/${targetSessionId}`, {
      method: 'DELETE',
    })

    const remainingSessions = sessions.value.filter((item) => item.session_id !== targetSessionId)
    sessions.value = remainingSessions

    if (sessionId.value !== targetSessionId) {
      return
    }

    if (remainingSessions.length > 0) {
      await loadSession(remainingSessions[0].session_id)
      return
    }

    sessionId.value = ''
    sessionPromptTemplate.value = 'personal_project'
    messages.value = []
    resetStructuredRequirementState()
    await createSession()
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToDeleteSession)
  } finally {
    deletingSessionId.value = ''
  }
}

function parseSseEvent(eventBlock: string): { event: string; data: string } {
  const lines = eventBlock.split(/\r?\n/)
  let eventName = 'message'
  const dataLines: string[] = []

  for (const line of lines) {
    if (!line || line.startsWith(':')) {
      continue
    }
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim()
      continue
    }
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }

  return { event: eventName, data: dataLines.join('\n') }
}

function splitSseBlocks(rawBuffer: string): { blocks: string[]; rest: string } {
  const blocks: string[] = []
  const separator = /(?:\r?\n){2}/g
  let lastIndex = 0
  let match: RegExpExecArray | null = separator.exec(rawBuffer)

  while (match) {
    const block = rawBuffer.slice(lastIndex, match.index)
    if (block.trim()) {
      blocks.push(block)
    }
    lastIndex = separator.lastIndex
    match = separator.exec(rawBuffer)
  }

  return {
    blocks,
    rest: rawBuffer.slice(lastIndex),
  }
}

function createSmoothWriter(target: ChatMessage) {
  let pending = ''
  let scheduled = false

  const flush = () => {
    if (!pending) {
      scheduled = false
      return
    }
    target.content += pending
    pending = ''
    scheduled = false
    scrollToBottom()
  }

  const scheduleFlush = () => {
    if (scheduled) {
      return
    }
    scheduled = true
    window.requestAnimationFrame(flush)
  }

  return {
    push(chunk: string) {
      if (!chunk) {
        return
      }
      pending += chunk
      scheduleFlush()
    },
    async finish() {
      flush()
      scrollToBottom()
    },
  }
}

async function sendMessageStream(
  session: string,
  message: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
  pipelineState?: { replyReleased: boolean; syncStarted: boolean },
  displayMessage?: string,
) {
  const response = await fetch(apiUrl(`/api/sessions/${session}/messages/stream`), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, language, display_message: displayMessage || message }),
  })

  if (!response.ok) {
    const errorJson = await response.json().catch(() => ({}))
    throw new Error(typeof errorJson?.error === 'string' ? errorJson.error : `Request failed: ${response.status}`)
  }

  if (!response.body) {
    throw new Error(t.value.browserNotSupport)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const writer = createSmoothWriter(assistantMessage)

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const extracted = splitSseBlocks(buffer)
    const chunks = extracted.blocks
    buffer = extracted.rest

    for (const chunk of chunks) {
      const parsed = parseSseEvent(chunk)
      let payload: any = {}
      try {
        payload = parsed.data ? JSON.parse(parsed.data) : {}
      } catch {
        payload = {}
      }

      if (parsed.event === 'error') {
        throw new Error(payload.error || t.value.streamingError)
      }

      if (parsed.event === 'content' && typeof payload.delta === 'string') {
        writer.push(payload.delta)
      }

      if (parsed.event === 'thinking' && typeof payload.delta === 'string') {
        assistantMessage.thinking = (assistantMessage.thinking || '') + payload.delta
        scrollToBottom()
      }

      if (parsed.event === 'thinking_done' && typeof payload.thinking === 'string') {
        assistantMessage.thinking = payload.thinking
        scrollToBottom()
      }

      if (parsed.event === 'assistant_done') {
        if (pipelineState) {
          releaseMessageReplyPhase(pipelineState)
          startMessageSyncPhase(pipelineState)
        }
      }

      if (parsed.event === 'summary') {
        applyStructuredRequirementPayload(payload)
        if (pipelineState) {
          finishMessageSyncPhase(pipelineState)
        }
      }
    }
  }

  await writer.finish()
}

async function sendMessageFallback(
  session: string,
  message: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
  displayMessage?: string,
) {
  const data = await apiJson<MessageResponse>(`/api/sessions/${session}/messages`, {
    method: 'POST',
    body: JSON.stringify({ message, language, display_message: displayMessage || message }),
  })

  const parsed = parseThinkContent(data.assistant_message || '')
  assistantMessage.content = parsed.content
  assistantMessage.thinking = data.assistant_thinking || parsed.thinking
  applyStructuredRequirementPayload(data)
}

function documentKindFromType(documentType?: string): ChatMessage['kind'] {
  if (documentType === 'prd_markdown') {
    return 'prd_doc'
  }
  if (documentType === 'system_design_markdown') {
    return 'design_doc'
  }
  return 'chat'
}

function applyGeneratedDocumentResponse(
  assistantMessage: ChatMessage,
  payload: Partial<GeneratedDocumentResponse>,
) {
  if (typeof payload.document_markdown === 'string') {
    assistantMessage.content = payload.document_markdown
  }

  const resolvedKind = documentKindFromType(payload.document_type)
  assistantMessage.kind = resolvedKind === 'chat' ? assistantMessage.kind || 'chat' : resolvedKind
  assistantMessage.downloadUrl = payload.download_url
  assistantMessage.downloadFilename = payload.filename
  assistantMessage.createdAt = payload.saved_at || assistantMessage.createdAt
  applyStructuredRequirementPayload(payload)
}

function finalizeGeneratedDocumentContent(assistantMessage: ChatMessage) {
  const parsed = parseThinkContent(assistantMessage.content)
  assistantMessage.content = parsed.content
  assistantMessage.thinking = [assistantMessage.thinking || '', parsed.thinking].filter(Boolean).join('\n\n')
}

function createGeneratedDocumentMessage(kind: NonNullable<ChatMessage['kind']>): ChatMessage {
  return {
    role: 'assistant',
    content: '',
    thinking: '',
    createdAt: new Date().toISOString(),
    kind,
    streaming: true,
  }
}

async function sendDocumentStream(
  session: string,
  endpoint: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
) {
  const response = await fetch(apiUrl(`/api/sessions/${session}/${endpoint}/stream`), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ language }),
  })

  if (!response.ok) {
    const errorJson = await response.json().catch(() => ({}))
    throw new Error(typeof errorJson?.error === 'string' ? errorJson.error : `Request failed: ${response.status}`)
  }

  if (!response.body) {
    throw new Error(t.value.browserNotSupport)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const writer = createSmoothWriter(assistantMessage)

  while (true) {
    const { done, value } = await reader.read()
    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const extracted = splitSseBlocks(buffer)
    const chunks = extracted.blocks
    buffer = extracted.rest

    for (const chunk of chunks) {
      const parsed = parseSseEvent(chunk)
      let payload: any = {}
      try {
        payload = parsed.data ? JSON.parse(parsed.data) : {}
      } catch {
        payload = {}
      }

      if (parsed.event === 'error') {
        throw new Error(payload.error || t.value.streamingError)
      }

      if (parsed.event === 'content' && typeof payload.delta === 'string') {
        writer.push(payload.delta)
      }

      if (parsed.event === 'thinking' && typeof payload.delta === 'string') {
        assistantMessage.thinking = (assistantMessage.thinking || '') + payload.delta
        scrollToBottom()
      }

      if (parsed.event === 'thinking_done' && typeof payload.thinking === 'string') {
        assistantMessage.thinking = payload.thinking
        scrollToBottom()
      }

      if (parsed.event === 'done') {
        applyGeneratedDocumentResponse(assistantMessage, payload)
      }
    }
  }

  await writer.finish()
}

async function sendDocumentFallback(
  session: string,
  endpoint: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
) {
  const data = await apiJson<GeneratedDocumentResponse>(`/api/sessions/${session}/${endpoint}`, {
    method: 'POST',
    body: JSON.stringify({ language }),
  })

  applyGeneratedDocumentResponse(assistantMessage, data)
}

async function sendPrdDocStream(
  session: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
) {
  await sendDocumentStream(session, 'prd-doc', assistantMessage, language)
}

async function sendPrdDocFallback(
  session: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
) {
  await sendDocumentFallback(session, 'prd-doc', assistantMessage, language)
}

async function sendDesignDocStream(
  session: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
) {
  await sendDocumentStream(session, 'design-doc', assistantMessage, language)
}

async function sendDesignDocFallback(
  session: string,
  assistantMessage: ChatMessage,
  language: LanguageCode = 'zh',
) {
  await sendDocumentFallback(session, 'design-doc', assistantMessage, language)
}

function scrollToBottom() {
  const align = (remainingFrames = 2) => {
    if (!chatList.value) {
      return
    }

    chatList.value.scrollTop = chatList.value.scrollHeight

    if (remainingFrames > 0) {
      window.requestAnimationFrame(() => align(remainingFrames - 1))
    }
  }

  void nextTick(() => {
    window.requestAnimationFrame(() => align())
  })
}

function appendReactiveMessage(message: ChatMessage): ChatMessage {
  messages.value.push(message)
  return messages.value[messages.value.length - 1] as ChatMessage
}

function finishGeneratedDocumentMessage(message: ChatMessage) {
  finalizeGeneratedDocumentContent(message)
  message.streaming = false
}

function autoResizeTextarea() {
  const textarea = textareaRef.value
  if (textarea) {
    if (!textarea.value) {
      textarea.style.height = ''
      return
    }

    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 300) + 'px'
  }
}

async function insertLineBreak(event: KeyboardEvent) {
  event.preventDefault()
  const target = event.target
  if (!(target instanceof HTMLTextAreaElement)) {
    return
  }

  const start = target.selectionStart
  const end = target.selectionEnd
  inputText.value = `${inputText.value.slice(0, start)}\n${inputText.value.slice(end)}`

  await nextTick()
  if (textareaRef.value) {
    textareaRef.value.selectionStart = start + 1
    textareaRef.value.selectionEnd = start + 1
  }
  autoResizeTextarea()
}

async function sendMessage() {
  const typedMessage = inputText.value.trim()
  const attachment = pendingAttachment.value
  if ((!typedMessage && !attachment) || sending.value || generatingDocuments.value || switchingSession.value) {
    return
  }

  if (!hasSession.value) {
    await createSession()
    if (!hasSession.value) {
      return
    }
  }

  clearError()
  const pipelineState = createMessagePipelineState()
  const displayMessage = attachmentDisplayMessage(typedMessage, attachment)
  const message = attachmentModelMessage(displayMessage, attachment)

  const userChatMessage = appendReactiveMessage({
    role: 'user',
    content: displayMessage,
    createdAt: new Date().toISOString(),
  })
  const assistantMessage = appendReactiveMessage({
    role: 'assistant',
    content: '',
    thinking: '',
    createdAt: new Date().toISOString(),
  })
  inputText.value = ''
  pendingAttachment.value = null
  if (textareaRef.value) {
    textareaRef.value.value = ''
    textareaRef.value.style.height = ''
  }
  await nextTick()
  autoResizeTextarea()
  scrollToBottom()

  try {
    await sendMessageStream(
      sessionId.value,
      message,
      assistantMessage,
      currentLanguage.value,
      pipelineState,
      displayMessage,
    )
    const streamParsed = parseThinkContent(assistantMessage.content)
    assistantMessage.content = streamParsed.content
    assistantMessage.thinking = [assistantMessage.thinking || '', streamParsed.thinking].filter(Boolean).join('\n\n')

    if (!assistantMessage.content.trim()) {
      await sendMessageFallback(sessionId.value, message, assistantMessage, currentLanguage.value, displayMessage)
    }

    await refreshHistory()
  } catch (error) {
    messages.value = messages.value.filter(
      (item) => item !== userChatMessage && item !== assistantMessage,
    )
    pendingAttachment.value = attachment
    inputText.value = typedMessage
    globalError.value = formatError(error, t.value.failedToSend)
  } finally {
    completeMessagePipeline(pipelineState)
    scrollToBottom()
  }
}

async function generateDocuments() {
  if (
    !hasSession.value ||
    generatingDocuments.value ||
    documentGenerationConfirmOpen.value ||
    messagePipelineActive.value ||
    switchingSession.value
  ) {
    return
  }

  if (!structuredRequirementProgress.value.readyToGenerate) {
    await requestDocumentGenerationConfirm()
    return
  }

  clearError()
  generatingDocuments.value = true
  let shouldRefreshHistory = false

  try {
    const prdMessage = appendReactiveMessage(createGeneratedDocumentMessage('prd_doc'))
    scrollToBottom()

    await sendPrdDocStream(sessionId.value, prdMessage, currentLanguage.value)
    finishGeneratedDocumentMessage(prdMessage)
    if (!prdMessage.content.trim()) {
      await sendPrdDocFallback(sessionId.value, prdMessage, currentLanguage.value)
      finishGeneratedDocumentMessage(prdMessage)
    }
    shouldRefreshHistory = true

    const designMessage = appendReactiveMessage(createGeneratedDocumentMessage('design_doc'))
    scrollToBottom()

    await sendDesignDocStream(sessionId.value, designMessage, currentLanguage.value)
    finishGeneratedDocumentMessage(designMessage)
    if (!designMessage.content.trim()) {
      await sendDesignDocFallback(sessionId.value, designMessage, currentLanguage.value)
      finishGeneratedDocumentMessage(designMessage)
    }
    shouldRefreshHistory = true
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToGenerate)
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'assistant' && !last.content) {
      messages.value.pop()
    } else if (last && isGeneratedDocumentMessage(last)) {
      last.streaming = false
    }
  } finally {
    if (shouldRefreshHistory) {
      await refreshHistory()
      await syncCurrentSessionDetail(sessionId.value)
    }
    generatingDocuments.value = false
    scrollToBottom()
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    audioBuffer.value = []

    audioContext.value = new AudioContext({ sampleRate: 16000 })
    const source = audioContext.value.createMediaStreamSource(stream)
    const processor = audioContext.value.createScriptProcessor(4096, 1, 1)

    processor.onaudioprocess = (event) => {
      const inputData = event.inputBuffer.getChannelData(0)
      audioBuffer.value.push(new Float32Array(inputData))
    }

    source.connect(processor)
    processor.connect(audioContext.value.destination)

    scriptProcessor.value = processor
    recording.value = true
  } catch (error) {
    console.error('Error starting recording:', error)
    globalError.value = t.value.microphoneAccessError
  }
}

function stopRecording() {
  if (audioContext.value && scriptProcessor.value) {
    scriptProcessor.value.disconnect()

    if (audioContext.value.state !== 'closed') {
      audioContext.value.close()
    }

    const totalLength = audioBuffer.value.reduce((acc, chunk) => acc + chunk.length, 0)
    const result = new Float32Array(totalLength)
    let offset = 0
    for (const chunk of audioBuffer.value) {
      result.set(chunk, offset)
      offset += chunk.length
    }

    const pcmData = new Int16Array(result.length)
    for (let i = 0; i < result.length; i++) {
      pcmData[i] = Math.max(-32768, Math.min(32767, result[i] * 32767))
    }

    const wavData = createWavHeader(pcmData.buffer)

    const formData = new FormData()
    const audioBlob = new Blob([wavData], { type: 'audio/wav' })
    formData.append('audio', audioBlob, 'recording.wav')

    fetch(apiUrl('/api/asr/recognize'), {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.text) {
          inputText.value = data.text
          sendMessage()
        } else if (data.error) {
          globalError.value = data.error
        }
      })
      .catch((error) => {
        console.error('Error recognizing speech:', error)
        globalError.value = t.value.speechRecognitionError
      })

    recording.value = false
  }
}

function createWavHeader(pcmData: ArrayBuffer) {
  const dataLength = pcmData.byteLength
  const buffer = new ArrayBuffer(44 + dataLength)
  const view = new DataView(buffer)

  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataLength, true)
  writeString(view, 8, 'WAVE')

  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, 16000, true)
  view.setUint32(28, 32000, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)

  writeString(view, 36, 'data')
  view.setUint32(40, dataLength, true)

  const pcmArray = new Int16Array(pcmData)
  const dataView = new DataView(buffer, 44)
  for (let i = 0; i < pcmArray.length; i++) {
    dataView.setInt16(i * 2, pcmArray[i], true)
  }

  return buffer
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

onMounted(async () => {
  loadingTemplates.value = true
  try {
    await loadBusinessTemplates()
  } catch (error) {
    globalError.value = formatError(error, t.value.failedToLoadTemplates)
  } finally {
    loadingTemplates.value = false
  }
  await bootstrapSessions()
})

watch(currentLanguage, (language, previousLanguage) => {
  const localizedTemplate = resolveLocalizedBusinessTemplateSummary(selectedBusinessTemplateId.value)
  if (localizedTemplate && localizedTemplate.template_id !== selectedBusinessTemplateId.value) {
    selectedBusinessTemplateId.value = localizedTemplate.template_id
    loadingTemplateDetail.value = true
    void ensureBusinessTemplateDetail(localizedTemplate.template_id)
      .catch((error) => {
        templateDialogError.value = formatError(error, t.value.failedToLoadTemplates)
      })
      .finally(() => {
        loadingTemplateDetail.value = false
      })
  }

  if (!sessionId.value || language === previousLanguage) {
    return
  }
  void loadStructuredRequirement(
    sessionId.value,
    { background: hasStructuredRequirementContent(structuredRequirementModel.value) },
  )
})

watch(messageRenderSignature, (signature, previousSignature) => {
  if (!isChatView.value || !messages.value.length || signature === previousSignature) {
    return
  }
  scrollToBottom()
})
</script>

<template>
  <div class="app-shell">
    <div v-if="globalError" class="error-banner" @click="clearError">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <span>{{ globalError }}</span>
      <button class="close-btn" :aria-label="t.close">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <main class="layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-topbar">
          <div class="sidebar-identity">
            <button
              class="sidebar-toggle"
              type="button"
              :title="sidebarToggleAriaLabel"
              :aria-label="sidebarToggleAriaLabel"
              :aria-expanded="!sidebarCollapsed"
              @click="toggleSidebar"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">
                <line x1="4" y1="7" x2="20" y2="7"/>
                <line x1="4" y1="12" x2="20" y2="12"/>
                <line x1="4" y1="17" x2="20" y2="17"/>
              </svg>
            </button>
            <div v-if="!sidebarCollapsed" class="sidebar-appmark">
              <strong>{{ t.title }}</strong>
              <span>{{ shellText.heroTag }}</span>
            </div>
          </div>

        </div>

        <div v-show="!sidebarCollapsed" class="sidebar-body">
          <nav class="sidebar-nav">
            <button type="button" class="sidebar-nav-item" :class="{ active: isChatView }" @click="openChatView">
              <span class="sidebar-nav-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </span>
              <span class="sidebar-nav-text">
                <strong>{{ t.conversation }}</strong>
                <small>{{ activeSessionTitle || t.untitledChat }}</small>
              </span>
            </button>
            <button
              type="button"
              class="sidebar-nav-item"
              :class="{ active: isTemplateLibraryView }"
              @click="openTemplateLibraryView"
            >
              <span class="sidebar-nav-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 7h16"/>
                  <path d="M4 12h16"/>
                  <path d="M4 17h10"/>
                </svg>
              </span>
              <span class="sidebar-nav-text">
                <strong>{{ t.templateLibrary }}</strong>
                <small>{{ templateCountLabel }}</small>
              </span>
            </button>
          </nav>

          <button
            class="sidebar-new-chat"
            type="button"
            :title="t.newChat"
            :aria-label="t.newChat"
            :disabled="newChatActionDisabled"
            @click="openNewChatChooser"
          >
            <span class="sidebar-new-chat-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </span>
            <span>{{ loadingSession ? t.creating : t.newChat }}</span>
          </button>

          <div class="sidebar-menu-scroll">
            <section v-if="false" ref="templateLibrarySectionRef" class="sidebar-block sidebar-template-block">
              <div class="sidebar-block-head">
                <h2>{{ t.templateLibrary }}</h2>
                <span>{{ loadingTemplates ? t.templateLibraryLoading : templateCountLabel }}</span>
              </div>

              <div v-if="loadingTemplates && !templateShelfItems.length" class="session-history-placeholder">
                {{ t.templateLibraryLoading }}
              </div>
              <div v-else-if="templateShelfItems.length" class="template-library-list">
                <button
                  v-for="templateItem in templateShelfItems"
                  :key="templateItem.template_id"
                  class="template-library-item"
                  type="button"
                  :disabled="loadingSession || messagePipelineActive || generatingDocuments || Boolean(applyingTemplateId)"
                  @click="openBusinessTemplate(templateItem.template_id)"
                >
                  <span class="menu-entry-accent template" aria-hidden="true"></span>
                  <div class="template-library-item-main">
                    <div class="template-library-item-top">
                      <span class="template-library-item-title">{{ templateItem.template_name }}</span>
                      <span class="template-library-item-count">{{ templateItem.section_count }}</span>
                    </div>
                    <p class="template-library-item-meta">
                      {{ formatTemplateFacet(templateItem.business_domain || templateItem.template_category) }}
                      <span v-if="templateItem.version"> · v{{ templateItem.version }}</span>
                    </p>
                  </div>
                </button>
              </div>
              <div v-else class="session-history-placeholder">
                {{ t.templateLibraryEmpty }}
              </div>
            </section>

            <section class="sidebar-block sidebar-history-block">
              <div class="sidebar-block-head">
                <h2>{{ shellText.recent }}</h2>
                <span>{{ loadingHistory ? t.historyLoading : sessionCountLabel }}</span>
              </div>

              <div v-if="loadingHistory && !recentSessions.length" class="session-history-placeholder">
                {{ t.historyLoading }}
              </div>
              <div v-else-if="recentSessions.length" class="session-history-list">
                <div
                  v-for="session in recentSessions"
                  :key="session.session_id"
                  class="session-card"
                  :class="{ active: session.session_id === sessionId }"
                >
                  <button
                    class="session-card-main"
                    type="button"
                    :disabled="switchingSession || sending || generatingDocuments || Boolean(deletingSessionId)"
                    @click="selectSession(session.session_id)"
                  >
                    <span class="menu-entry-accent recent" aria-hidden="true"></span>
                    <div class="session-card-copy">
                      <div class="session-card-top">
                        <span class="session-card-title">{{ sessionTitle(session.title) }}</span>
                        <span class="session-card-time">{{ formatSessionTime(session.updated_at) }}</span>
                      </div>
                      <p class="session-card-preview">{{ sessionPreview(session) }}</p>
                      <p v-if="sessionTemplateName(session)" class="session-card-template">
                        {{ sessionTemplateName(session) }}
                      </p>
                    </div>
                  </button>

                  <button
                    class="session-card-delete"
                    type="button"
                    :title="t.deleteSession"
                    :aria-label="t.deleteSession"
                    :disabled="!canMutateHistory() || deleteSessionConfirmOpen || deletingSessionId === session.session_id"
                    @click="deleteSession(session.session_id)"
                  >
                    <svg class="session-card-delete-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                      <path d="M10 11v6"/>
                      <path d="M14 11v6"/>
                      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                    </svg>
                  </button>
                </div>
              </div>
              <div v-else class="session-history-placeholder">
                {{ t.historyEmpty }}
              </div>
            </section>
          </div>
        </div>      </aside>

      <section class="main-shell">
        <header class="main-topbar">
          <div class="ats-lockup" aria-label="AT&S AI Platform">
            <img class="ats-lockup-logo" src="./logo.svg" alt="AT&S AI Platform" />
          </div>

          <div class="main-topbar-actions">
            <details ref="languageMenuRef" class="language-switcher">
              <summary>
                <span class="language-switcher-label">{{ t.languageSection }}</span>
                <span class="language-switcher-value">{{ currentLanguageLabel }}</span>
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
                  :class="{ active: currentLanguage === option.code }"
                  @click="selectLanguage(option.code)"
                >
                  {{ option.label }}
                </button>
              </div>
            </details>
          </div>
        </header>

        <div v-if="isChatView" class="main-stage">
          <section class="conversation-shell" :class="{ 'has-messages': messages.length > 0 }">
            <div v-if="!messages.length" class="welcome-stage">
              <div class="welcome-copy">
                <p class="welcome-kicker">{{ shellText.heroTag }}</p>
              </div>

              <div class="assistant-prompt">
                <span class="assistant-prompt-badge">AI</span>
                <p>{{ shellText.assistantIntro }}</p>
              </div>
            </div>

            <div v-else class="chat-stream-shell">
              <div class="conversation-meta">
                <div class="conversation-title-wrap">
                  <h2>{{ activeSessionTitle || t.conversation }}</h2>
                  <span class="conversation-chip">{{ activeMessageCountLabel }}</span>
                  <span v-if="activeBusinessTemplateName" class="conversation-chip accent">
                    {{ activeBusinessTemplateName }}
                  </span>
                </div>
              </div>

              <div class="chat-list" ref="chatList">
                <div
                  v-for="(msg, idx) in messages"
                  :key="`${msg.role}-${idx}`"
                  class="bubble"
                  :class="[msg.role, { 'design-doc-bubble': isGeneratedDocumentMessage(msg) }]"
                >
                  <div class="message-header">
                    <span class="role">{{ msg.role === 'user' ? t.you : t.pmAssistant }}</span>
                    <span class="timestamp">{{ formatMessageTime(msg.createdAt) }}</span>
                  </div>

                  <details v-if="msg.role === 'assistant' && msg.thinking" class="think-box" :open="!msg.content">
                    <summary class="think-box-summary">
                      <svg class="think-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M12 16v-4"/>
                        <path d="M12 8h.01"/>
                      </svg>
                      {{ t.viewReasoning }}
                    </summary>
                    <pre class="think-content">{{ msg.thinking }}</pre>
                  </details>

                  <div v-if="(sending || generatingDocuments) && msg.role === 'assistant' && !msg.content" class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                  </div>
                  <div v-else-if="isGeneratedDocumentMessage(msg)" class="design-doc-card">
                    <div class="design-doc-toolbar">
                      <span class="design-doc-badge">{{ documentBadgeLabel(msg) }}</span>
                    </div>
                    <pre v-if="msg.streaming" class="content design-doc-content streaming-doc-content">{{ msg.content }}</pre>
                    <MarkdownRenderer v-else class="content design-doc-content" :source="msg.content" />
                    <div v-if="msg.downloadUrl" class="design-doc-footer">
                      <button
                        class="btn btn-secondary design-doc-download"
                        type="button"
                        @click="triggerDocumentDownload(msg.downloadUrl, msg.downloadFilename)"
                      >
                        <svg class="btn-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M12 3v12"/>
                          <path d="M7 10l5 5 5-5"/>
                          <path d="M5 21h14"/>
                        </svg>
                        {{ t.downloadMarkdown }}
                      </button>
                    </div>
                  </div>
                  <MarkdownRenderer
                    v-else-if="msg.role === 'assistant'"
                    class="content"
                    :source="msg.content"
                  />
                  <p v-else class="content">{{ msg.content }}</p>
                </div>
              </div>
            </div>

            <div class="composer-zone">
              <div v-if="hasSession" class="composer-context">
                <div class="composer-context-row" :class="{ 'template-driven': templateDrivenSession }">
                  <div v-if="conversationChainVisible" class="conversation-chain-status">
                    <span class="conversation-chain-mode">{{ conversationChainModeLabel }}</span>
                    <span class="conversation-chain-node">{{ conversationChainNodeLabel }}</span>
                    <span v-if="conversationChainProgressLabel" class="conversation-chain-progress">
                      {{ conversationChainProgressLabel }}
                    </span>
                    <span class="conversation-chain-state">{{ conversationChainStatusLabel }}</span>
                  </div>
                  <div v-if="!templateDrivenSession" class="template-picker-options">
                    <button
                      v-for="option in promptTemplateOptions"
                      :key="option.value"
                      class="template-chip"
                      :class="{ active: sessionPromptTemplate === option.value }"
                      type="button"
                      :disabled="!canChangePromptTemplate"
                      @click="updatePromptTemplate(option.value)"
                    >
                      {{ option.label }}
                    </button>
                  </div>
                  <div class="composer-context-actions">
                    <div v-if="latestPrdDocument || latestDesignDocument" class="composer-document-actions">
                      <button
                        v-if="latestPrdDocument"
                        class="composer-document-download-btn"
                        type="button"
                        :aria-label="`${t.downloadMarkdown}: ${t.prdDocLabel}`"
                        :title="t.prdDocLabel"
                        :disabled="sending || generatingDocuments || switchingSession"
                        @click="downloadLatestGeneratedDocument('prd')"
                      >
                        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M12 3v12"/>
                          <path d="M7 10l5 5 5-5"/>
                          <path d="M5 21h14"/>
                        </svg>
                        <span>{{ t.prdDocLabel }}</span>
                      </button>
                      <button
                        v-if="latestDesignDocument"
                        class="composer-document-download-btn"
                        type="button"
                        :aria-label="`${t.downloadMarkdown}: ${t.designDocLabel}`"
                        :title="t.designDocLabel"
                        :disabled="sending || generatingDocuments || switchingSession"
                        @click="downloadLatestGeneratedDocument('design')"
                      >
                        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M12 3v12"/>
                          <path d="M7 10l5 5 5-5"/>
                          <path d="M5 21h14"/>
                        </svg>
                        <span>{{ t.designDocLabel }}</span>
                      </button>
                    </div>
                    <button
                      class="preview-toggle-btn"
                      type="button"
                      :aria-expanded="previewPanelOpen"
                      @click="togglePreviewPanel"
                    >
                      {{ previewToggleLabel }}
                    </button>
                  </div>
                </div>
              </div>

              <form class="composer-card" @submit.prevent="sendMessage">
                <input
                  ref="attachmentInputRef"
                  class="composer-file-input"
                  type="file"
                  accept=".pptx,.docx,.xlsx,.pdf,.png,.jpg,.jpeg,.webp,.gif,.txt,.md,.csv,.json,.log"
                  @change="handleAttachmentSelected"
                />
                <div v-if="pendingAttachment" class="composer-attachment-chip">
                  <span class="composer-attachment-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21.4 11.6 12 21a6 6 0 0 1-8.5-8.5l9.9-9.9a4 4 0 0 1 5.7 5.7l-10 10a2 2 0 0 1-2.8-2.8l9.4-9.4"/>
                    </svg>
                  </span>
                  <span class="composer-attachment-copy">
                    <strong>{{ pendingAttachment.filename }}</strong>
                    <small>{{ t.attachmentReady }} / {{ pendingAttachmentMeta(pendingAttachment) }}</small>
                  </span>
                  <button
                    class="composer-attachment-remove"
                    type="button"
                    :aria-label="t.removeAttachment"
                    :title="t.removeAttachment"
                    @click="removePendingAttachment"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 6 6 18"/>
                      <path d="m6 6 12 12"/>
                    </svg>
                  </button>
                </div>
                <textarea
                  v-model="inputText"
                  rows="1"
                  :placeholder="shellText.composerPlaceholder"
                  :disabled="sending || generatingDocuments || switchingSession"
                  class="composer-input"
                  @keydown.enter.exact.prevent="sendMessage"
                  @keydown.enter.shift.prevent="insertLineBreak"
                  @input="autoResizeTextarea"
                  ref="textareaRef"
                />

                <div class="composer-actions">
                  <button
                    class="btn btn-icon composer-attach"
                    type="button"
                    :title="uploadingAttachment ? t.uploadingAttachment : t.attachFile"
                    :aria-label="uploadingAttachment ? t.uploadingAttachment : t.attachFile"
                    :disabled="uploadingAttachment || sending || generatingDocuments || switchingSession"
                    @click="openAttachmentPicker"
                  >
                    <svg v-if="!uploadingAttachment" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21.4 11.6 12 21a6 6 0 0 1-8.5-8.5l9.9-9.9a4 4 0 0 1 5.7 5.7l-10 10a2 2 0 0 1-2.8-2.8l9.4-9.4"/>
                    </svg>
                    <svg v-else class="composer-send-spinner" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-opacity="0.28" stroke-width="2.4"/>
                      <path d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>
                    </svg>
                  </button>
                  <button
                    class="btn btn-icon composer-mic"
                    type="button"
                    :class="{ recording: recording }"
                    :title="recording ? t.stopRecording : t.startRecording"
                    :disabled="sending || generatingDocuments || switchingSession"
                    @click="recording ? stopRecording() : startRecording()"
                  >
                    <svg v-if="!recording" class="icon-mic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                      <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                      <line x1="12" y1="19" x2="12" y2="23"/>
                      <line x1="8" y1="23" x2="16" y2="23"/>
                    </svg>
                    <svg v-else class="icon-stop" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="6" width="12" height="12" rx="2"/>
                    </svg>
                  </button>

                  <button
                    class="composer-send"
                    type="submit"
                    :aria-label="sending ? t.sending : t.send"
                    :title="sending ? t.sending : t.send"
                    :disabled="!canSendComposerMessage"
                  >
                    <svg v-if="!sending" class="btn-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                      <path d="M12 5v14"/>
                      <path d="M6.5 10.5 12 5l5.5 5.5"/>
                    </svg>
                    <svg v-else class="composer-send-spinner" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-opacity="0.28" stroke-width="2.4"/>
                      <path d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>
                    </svg>
                  </button>
                </div>
              </form>

              <div class="composer-footnote">
                <span>{{ shellText.footerNotice }}</span>
                <span>{{ shellText.footerBrand }}</span>
              </div>
            </div>
          </section>

          <aside class="workspace-side">
            <div class="workspace-side-scroll">
              <StructuredRequirementPanel
                :language="currentLanguage"
                :model="structuredRequirementModel"
                :loading="loadingStructuredRequirement"
                :syncing="syncingStructuredRequirement"
                :generating-documents="generatingDocuments"
                :opening-go-coding="openingGoCoding"
                :generation-disabled="messagePipelineActive || switchingSession || documentGenerationConfirmOpen || !hasSession || !structuredRequirementProgress.readyToGenerate"
                :has-prd-document="Boolean(latestPrdDocument)"
                :has-design-document="Boolean(latestDesignDocument)"
                :error="structuredRequirementError"
                @generate-documents="generateDocuments"
                @go-coding="openGoCoding"
              />
            </div>
          </aside>
        </div>

        <div v-else class="main-stage template-stage">
          <section class="template-page-shell">
            <header class="template-page-hero">
              <div class="template-page-hero-copy">
                <p class="template-page-kicker">{{ templateCountLabel }}</p>
                <h1>{{ t.templateLibrary }}</h1>
                <p>{{ t.templateLibraryHint }}</p>
              </div>
            </header>

            <div v-if="loadingTemplates" class="template-page-state">
              {{ t.templateLibraryLoading }}
            </div>
            <div v-else-if="localizedBusinessTemplates.length" class="template-page-grid">
              <article v-for="templateItem in localizedBusinessTemplates" :key="templateItem.template_id" class="template-page-card">
                <div class="template-page-card-head">
                  <div class="template-page-card-heading">
                    <p class="template-page-card-eyebrow">
                      {{ formatTemplateFacet(templateItem.business_domain || templateItem.template_category) }}
                    </p>
                    <h3>{{ templateItem.template_name }}</h3>
                  </div>
                  <button
                    class="btn btn-secondary template-page-detail-btn template-page-card-detail-btn"
                    type="button"
                    :disabled="loadingSession || messagePipelineActive || generatingDocuments || Boolean(applyingTemplateId)"
                    @click="openBusinessTemplate(templateItem.template_id)"
                  >
                    {{ t.templateOpen }}
                  </button>
                </div>

                <p class="template-page-card-description">
                  {{ templateItem.description || t.templateLibraryHint }}
                </p>

                <div v-if="templateItem.tags.length" class="template-page-tags">
                  <span v-for="tag in templateItem.tags.slice(0, 4)" :key="tag" class="template-page-tag">{{ formatTemplateTag(tag) }}</span>
                </div>

                <div v-if="templateItem.section_titles.length" class="template-page-sections">
                  <span
                    v-for="sectionTitle in templateItem.section_titles.slice(0, 4)"
                    :key="sectionTitle"
                    class="template-page-section-pill"
                  >
                    {{ sectionTitle }}
                  </span>
                </div>

                <div class="template-page-card-actions">
                  <button
                    class="btn template-page-apply-btn"
                    type="button"
                    :disabled="loadingSession || messagePipelineActive || generatingDocuments || Boolean(applyingTemplateId)"
                    @click="launchBusinessTemplateSession(templateItem.template_id, { startMode: 'guided' })"
                  >
                    {{ applyingTemplateId === templateItem.template_id ? t.creating : t.templateApplyGuided }}
                  </button>
                  <button
                    v-if="templateItem.has_example_model"
                    class="btn template-page-apply-btn"
                    type="button"
                    :disabled="loadingSession || messagePipelineActive || generatingDocuments || Boolean(applyingTemplateId)"
                    @click="launchBusinessTemplateSession(templateItem.template_id, { startMode: 'example' })"
                  >
                    {{ applyingTemplateId === templateItem.template_id ? t.creating : t.templateApplyExample }}
                  </button>
                </div>
              </article>
            </div>
            <div v-else class="template-page-state">
              {{ t.templateLibraryEmpty }}
            </div>
          </section>
        </div>
      </section>
    </main>

    <div v-if="newChatChooserOpen" class="template-dialog-backdrop" @click.self="closeNewChatChooser">
      <div class="template-dialog new-chat-dialog" role="dialog" aria-modal="true" :aria-label="t.newChatStartTitle">
        <div class="template-dialog-head">
          <div>
            <p class="template-dialog-eyebrow">{{ t.newChat }}</p>
            <h3>{{ t.newChatStartTitle }}</h3>
          </div>
          <button class="template-dialog-close" type="button" :aria-label="t.close" @click="closeNewChatChooser">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="template-dialog-body new-chat-dialog-body">
          <p class="new-chat-dialog-intro">{{ t.newChatStartSubtitle }}</p>

          <div class="new-chat-start-grid">
            <button class="new-chat-start-card" type="button" :disabled="newChatActionDisabled" @click="startGeneralNewChat">
              <span class="new-chat-start-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H8l-5 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </span>
              <span>
                <strong>{{ t.newChatGeneralTitle }}</strong>
                <small>{{ t.newChatGeneralDesc }}</small>
              </span>
            </button>

            <button
              class="new-chat-start-card emphasized"
              type="button"
              :disabled="newChatActionDisabled || loadingTemplates"
              @click="startIcSubstrateNewChat()"
            >
              <span class="new-chat-start-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 6h16"/>
                  <path d="M4 12h16"/>
                  <path d="M4 18h10"/>
                </svg>
              </span>
              <span>
                <strong>{{ t.newChatIcSubstrateTitle }}</strong>
                <small>{{ t.newChatIcSubstrateDesc }}</small>
              </span>
            </button>
          </div>

          <div class="new-chat-department-picker">
            <p>{{ t.newChatChooseDepartment }}</p>
            <div class="new-chat-department-grid">
              <button
                v-for="department in icSubstrateStartDepartments"
                :key="department"
                type="button"
                :disabled="newChatActionDisabled || loadingTemplates"
                @click="startIcSubstrateNewChat(department)"
              >
                {{ department }}
              </button>
            </div>
          </div>
        </div>

        <div class="template-dialog-actions">
          <button class="btn btn-secondary" type="button" @click="closeNewChatChooser">
            {{ t.templateCancel }}
          </button>
          <button class="btn btn-secondary" type="button" @click="openTemplateLibraryFromNewChatChooser">
            {{ t.newChatTemplateLibrary }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="templateDialogOpen" class="template-dialog-backdrop" @click.self="closeBusinessTemplateDialog">
      <div class="template-dialog" role="dialog" aria-modal="true" :aria-label="t.templateDetail">
        <div class="template-dialog-head">
          <div>
            <p class="template-dialog-eyebrow">{{ t.templateLibrary }}</p>
            <h3>{{ selectedBusinessTemplate?.template_name || t.templateDetail }}</h3>
          </div>
          <button class="template-dialog-close" type="button" :aria-label="t.close" @click="closeBusinessTemplateDialog">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div v-if="loadingTemplateDetail" class="template-dialog-state">
          {{ t.templateLibraryLoading }}
        </div>
        <div v-else-if="templateDialogError" class="template-dialog-state error">
          {{ templateDialogError }}
        </div>
        <div v-else-if="selectedBusinessTemplate" class="template-dialog-body template-markdown-dialog-body">
          <div v-if="selectedBusinessTemplate.tags.length" class="template-dialog-tags compact">
            <span v-for="tag in selectedBusinessTemplate.tags" :key="tag" class="template-dialog-tag">{{ formatTemplateTag(tag) }}</span>
          </div>

          <MarkdownRenderer
            v-if="selectedBusinessTemplate.template_markdown"
            class="template-markdown-preview"
            :source="selectedBusinessTemplate.template_markdown"
          />

          <div v-else class="template-dialog-state">
            {{ selectedBusinessTemplate.description }}
          </div>

          <div class="template-dialog-note">
            <p>{{ t.templateApplyHint }}</p>
            <p>{{ t.templatePromptManagedHint }}</p>
          </div>
        </div>

        <div class="template-dialog-actions">
          <button class="btn btn-secondary" type="button" :disabled="Boolean(applyingTemplateId)" @click="closeBusinessTemplateDialog">
            {{ t.templateCancel }}
          </button>
          <button class="btn btn-primary" type="button" :disabled="loadingTemplateDetail || Boolean(applyingTemplateId) || !selectedBusinessTemplate" @click="applyBusinessTemplate">
            {{ applyingTemplateId ? t.creating : t.templateApplyGuided }}
          </button>
          <button
            v-if="selectedBusinessTemplate?.has_example_model"
            class="btn btn-primary"
            type="button"
            :disabled="loadingTemplateDetail || Boolean(applyingTemplateId) || !selectedBusinessTemplate"
            @click="applyBusinessTemplateExample"
          >
            {{ applyingTemplateId ? t.creating : t.templateApplyExample }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="deleteSessionConfirmOpen"
      class="template-dialog-backdrop"
      @click.self="resolveDeleteSessionConfirm(false)"
    >
      <div class="template-dialog document-confirm-dialog" role="dialog" aria-modal="true" aria-label="AIPM">
        <div class="template-dialog-head">
          <div>
            <p class="template-dialog-eyebrow">{{ t.deleteSession }}</p>
            <h3>AIPM</h3>
          </div>
          <button
            class="template-dialog-close"
            type="button"
            :aria-label="t.close"
            @click="resolveDeleteSessionConfirm(false)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="template-dialog-body">
          <p class="document-confirm-message">{{ t.deleteSessionConfirm }}</p>
        </div>

        <div class="template-dialog-actions">
          <button class="btn btn-secondary" type="button" @click="resolveDeleteSessionConfirm(false)">
            {{ t.templateCancel }}
          </button>
          <button class="btn btn-danger" type="button" @click="resolveDeleteSessionConfirm(true)">
            {{ t.delete }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="documentGenerationConfirmOpen"
      class="template-dialog-backdrop"
      @click.self="resolveDocumentGenerationConfirm(false)"
    >
      <div class="template-dialog document-confirm-dialog" role="dialog" aria-modal="true" aria-label="AIPM">
        <div class="template-dialog-head">
          <div>
            <p class="template-dialog-eyebrow">{{ t.generatePrd }}</p>
            <h3>AIPM</h3>
          </div>
          <button
            class="template-dialog-close"
            type="button"
            :aria-label="t.close"
            @click="resolveDocumentGenerationConfirm(false)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="template-dialog-body">
          <p class="document-confirm-message">{{ documentGenerationConfirmMessage }}</p>
        </div>

        <div class="template-dialog-actions">
          <button class="btn btn-secondary" type="button" @click="resolveDocumentGenerationConfirm(false)">
            {{ t.templateCancel }}
          </button>
          <button
            v-if="structuredRequirementProgress.readyToGenerate"
            class="btn btn-primary"
            type="button"
            @click="resolveDocumentGenerationConfirm(true)"
          >
            {{ t.generatePrd }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="previewPanelOpen" class="template-dialog-backdrop" @click.self="closePreviewPanel">
      <div class="template-dialog preview-dialog" role="dialog" aria-modal="true" :aria-label="previewDialogCopy.title">
        <div class="template-dialog-head">
          <div>
            <p class="template-dialog-eyebrow">{{ previewDialogCopy.eyebrow }}</p>
            <h3>{{ previewDialogCopy.title }}</h3>
          </div>
          <button class="template-dialog-close" type="button" :aria-label="t.close" @click="closePreviewPanel">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div class="template-dialog-body preview-dialog-body">
          <p class="preview-dialog-description">{{ previewDialogCopy.description }}</p>
          <RequirementMarkdownPreview
            class="preview-dialog-panel"
            :language="currentLanguage"
            :model="structuredRequirementModel"
            :loading="loadingStructuredRequirement"
            :syncing="syncingStructuredRequirement"
            :error="structuredRequirementError"
          />
        </div>

        <div class="template-dialog-actions">
          <button class="btn btn-secondary" type="button" @click="closePreviewPanel">
            {{ t.close }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
:root {
  --page-bg: #f6f8fb;
  --panel: #ffffff;
  --panel-strong: #ffffff;
  --panel-soft: #f0f6ff;
  --sidebar-bg: #eef2f4;
  --ink: #17202a;
  --muted: #647280;
  --line: #d9e1e7;
  --line-strong: rgba(17, 19, 21, 0.28);
  --accent: #2563eb;
  --accent-strong: #1d4ed8;
  --accent-soft: #e8f1ff;
  --brand-dark: #17202a;
  --brand-light: #2563eb;
  --warn: #c2413b;
  --radius-lg: 8px;
  --radius-md: 8px;
  --radius-sm: 6px;
  --shadow: 0 14px 34px rgba(38, 55, 70, 0.1);
  --shadow-soft: 0 8px 22px rgba(38, 55, 70, 0.08);
  --font: "Plus Jakarta Sans", "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --mono: "SFMono-Regular", Consolas, "Liberation Mono", monospace;

  font-family: var(--font);
  color: var(--ink);
  background: var(--page-bg);
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

html,
body,
#app {
  height: 100%;
}

body {
  margin: 0;
  background: var(--page-bg);
}

* {
  box-sizing: border-box;
}

.app-shell {
  min-height: 100dvh;
  height: 100dvh;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 1px solid #f0c6c6;
  background: #fff4f4;
  color: #9a3434;
  box-shadow: var(--shadow-soft);
  cursor: pointer;
}

.error-icon,
.close-btn svg {
  width: 16px;
  height: 16px;
}

.close-btn {
  margin-left: auto;
  border: 0;
  background: transparent;
  color: inherit;
  opacity: 0.78;
  cursor: pointer;
}

.layout {
  flex: 1 1 auto;
  height: 100%;
  width: 100%;
  margin: 0;
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-columns: 272px minmax(0, 1fr);
  gap: 0;
}

.layout.sidebar-collapsed {
  grid-template-columns: 92px minmax(0, 1fr);
}

.sidebar {
  height: 100%;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 16px;
  border-radius: 0;
  background-color: #0a2a55;
  background-image: url('./sidebar_circuit_background.svg');
  background-position: left center;
  background-size: cover;
  background-repeat: no-repeat;
  border: 0;
  border-right: 1px solid var(--line);
  box-shadow: none;
}

.sidebar.collapsed {
  padding: 18px 12px;
}

.sidebar-topbar,
.sidebar-identity {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sidebar-identity {
  justify-content: flex-start;
}

.sidebar-toggle,
.template-dialog-close,
.session-card-delete {
  border: 0;
  cursor: pointer;
}

.sidebar-toggle {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--panel-soft);
  color: var(--accent-strong);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 0 1px rgba(220, 229, 243, 0.88);
}

.sidebar-toggle svg {
  width: 18px;
  height: 18px;
}

.sidebar-appmark {
  display: grid;
  gap: 2px;
}

.sidebar-appmark strong {
  font-size: 1.12rem;
  letter-spacing: 0;
}

.sidebar-appmark span {
  font-size: 0.78rem;
  color: var(--muted);
}

.btn:hover:not(:disabled),
.composer-send:hover:not(:disabled) {
  transform: translateY(-1px);
}

.btn:disabled,
.composer-send:disabled,
.template-chip:disabled,
.template-library-item:disabled {
  opacity: 0.58;
  cursor: not-allowed;
  transform: none;
}

.sidebar-body {
  min-height: 0;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  gap: 14px;
}

.sidebar-nav {
  display: grid;
  gap: 8px;
}

.sidebar-nav-item {
  min-height: 56px;
  border: 0;
  border-radius: var(--radius-md);
  padding: 10px 14px;
  background: transparent;
  color: var(--muted);
  text-align: left;
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  align-items: center;
  column-gap: 12px;
  cursor: pointer;
  box-shadow: none;
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.sidebar-nav-item:hover {
  background: var(--panel-strong);
  color: var(--ink);
}

.sidebar-nav-item.active {
  background: var(--accent-soft);
  color: var(--accent-strong);
  box-shadow: none;
}

.sidebar-nav-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.sidebar-nav-icon svg {
  width: 18px;
  height: 18px;
}

.sidebar-nav-text {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.sidebar-nav-text strong {
  font-size: 0.92rem;
  font-weight: 760;
}

.sidebar-nav-text small {
  display: block;
  min-width: 0;
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.3;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.sidebar-nav-item.active .sidebar-nav-text small {
  color: #4a71c5;
}

.sidebar-menu-scroll {
  min-height: 0;
  overflow: auto;
  display: grid;
  align-content: start;
  gap: 18px;
  padding-right: 4px;
}

.sidebar-new-chat {
  width: 100%;
  min-height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: var(--radius-md);
  padding: 0 14px;
  background: linear-gradient(135deg, #f8fbff 0%, #dbeafe 100%);
  color: #123b7a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  font-size: 0.9rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(4, 21, 49, 0.22);
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.sidebar-new-chat:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #ffffff;
  box-shadow: 0 14px 28px rgba(4, 21, 49, 0.28);
}

.sidebar-new-chat:disabled {
  opacity: 0.62;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.sidebar-new-chat-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent);
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.sidebar-new-chat-icon svg {
  width: 14px;
  height: 14px;
}

.sidebar.collapsed .sidebar-new-chat {
  width: 48px;
  height: 48px;
  min-height: 48px;
  justify-self: center;
  padding: 0;
  border-radius: var(--radius-md);
}

.sidebar.collapsed .sidebar-new-chat > span:not(.sidebar-new-chat-icon) {
  display: none;
}

.sidebar-block {
  min-height: 0;
  display: grid;
  gap: 10px;
}

.sidebar-template-block {
  align-content: start;
}

.sidebar-history-block {
  min-height: 0;
}

.sidebar-block-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  padding: 0 6px;
}

.sidebar-block-head h2 {
  margin: 0;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6b7b97;
}

.sidebar-block-head span {
  color: var(--muted);
  font-size: 0.7rem;
  white-space: nowrap;
}

.template-library-list,
.session-history-list {
  min-height: 0;
  display: grid;
  gap: 6px;
}

.session-history-list {
  overflow: visible;
  padding-right: 0;
}

.session-history-placeholder {
  padding: 12px 14px;
  border-radius: var(--radius-md);
  border: 1px dashed var(--line);
  background: rgba(255, 255, 255, 0.42);
  color: var(--muted);
  line-height: 1.5;
  font-size: 0.78rem;
}

.template-library-item,
.session-card {
  width: 100%;
  border-radius: var(--radius-md);
  background: transparent;
  border: 0;
  box-shadow: none;
}

.template-library-item {
  padding: 10px 12px;
  text-align: left;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: start;
  gap: 10px;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
  border-radius: var(--radius-md);
}

.template-library-item:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.72);
}

.template-library-item-main {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.template-library-item-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: baseline;
}

.template-library-item-title,
.session-card-title {
  font-weight: 700;
  color: var(--ink);
}

.template-library-item-title {
  min-width: 0;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  font-size: 0.88rem;
}

.template-library-item-count,
.session-card-time {
  color: var(--muted);
  font-size: 0.72rem;
}

.template-library-item-meta,
.session-card-preview {
  margin: 0;
  color: var(--muted);
  font-size: 0.76rem;
  line-height: 1.4;
}

.session-card-preview {
  width: 100%;
  max-width: 100%;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: normal;
}

.session-card {
  position: relative;
  display: block;
  padding: 0;
  transition: background 0.2s ease, color 0.2s ease;
  border-radius: var(--radius-md);
}

.session-card.active {
  background: var(--accent-soft);
}

.session-card-main {
  width: 100%;
  max-width: 100%;
  border: 0;
  background: transparent;
  padding: 10px 46px 10px 12px;
  text-align: left;
  color: inherit;
  cursor: pointer;
  min-width: 0;
  justify-self: stretch;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  align-items: start;
}

.session-card-copy {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  display: grid;
  gap: 4px;
}

.session-card-top {
  width: 100%;
  max-width: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-items: start;
  gap: 2px;
}

.session-card-title {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  font-size: 0.86rem;
  line-height: 1.3;
  display: block;
  max-height: 2.6em;
  overflow: hidden;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: normal;
}

.session-card-time {
  justify-self: start;
  white-space: nowrap;
}

.session-card-template {
  margin: 2px 0 0;
  color: #295bbc;
  font-size: 0.72rem;
  font-weight: 700;
}

.session-card-delete {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  margin: 0;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: none;
}

.session-card-delete:hover:not(:disabled) {
  color: var(--warn);
  background: rgba(255, 242, 242, 0.9);
}

.session-card-delete-icon {
  width: 14px;
  height: 14px;
}

.menu-entry-accent {
  width: 4px;
  height: 100%;
  min-height: 34px;
  border-radius: 999px;
  background: rgba(95, 139, 240, 0.28);
}

.menu-entry-accent.template {
  background: var(--accent);
}

.menu-entry-accent.recent {
  background: var(--accent);
}

.main-shell {
  height: 100%;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 14px 14px 0;
  border-radius: 0;
  background: var(--panel);
  border: 0;
  box-shadow: none;
  overflow: hidden;
}

.main-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background-color: #061b36;
  background-image: url('./topbar_circuit_background.svg');
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  border: 1px solid rgba(102, 178, 255, 0.24);
  border-radius: 0;
  backdrop-filter: blur(18px);
}

.main-topbar-actions {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 0;
}

.ats-lockup {
  display: inline-flex;
  align-items: center;
  overflow: hidden;
  border-radius: var(--radius-md);
  box-shadow: 0 10px 22px rgba(38, 55, 70, 0.08);
}

.ats-lockup-logo {
  display: block;
  width: 236px;
  height: auto;
  max-height: 50px;
}

.ats-lockup-segment {
  min-width: 108px;
  padding: 10px 14px;
  color: #fff;
  font-size: 0.92rem;
  font-weight: 800;
  letter-spacing: 0;
}

.ats-lockup-segment.dark {
  background: var(--brand-dark);
}

.ats-lockup-segment.light {
  background: var(--brand-light);
}

.language-switcher {
  position: relative;
}

.language-switcher summary {
  min-width: 184px;
  list-style: none;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 16px;
  border-radius: var(--radius-md);
  background: rgba(6, 24, 50, 0.84);
  color: rgba(246, 251, 255, 0.96);
  cursor: pointer;
  outline: none;
  box-shadow: inset 0 0 0 1px rgba(142, 210, 255, 0.26), 0 8px 18px rgba(0, 10, 24, 0.18);
  transition: background 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
}

.language-switcher summary::-webkit-details-marker {
  display: none;
}

.language-switcher-label {
  color: rgba(205, 229, 248, 0.72);
  font-size: 0.82rem;
}

.language-switcher-value {
  font-size: 0.9rem;
  font-weight: 700;
}

.language-switcher summary svg {
  width: 14px;
  height: 14px;
  color: var(--muted);
  transition: transform 0.18s ease, color 0.18s ease;
}

.language-switcher[open] summary {
  background: #fff;
  color: var(--accent-strong);
  box-shadow: inset 0 0 0 1px rgba(95, 139, 240, 0.38), 0 12px 24px rgba(43, 76, 128, 0.1);
}

.language-switcher[open] summary svg {
  color: var(--accent-strong);
  transform: rotate(180deg);
}

.language-switcher summary:focus-visible {
  box-shadow: inset 0 0 0 1px rgba(95, 139, 240, 0.5), 0 0 0 3px rgba(95, 139, 240, 0.16);
}

.language-switcher-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  z-index: 10;
  min-width: 100%;
  padding: 8px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid var(--line);
  box-shadow: 0 18px 38px rgba(43, 76, 128, 0.16);
  display: grid;
  gap: 4px;
}

.language-switcher-option {
  border: 0;
  border-radius: 10px;
  padding: 10px 12px;
  background: transparent;
  text-align: left;
  color: var(--ink);
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.language-switcher-option.active,
.language-switcher-option:hover {
  background: rgba(232, 240, 255, 0.9);
  color: var(--accent-strong);
  box-shadow: inset 0 0 0 1px rgba(95, 139, 240, 0.16);
}

.main-stage {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(258px, 286px);
  gap: 12px;
}

.template-stage {
  grid-template-columns: minmax(0, 1fr);
}

.conversation-shell {
  height: 100%;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  overflow: hidden;
}

.template-page-shell {
  min-height: 0;
  width: 100%;
  margin: 0;
  display: grid;
  align-content: start;
  gap: 18px;
  overflow: auto;
  padding: 4px 6px 4px 0;
}

.template-page-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
}

.template-page-kicker {
  margin: 0 0 10px;
  color: var(--accent-strong);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.template-page-hero-copy h1 {
  margin: 0;
  font-size: clamp(2.1rem, 3.6vw, 3.4rem);
  line-height: 0.98;
  letter-spacing: 0;
}

.template-page-hero-copy p:last-child {
  margin: 10px 0 0;
  max-width: 760px;
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.58;
}

.template-page-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.template-page-card {
  display: grid;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.94);
  box-shadow: var(--shadow-soft);
}

.template-page-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.template-page-card-heading {
  min-width: 0;
  display: grid;
  gap: 6px;
}

.template-page-card-eyebrow {
  margin: 0;
  color: var(--accent-strong);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.template-page-card-heading h3 {
  margin: 0;
  font-size: 1.08rem;
  line-height: 1.3;
}

.template-page-card-count {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  background: #eef3ff;
  color: #4b6ba4;
  font-size: 0.76rem;
  font-weight: 700;
  white-space: nowrap;
}

.template-page-card-description {
  margin: 0;
  color: #42536c;
  line-height: 1.58;
  font-size: 0.9rem;
}

.template-page-tags,
.template-page-sections {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-page-tag,
.template-page-section-pill {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 11px;
  border-radius: 999px;
  font-size: 0.76rem;
  line-height: 1;
}

.template-page-tag {
  background: #eef4ff;
  color: #4b6ba4;
  font-weight: 700;
}

.template-page-section-pill {
  background: #f7faff;
  color: #5d6f8d;
  border: 1px solid #dce6f7;
}

.template-page-card-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-top: auto;
}

.template-page-detail-btn,
.template-page-apply-btn {
  justify-content: center;
}

.template-page-card-detail-btn {
  flex: 0 0 auto;
  min-height: 32px;
  padding: 0 12px;
  font-size: 0.78rem;
  white-space: nowrap;
}

.template-page-state {
  padding: 18px 20px;
  border-radius: var(--radius-md);
  border: 1px dashed var(--line);
  background: rgba(255, 255, 255, 0.72);
  color: var(--muted);
  line-height: 1.6;
}

.conversation-shell.has-messages {
  justify-content: flex-start;
}

.welcome-stage {
  flex: 1 1 auto;
  width: 100%;
  margin: 0;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 26px;
  padding: 8px 10px;
  overflow: auto;
}

.welcome-kicker {
  margin: 0 0 12px;
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.assistant-prompt {
  display: grid;
  grid-template-columns: auto 1fr;
  align-items: center;
  gap: 14px;
  max-width: 820px;
  padding: 16px 20px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(220, 229, 243, 0.95);
  box-shadow: var(--shadow-soft);
}

.assistant-prompt-badge {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.assistant-prompt p {
  margin: 0;
  font-size: 0.98rem;
  line-height: 1.52;
}

.chat-stream-shell {
  flex: 1 1 auto;
  width: 100%;
  margin: 0;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.conversation-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.conversation-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.conversation-title-wrap h2 {
  margin: 0;
  font-size: 1.36rem;
  letter-spacing: 0;
}

.conversation-chip {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: #eef3ff;
  color: #4b6ba4;
  font-size: 0.78rem;
  font-weight: 700;
}

.conversation-chip.accent {
  background: rgba(65, 117, 234, 0.12);
  color: var(--accent-strong);
}

.chat-list,
.workspace-side-scroll,
.template-page-shell,
.sidebar-menu-scroll,
.session-history-list {
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(117, 136, 173, 0.55) transparent;
}

.chat-list::-webkit-scrollbar,
.workspace-side-scroll::-webkit-scrollbar,
.template-page-shell::-webkit-scrollbar,
.sidebar-menu-scroll::-webkit-scrollbar,
.session-history-list::-webkit-scrollbar {
  width: 8px;
}

.chat-list::-webkit-scrollbar-thumb,
.workspace-side-scroll::-webkit-scrollbar-thumb,
.template-page-shell::-webkit-scrollbar-thumb,
.sidebar-menu-scroll::-webkit-scrollbar-thumb,
.session-history-list::-webkit-scrollbar-thumb {
  background: rgba(117, 136, 173, 0.45);
  border-radius: 999px;
}

.chat-list {
  flex: 1 1 auto;
  min-height: 0;
  padding: 6px 6px 6px 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: auto;
}

.bubble {
  width: min(100%, 920px);
  padding: 18px 22px;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-soft);
}

.bubble.user {
  width: fit-content;
  max-width: min(78%, 760px);
  min-width: min(100%, 260px);
  align-self: flex-end;
  margin-left: auto;
  background: var(--accent);
  border-color: rgba(47, 101, 216, 0.5);
  border-top-right-radius: 10px;
  color: #fff;
  box-shadow: 0 18px 34px rgba(47, 101, 216, 0.22);
}

.bubble.assistant {
  align-self: flex-start;
  background: #ffffff;
  border-color: #d9e5f5;
  border-left: 4px solid var(--accent);
  border-top-left-radius: 10px;
}

.bubble.design-doc-bubble {
  width: 100%;
}

.message-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.role {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 9px;
  border-radius: 999px;
  background: #eef3ff;
  font-size: 0.82rem;
  font-weight: 700;
  color: #486486;
}

.bubble.user .role {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.bubble.assistant .role {
  background: rgba(37, 99, 235, 0.12);
  color: #173f9f;
}

.timestamp {
  color: var(--muted);
  font-size: 0.74rem;
}

.bubble.user .timestamp {
  color: rgba(255, 255, 255, 0.72);
}

.content,
.think-content,
.design-doc-content {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.6;
}

.bubble.user .content {
  color: #fff;
}

.bubble.assistant .content {
  color: #2f405d;
}

.design-doc-card {
  display: grid;
  gap: 14px;
}

.design-doc-badge {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  background: #eef3ff;
  color: var(--accent-strong);
  font-size: 0.78rem;
  font-weight: 700;
}

.design-doc-content,
.think-content {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid #e2e8f5;
  background: #f7faff;
  font-size: 0.84rem;
}

.think-content {
  font-family: var(--mono);
}

.design-doc-content {
  white-space: normal;
}

.streaming-doc-content {
  max-height: 56vh;
  overflow: auto;
  white-space: pre-wrap;
  font-family: var(--mono);
}

.design-doc-footer {
  display: flex;
  justify-content: flex-end;
}

.think-box {
  margin-bottom: 12px;
}

.think-box-summary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.82rem;
}

.think-icon {
  width: 16px;
  height: 16px;
}

.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: typingBounce 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

.composer-zone {
  flex: 0 0 auto;
  width: 100%;
  margin: 0;
  min-width: 0;
  display: grid;
  gap: 12px;
}

.composer-context {
  display: grid;
  gap: 10px;
}

.composer-context-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.composer-context-row.template-driven {
  justify-content: space-between;
}

.conversation-chain-status {
  min-width: 0;
  max-width: 100%;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex: 1 1 auto;
  color: #35506f;
  font-size: 0.8rem;
  line-height: 1.35;
}

.conversation-chain-mode,
.conversation-chain-progress,
.conversation-chain-state {
  flex: 0 0 auto;
  border: 1px solid rgba(37, 99, 235, 0.14);
  border-radius: 999px;
  padding: 5px 9px;
  background: rgba(244, 248, 255, 0.9);
  color: #365988;
  font-weight: 800;
}

.conversation-chain-node {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 700;
}

.conversation-chain-state {
  background: #ffffff;
  color: #66758b;
}

.template-picker-options {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1 1 auto;
}

.composer-context-actions,
.composer-document-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.composer-context-actions {
  justify-content: flex-end;
  flex: 0 0 auto;
}

.composer-document-download-btn {
  min-height: 38px;
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 999px;
  padding: 0 12px;
  background: #ffffff;
  color: var(--accent-strong);
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-shrink: 0;
  white-space: nowrap;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.composer-document-download-btn svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
}

.composer-document-download-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: #bfd2f7;
  color: var(--accent-strong);
  box-shadow: 0 10px 18px rgba(74, 104, 157, 0.12);
}

.composer-document-download-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.preview-toggle-btn {
  min-height: 38px;
  border: 1px solid #d7e1f3;
  border-radius: 999px;
  padding: 0 16px;
  background: rgba(255, 255, 255, 0.9);
  color: #365988;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  white-space: nowrap;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.preview-toggle-btn:hover {
  transform: translateY(-1px);
  border-color: #bfd2f7;
  color: var(--accent-strong);
  box-shadow: 0 10px 18px rgba(74, 104, 157, 0.12);
}

.template-chip {
  min-height: 36px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.75);
  color: var(--muted);
  font-weight: 700;
  cursor: pointer;
}

.template-chip.active {
  background: var(--accent-soft);
  border-color: #bfd2f7;
  color: var(--accent-strong);
}

.template-picker-hint {
  margin: 0;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.55;
}

.composer-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: flex-end;
  gap: 16px;
  padding: 18px 20px 18px 22px;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: var(--shadow);
}

.composer-file-input {
  display: none;
}

.composer-attachment-chip {
  grid-column: 1 / -1;
  width: 100%;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #d8e3f7;
  border-radius: var(--radius-md);
  background: #f7faff;
}

.composer-attachment-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #eaf1ff;
  color: var(--accent);
}

.composer-attachment-icon svg,
.composer-attachment-remove svg {
  width: 17px;
  height: 17px;
}

.composer-attachment-copy {
  min-width: 0;
  display: grid;
  gap: 2px;
}

.composer-attachment-copy strong,
.composer-attachment-copy small {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.composer-attachment-copy strong {
  color: var(--ink);
  font-size: 0.9rem;
}

.composer-attachment-copy small {
  color: var(--muted);
  font-size: 0.76rem;
}

.composer-attachment-remove {
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #71809a;
  cursor: pointer;
}

.composer-attachment-remove:hover {
  background: #eaf1ff;
  color: var(--accent);
}

.composer-input {
  width: 100%;
  min-height: 84px;
  max-height: 220px;
  border: 0;
  background: transparent;
  resize: none;
  color: var(--ink);
  font-size: 1rem;
  line-height: 1.6;
  font-family: var(--font);
  overflow-y: hidden;
}

.composer-input:focus {
  outline: none;
}

.composer-input::placeholder {
  color: #9aa5b9;
}

.composer-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn {
  min-height: 44px;
  padding: 0 16px;
  border-radius: var(--radius-md);
  border: 0;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: 0 12px 22px rgba(65, 117, 234, 0.18);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: var(--ink);
  box-shadow: inset 0 0 0 1px rgba(220, 229, 243, 0.92);
}

.btn-danger {
  background: var(--warn);
  box-shadow: 0 12px 22px rgba(194, 65, 59, 0.18);
}

.btn-icon {
  width: 46px;
  min-width: 46px;
  height: 46px;
  padding: 0;
  justify-content: center;
  border-radius: 50%;
  background: #f3f7ff;
  color: var(--accent);
}

.btn-icon.recording {
  background: #fff1f1;
  color: var(--warn);
  box-shadow: 0 0 0 0 rgba(181, 72, 72, 0.4);
  animation: pulse 1.5s infinite;
}

.composer-attach:disabled {
  color: #9aa5b9;
  cursor: not-allowed;
  opacity: 0.72;
}

.composer-send {
  width: 54px;
  height: 54px;
  border: 0;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 16px 28px rgba(65, 117, 234, 0.24);
  cursor: pointer;
}

.btn-icon-svg,
.btn-icon svg,
.composer-send svg {
  width: 18px;
  height: 18px;
}

.composer-footnote {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.32;
  text-align: center;
}

.workspace-side {
  min-width: 0;
  min-height: 0;
}

.workspace-side-scroll {
  height: 100%;
  min-height: 0;
  overflow: auto;
  display: grid;
  align-content: start;
  gap: 12px;
  padding-right: 2px;
}

.template-dialog-backdrop {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(27, 42, 68, 0.34);
  backdrop-filter: blur(8px);
}

.template-dialog {
  width: min(720px, 100%);
  max-height: min(90vh, 920px);
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
  background: #fff;
  box-shadow: 0 30px 80px rgba(36, 55, 96, 0.24);
  overflow: hidden;
}

.document-confirm-dialog {
  width: min(520px, 100%);
}

.new-chat-dialog {
  width: min(780px, 100%);
}

.new-chat-dialog-body {
  display: grid;
  gap: 18px;
}

.new-chat-dialog-intro {
  margin: 0;
  color: #61718a;
  line-height: 1.55;
}

.new-chat-start-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.new-chat-start-card {
  min-height: 118px;
  border: 1px solid #dbe6f7;
  border-radius: var(--radius-md);
  padding: 16px;
  background: #ffffff;
  color: #18345f;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.new-chat-start-card:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: rgba(37, 99, 235, 0.42);
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.14);
}

.new-chat-start-card:disabled,
.new-chat-department-grid button:disabled {
  opacity: 0.58;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.new-chat-start-card.emphasized {
  border-color: rgba(37, 99, 235, 0.36);
  background: #f8fbff;
}

.new-chat-start-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: rgba(37, 99, 235, 0.12);
  color: var(--accent);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.new-chat-start-icon svg {
  width: 19px;
  height: 19px;
}

.new-chat-start-card strong,
.new-chat-start-card small {
  display: block;
}

.new-chat-start-card strong {
  margin-bottom: 6px;
  font-size: 0.98rem;
}

.new-chat-start-card small {
  color: #61718a;
  line-height: 1.45;
}

.new-chat-department-picker {
  display: grid;
  gap: 10px;
}

.new-chat-department-picker p {
  margin: 0;
  color: #3d506e;
  font-weight: 760;
}

.new-chat-department-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.new-chat-department-grid button {
  min-height: 34px;
  border: 1px solid rgba(37, 99, 235, 0.18);
  border-radius: var(--radius-md);
  padding: 0 11px;
  background: #ffffff;
  color: #173f9f;
  font-size: 0.78rem;
  font-weight: 720;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.new-chat-department-grid button:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #eef4ff;
  border-color: rgba(37, 99, 235, 0.38);
}

.template-dialog-head,
.template-dialog-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
}

.template-dialog-head {
  align-items: flex-start;
  border-bottom: 1px solid #edf2fb;
}

.template-dialog-head h3 {
  margin: 6px 0 0;
  font-size: 1.28rem;
}

.template-dialog-eyebrow {
  margin: 0;
  color: var(--accent-strong);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.template-dialog-close {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: #f4f8ff;
  color: var(--muted);
}

.template-dialog-close svg {
  width: 18px;
  height: 18px;
}

.template-dialog-state,
.template-dialog-description,
.template-dialog-body {
  color: #42536c;
}

.template-dialog-state {
  margin: 20px 24px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px dashed var(--line);
  background: #f7faff;
}

.template-dialog-state.error {
  border-style: solid;
  border-color: #f0c6c6;
  background: #fff4f4;
  color: #9a3434;
}

.template-dialog-body {
  overflow: auto;
  padding: 20px 24px;
  display: grid;
  gap: 18px;
}

.template-markdown-dialog-body {
  gap: 14px;
}

.template-dialog-description {
  margin: 0;
  line-height: 1.7;
}

.document-confirm-message {
  margin: 0;
  color: var(--ink);
  line-height: 1.7;
}

.template-dialog-block {
  display: grid;
  gap: 10px;
}

.template-dialog-block h4 {
  margin: 0;
  font-size: 0.95rem;
}

.template-dialog-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-dialog-tags.compact {
  gap: 6px;
}

.template-dialog-tag {
  padding: 7px 12px;
  border-radius: 999px;
  background: #eef4ff;
  color: #4b6ba4;
  font-size: 0.78rem;
  font-weight: 700;
}

.template-markdown-preview {
  padding: 16px 18px;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: #fbfdfe;
  color: var(--ink);
}

.template-dialog-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 8px;
}

.template-dialog-field-count {
  margin-left: 8px;
  color: var(--muted);
  font-size: 0.76rem;
}

.template-dialog-note {
  display: grid;
  gap: 8px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: #f7faff;
  border: 1px solid var(--line);
}

.template-dialog-note p {
  margin: 0;
  line-height: 1.55;
}

.template-dialog-actions {
  justify-content: flex-end;
  border-top: 1px solid #edf2fb;
}

.preview-dialog {
  width: min(1080px, 100%);
  max-height: min(92vh, 980px);
}

.preview-dialog-body {
  overflow: hidden;
  grid-template-rows: auto minmax(0, 1fr);
}

.preview-dialog-description {
  margin: 0;
  color: #61718a;
  line-height: 1.65;
}

.preview-dialog-panel {
  min-height: 0;
  height: 100%;
}

.icon-mic,
.icon-stop {
  width: 20px;
  height: 20px;
}

.composer-send-spinner {
  width: 20px;
  height: 20px;
  animation: spin 0.9s linear infinite;
}

@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(181, 72, 72, 0.4);
  }
  70% {
    box-shadow: 0 0 0 12px rgba(181, 72, 72, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(181, 72, 72, 0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.error-banner,
.sidebar-toggle,
.sidebar-nav-item,
.session-history-placeholder,
.template-library-item,
.session-card,
.language-switcher summary,
.language-switcher-menu,
.language-switcher-option,
.template-page-card,
.template-page-state,
.assistant-prompt,
.conversation-chip,
.bubble,
.role,
.design-doc-badge,
.design-doc-content,
.think-content,
.preview-toggle-btn,
.template-chip,
.composer-card,
.btn,
.template-dialog,
.template-dialog-close,
.template-dialog-state,
.template-dialog-tag,
.template-dialog-note {
  border-radius: var(--radius-md);
}

.template-page-card,
.assistant-prompt,
.bubble,
.composer-card,
.template-dialog,
.language-switcher-menu {
  background: var(--panel);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-soft);
}

.template-page-card,
.assistant-prompt,
.bubble.assistant,
.composer-card {
  background: #ffffff;
}

.bubble.user,
.btn,
.composer-send {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.22);
}

.bubble.user {
  border-top-right-radius: var(--radius-sm);
}

.bubble.assistant {
  border-color: var(--line);
  border-left: 4px solid var(--accent);
  border-top-left-radius: var(--radius-sm);
}

.bubble.assistant .role,
.conversation-chip,
.template-page-card-count,
.template-page-tag,
.design-doc-badge {
  background: rgba(37, 99, 235, 0.12);
  color: #173f9f;
}

.assistant-prompt-badge,
.typing-dot {
  background: var(--accent);
}

.btn:hover:not(:disabled),
.composer-send:hover:not(:disabled) {
  background: var(--accent-strong);
  color: #ffffff;
}

.btn-danger:hover:not(:disabled) {
  background: #a73531;
}

.btn-secondary,
.preview-toggle-btn,
.template-chip {
  background: #ffffff;
  border: 1px solid rgba(37, 99, 235, 0.16);
  color: var(--accent-strong);
  box-shadow: none;
}

.template-chip.active,
.language-switcher-option.active,
.language-switcher-option:hover,
.session-card.active,
.conversation-chip.accent {
  background: var(--accent-soft);
  color: var(--accent-strong);
}

.design-doc-content,
.think-content,
.template-dialog-note {
  background: #fbfdfe;
  border-color: var(--line);
}

.sidebar {
  color: rgba(236, 246, 255, 0.94);
  border-right-color: rgba(102, 178, 255, 0.22);
}

.sidebar-toggle {
  background: rgba(7, 24, 52, 0.82);
  color: #e9f7ff;
  box-shadow: inset 0 0 0 1px rgba(125, 202, 255, 0.24);
}

.sidebar-appmark strong,
.sidebar-nav-text strong,
.template-library-item-title,
.session-card-title {
  color: rgba(248, 252, 255, 0.96);
}

.sidebar-appmark strong {
  text-shadow: 0 1px 8px rgba(0, 10, 24, 0.38);
}

.sidebar .session-card,
.sidebar .template-library-item {
  background: rgba(9, 42, 84, 0.48);
}

.sidebar .session-card-title,
.sidebar .template-library-item-title {
  font-weight: 680;
}

.sidebar-appmark span,
.sidebar-block-head span,
.sidebar-nav-text small,
.template-library-item-count,
.template-library-item-meta,
.session-card-time,
.session-card-preview {
  color: rgba(201, 224, 244, 0.72);
}

.sidebar-block-head h2 {
  color: rgba(158, 215, 255, 0.82);
}

.sidebar-nav-item,
.template-library-item,
.session-card-main {
  color: rgba(229, 244, 255, 0.86);
}

.sidebar-nav-item:hover,
.template-library-item:hover:not(:disabled),
.session-card:hover {
  background: rgba(17, 72, 134, 0.66);
  color: #ffffff;
}

.sidebar-nav-item.active,
.sidebar .session-card.active {
  background: rgba(19, 91, 164, 0.78);
  color: #ffffff;
  box-shadow: inset 0 0 0 1px rgba(122, 199, 255, 0.3);
}

.sidebar-nav-item.active .sidebar-nav-text small,
.sidebar .session-card.active .session-card-preview,
.sidebar .session-card.active .session-card-time {
  color: rgba(221, 241, 255, 0.86);
}

.session-card-template {
  color: rgba(151, 219, 255, 0.86);
}

.session-history-placeholder {
  background: rgba(10, 43, 86, 0.58);
  border-color: rgba(125, 202, 255, 0.2);
  color: rgba(221, 241, 255, 0.74);
}

.session-card-delete {
  color: rgba(221, 241, 255, 0.44);
}

.session-card-delete:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.12);
  color: #ffffff;
}

.menu-entry-accent,
.menu-entry-accent.template,
.menu-entry-accent.recent {
  background: rgba(112, 214, 255, 0.34);
}

.template-page-hero-copy h1,
.conversation-title-wrap h2,
.sidebar-appmark strong,
.ats-lockup-segment,
.template-dialog-head h3 {
  letter-spacing: 0;
}

.template-page-hero-copy h1,
.ats-lockup-segment,
.sidebar-appmark strong {
  font-weight: 800;
}

.main-topbar,
.template-dialog-head,
.template-dialog-actions {
  border-color: var(--line);
}

.template-dialog-state.error,
.error-banner {
  background: rgba(220, 38, 38, 0.13);
  border-color: rgba(220, 38, 38, 0.38);
  color: #991b1b;
}

@media (max-width: 1100px) {
  .main-stage {
    grid-template-columns: minmax(0, 1fr);
  }

  .workspace-side {
    min-height: min(90dvh, 980px);
  }
}

@media (max-height: 860px) {
  .app-shell {
    padding: 0;
    gap: 0;
  }

  .layout {
    gap: 14px;
  }

  .sidebar,
  .sidebar.collapsed {
    gap: 14px;
    padding: 14px;
  }

  .main-shell {
    gap: 14px;
    padding: 12px 12px 0;
  }

  .main-stage {
    gap: 12px;
  }

  .conversation-shell,
  .chat-stream-shell {
    gap: 14px;
  }

  .welcome-stage {
    gap: 18px;
    padding: 4px 8px;
  }

  .welcome-kicker {
    margin-bottom: 8px;
  }

  .assistant-prompt {
    gap: 12px;
    padding: 14px 18px;
  }

  .assistant-prompt-badge {
    width: 38px;
    height: 38px;
  }

  .assistant-prompt p {
    font-size: 0.92rem;
    line-height: 1.46;
  }

  .chat-list {
    gap: 12px;
  }

  .bubble {
    padding: 16px 18px;
  }

  .composer-zone {
    gap: 10px;
  }

  .composer-context {
    gap: 8px;
  }

  .composer-card {
    gap: 14px;
    padding: 14px 18px 14px 20px;
    border-radius: var(--radius-md);
  }

  .composer-input {
    min-height: 64px;
    max-height: 180px;
  }

  .btn-icon {
    width: 42px;
    min-width: 42px;
    height: 42px;
  }

  .composer-send {
    width: 50px;
    height: 50px;
  }

  .workspace-side-scroll {
    gap: 10px;
  }

}

@media (max-width: 1040px) {
  .app-shell {
    height: auto;
    overflow: visible;
  }

  .layout,
  .layout.sidebar-collapsed {
    grid-template-columns: 1fr;
  }

  .sidebar,
  .sidebar.collapsed {
    padding: 16px;
  }

  .sidebar.collapsed .sidebar-body,
  .sidebar.collapsed .sidebar-appmark {
    display: grid;
  }

  .sidebar-body {
    grid-template-rows: auto auto auto;
  }
}

@media (max-width: 768px) {
  .app-shell {
    padding: 0;
  }

  .new-chat-start-grid {
    grid-template-columns: 1fr;
  }

  .main-shell {
    padding: 18px 18px 0;
    border-radius: 0;
  }

  .main-topbar {
    flex-wrap: wrap;
  }

  .ats-lockup-segment {
    min-width: 110px;
  }

  .language-switcher summary {
    min-width: 170px;
  }

  .welcome-stage {
    padding: 8px 0;
  }

  .assistant-prompt {
    grid-template-columns: 1fr;
    justify-items: start;
  }

  .template-page-hero {
    align-items: flex-start;
  }

  .template-page-hero-copy h1 {
    font-size: clamp(1.8rem, 8vw, 2.5rem);
  }

  .template-page-hero-copy p:last-child {
    font-size: 0.92rem;
  }

  .template-page-grid {
    grid-template-columns: 1fr;
  }

  .template-page-card {
    padding: 16px;
  }

  .template-page-card-actions {
    grid-template-columns: 1fr;
  }

  .composer-card {
    grid-template-columns: 1fr;
  }

  .composer-context-row {
    align-items: stretch;
  }

  .composer-context-actions,
  .composer-document-actions {
    width: 100%;
  }

  .composer-context-actions {
    justify-content: stretch;
  }

  .composer-document-download-btn {
    flex: 1 1 140px;
  }

  .composer-actions {
    width: 100%;
    justify-content: space-between;
  }

  .composer-footnote {
    gap: 4px;
  }

  .preview-toggle-btn {
    width: 100%;
    justify-content: center;
  }

  .composer-context-actions .preview-toggle-btn {
    width: auto;
    flex: 1 1 150px;
  }

  .bubble {
    width: 100%;
  }

  .template-dialog-backdrop {
    padding: 10px;
  }

  .preview-dialog {
    max-height: min(94vh, 860px);
  }

  .template-dialog-actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .template-dialog-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
