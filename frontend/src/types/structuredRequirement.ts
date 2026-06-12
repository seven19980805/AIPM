export type StructuredRequirementFeature = {
  feature_name: string
  description: string
  trigger: string
  processing_logic: string
  inputs: string[]
  outputs: string[]
  exception_cases: string[]
}

export type StructuredRequirementPage = {
  page_name: string
  entry_point: string
  page_elements: string[]
  button_actions: string[]
}

export type RequirementCollectionStatus =
  | 'missing'
  | 'captured'
  | 'pending_confirmation'
  | 'confirmed'
  | 'conflict'

export type RequirementCollectionItem = {
  status: RequirementCollectionStatus
  reason: string
  pending_questions: string[]
}

export type StructuredRequirementCollectionStatus = {
  objective: RequirementCollectionItem
  scope: RequirementCollectionItem
  users: RequirementCollectionItem
  scenarios: RequirementCollectionItem
  features: RequirementCollectionItem
  pages: RequirementCollectionItem
  rules: RequirementCollectionItem
  integrations: RequirementCollectionItem
  acceptance: RequirementCollectionItem
}

export type StructuredRequirementModel = {
  document_info: {
    project_name: string
    requirement_name: string
  }
  product_context: {
    requesting_department: string
    business_owner: string
    software_type: string
    primary_user: string
    decision_or_action: string
    acceptance_owner: string
  }
  background: {
    summary: string
    objective: string
  }
  scope: {
    in_scope: string[]
    out_of_scope: string[]
  }
  users_and_scenarios: {
    target_users: string[]
    core_scenarios: string[]
  }
  functional_requirements: {
    overview: string
    feature_details: StructuredRequirementFeature[]
  }
  business_rules: string[]
  page_and_interaction: {
    pages: StructuredRequirementPage[]
    interaction_flow: string[]
  }
  copywriting: string[]
  data_and_dependencies: string[]
  risks_and_notes: string[]
  acceptance_criteria: string[]
  open_questions: string[]
  collection_status: StructuredRequirementCollectionStatus
}

export type ConversationChainNodeStatus = 'complete' | 'current' | 'pending'

export type ConversationChainNode = {
  track: string
  node: string
  label: string
  status: ConversationChainNodeStatus
}

export type ConversationChainState = {
  enabled: boolean
  mode?: 'template' | 'ic_substrate' | string
  template_id?: string
  template_name?: string
  current_track?: string
  current_node?: string
  current_node_label?: string
  current_step_index?: number
  total_steps?: number
  status?: 'not_started' | 'in_progress' | 'complete' | string
  next_question_source?: string
  intent_track?: string
  intent_focus?: string
  tracks?: string[]
  nodes?: ConversationChainNode[]
}

export type StructuredRequirementResponse = {
  session_id: string
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: unknown
}

export function createEmptyConversationChainState(): ConversationChainState {
  return { enabled: false }
}

export function createEmptyStructuredRequirementModel(): StructuredRequirementModel {
  return {
    document_info: {
      project_name: '',
      requirement_name: '',
    },
    product_context: {
      requesting_department: '',
      business_owner: '',
      software_type: '',
      primary_user: '',
      decision_or_action: '',
      acceptance_owner: '',
    },
    background: {
      summary: '',
      objective: '',
    },
    scope: {
      in_scope: [],
      out_of_scope: [],
    },
    users_and_scenarios: {
      target_users: [],
      core_scenarios: [],
    },
    functional_requirements: {
      overview: '',
      feature_details: [],
    },
    business_rules: [],
    page_and_interaction: {
      pages: [],
      interaction_flow: [],
    },
    copywriting: [],
    data_and_dependencies: [],
    risks_and_notes: [],
    acceptance_criteria: [],
    open_questions: [],
    collection_status: {
      objective: createEmptyRequirementCollectionItem(),
      scope: createEmptyRequirementCollectionItem(),
      users: createEmptyRequirementCollectionItem(),
      scenarios: createEmptyRequirementCollectionItem(),
      features: createEmptyRequirementCollectionItem(),
      pages: createEmptyRequirementCollectionItem(),
      rules: createEmptyRequirementCollectionItem(),
      integrations: createEmptyRequirementCollectionItem(),
      acceptance: createEmptyRequirementCollectionItem(),
    },
  }
}

export function normalizeConversationChainState(payload: unknown): ConversationChainState {
  const root = isRecord(payload) ? payload : {}
  const enabled = Boolean(root.enabled)
  if (!enabled) {
    return createEmptyConversationChainState()
  }

  return {
    enabled: true,
    mode: asString(root.mode),
    template_id: asString(root.template_id),
    template_name: asString(root.template_name),
    current_track: asString(root.current_track),
    current_node: asString(root.current_node),
    current_node_label: asString(root.current_node_label),
    current_step_index: asNumber(root.current_step_index),
    total_steps: asNumber(root.total_steps),
    status: asString(root.status),
    next_question_source: asString(root.next_question_source),
    intent_track: asString(root.intent_track),
    intent_focus: asString(root.intent_focus),
    tracks: asStringArray(root.tracks),
    nodes: asConversationChainNodes(root.nodes),
  }
}

export function extractConversationChainState(payload: unknown): ConversationChainState | null {
  if (!isRecord(payload) || payload.conversation_chain_state === undefined) {
    return null
  }
  return normalizeConversationChainState(payload.conversation_chain_state)
}

export function normalizeStructuredRequirementModel(payload: unknown): StructuredRequirementModel {
  const root = isRecord(payload) ? payload : {}

  const documentInfo = asRecord(root.document_info)
  const productContext = asRecord(root.product_context)
  const background = asRecord(root.background)
  const scope = asRecord(root.scope)
  const usersAndScenarios = asRecord(root.users_and_scenarios)
  const functionalRequirements = asRecord(root.functional_requirements)
  const pageAndInteraction = asRecord(root.page_and_interaction)

  return {
    document_info: {
      project_name: asString(documentInfo.project_name),
      requirement_name: asString(documentInfo.requirement_name),
    },
    product_context: {
      requesting_department: asString(productContext.requesting_department),
      business_owner: asString(productContext.business_owner),
      software_type: asString(productContext.software_type),
      primary_user: asString(productContext.primary_user),
      decision_or_action: asString(productContext.decision_or_action),
      acceptance_owner: asString(productContext.acceptance_owner),
    },
    background: {
      summary: asString(background.summary),
      objective: asString(background.objective),
    },
    scope: {
      in_scope: asStringArray(scope.in_scope),
      out_of_scope: asStringArray(scope.out_of_scope),
    },
    users_and_scenarios: {
      target_users: asStringArray(usersAndScenarios.target_users),
      core_scenarios: asStringArray(usersAndScenarios.core_scenarios),
    },
    functional_requirements: {
      overview: asString(functionalRequirements.overview),
      feature_details: asFeatureDetails(functionalRequirements.feature_details),
    },
    business_rules: asStringArray(root.business_rules),
    page_and_interaction: {
      pages: asPages(pageAndInteraction.pages),
      interaction_flow: asStringArray(pageAndInteraction.interaction_flow),
    },
    copywriting: asStringArray(root.copywriting),
    data_and_dependencies: asStringArray(root.data_and_dependencies),
    risks_and_notes: asStringArray(root.risks_and_notes),
    acceptance_criteria: asStringArray(root.acceptance_criteria),
    open_questions: asStringArray(root.open_questions),
    collection_status: asCollectionStatus(root.collection_status),
  }
}

export function extractStructuredRequirementModel(payload: unknown): StructuredRequirementModel | null {
  if (!isRecord(payload)) {
    return null
  }

  if (payload.structured_requirement_model !== undefined) {
    return normalizeStructuredRequirementModel(payload.structured_requirement_model)
  }
  if (payload.summary !== undefined) {
    return normalizeStructuredRequirementModel(payload.summary)
  }

  if (looksLikeStructuredRequirementRoot(payload)) {
    return normalizeStructuredRequirementModel(payload)
  }

  return null
}

export function hasStructuredRequirementContent(model: StructuredRequirementModel): boolean {
  return Boolean(
    model.document_info.project_name ||
      model.document_info.requirement_name ||
      model.product_context.requesting_department ||
      model.product_context.business_owner ||
      model.product_context.software_type ||
      model.product_context.primary_user ||
      model.product_context.decision_or_action ||
      model.product_context.acceptance_owner ||
      model.background.summary ||
      model.background.objective ||
      model.scope.in_scope.length ||
      model.scope.out_of_scope.length ||
      model.users_and_scenarios.target_users.length ||
      model.users_and_scenarios.core_scenarios.length ||
      model.functional_requirements.overview ||
      model.functional_requirements.feature_details.length ||
      model.business_rules.length ||
      model.page_and_interaction.pages.length ||
      model.page_and_interaction.interaction_flow.length ||
      model.copywriting.length ||
      model.data_and_dependencies.length ||
      model.risks_and_notes.length ||
      model.acceptance_criteria.length ||
      model.open_questions.length
  )
}

function asFeatureDetails(value: unknown): StructuredRequirementFeature[] {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map((item) => {
      const raw = asRecord(item)
      return {
        feature_name: asString(raw.feature_name),
        description: asString(raw.description),
        trigger: asString(raw.trigger),
        processing_logic: asString(raw.processing_logic),
        inputs: asStringArray(raw.inputs),
        outputs: asStringArray(raw.outputs),
        exception_cases: asStringArray(raw.exception_cases),
      }
    })
    .filter((item) => featureHasContent(item))
}

function asConversationChainNodes(value: unknown): ConversationChainNode[] {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map((item) => {
      const raw = asRecord(item)
      const status = asString(raw.status)
      return {
        track: asString(raw.track),
        node: asString(raw.node),
        label: asString(raw.label),
        status: isConversationChainNodeStatus(status) ? status : 'pending',
      }
    })
    .filter((item) => item.track || item.node || item.label)
}

function isConversationChainNodeStatus(value: string): value is ConversationChainNodeStatus {
  return value === 'complete' || value === 'current' || value === 'pending'
}

function asNumber(value: unknown): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : 0
  }
  return 0
}

function asPages(value: unknown): StructuredRequirementPage[] {
  if (!Array.isArray(value)) {
    return []
  }

  return value
    .map((item) => {
      const raw = asRecord(item)
      return {
        page_name: asString(raw.page_name),
        entry_point: asString(raw.entry_point),
        page_elements: asStringArray(raw.page_elements),
        button_actions: asStringArray(raw.button_actions),
      }
    })
    .filter((item) => pageHasContent(item))
}

function asString(value: unknown): string {
  if (typeof value === 'string') {
    return value.trim()
  }
  if (value === null || value === undefined) {
    return ''
  }
  return String(value).trim()
}

function asStringArray(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value.map((item) => asString(item)).filter(Boolean)
  }
  if (typeof value === 'string' && value.trim()) {
    return [value.trim()]
  }
  return []
}

function asRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {}
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
}

function looksLikeStructuredRequirementRoot(value: Record<string, unknown>): boolean {
  return [
    'document_info',
    'product_context',
    'background',
    'scope',
    'users_and_scenarios',
    'functional_requirements',
    'business_rules',
    'page_and_interaction',
    'copywriting',
    'data_and_dependencies',
    'risks_and_notes',
    'acceptance_criteria',
    'open_questions',
    'collection_status',
  ].some((key) => key in value)
}

function asCollectionStatus(value: unknown): StructuredRequirementCollectionStatus {
  const raw = asRecord(value)
  return {
    objective: asCollectionItem(raw.objective),
    scope: asCollectionItem(raw.scope),
    users: asCollectionItem(raw.users),
    scenarios: asCollectionItem(raw.scenarios),
    features: asCollectionItem(raw.features),
    pages: asCollectionItem(raw.pages),
    rules: asCollectionItem(raw.rules),
    integrations: asCollectionItem(raw.integrations),
    acceptance: asCollectionItem(raw.acceptance),
  }
}

function asCollectionItem(value: unknown): RequirementCollectionItem {
  const raw = asRecord(value)
  const status = normalizeCollectionStatus(raw.status)
  return {
    status,
    reason: asString(raw.reason),
    pending_questions: asStringArray(raw.pending_questions),
  }
}

function normalizeCollectionStatus(value: unknown): RequirementCollectionStatus {
  const normalized = asString(value).toLowerCase()
  if (
    normalized === 'captured' ||
    normalized === 'pending_confirmation' ||
    normalized === 'confirmed' ||
    normalized === 'conflict'
  ) {
    return normalized
  }
  return 'missing'
}

function createEmptyRequirementCollectionItem(): RequirementCollectionItem {
  return {
    status: 'missing',
    reason: '',
    pending_questions: [],
  }
}

function featureHasContent(feature: StructuredRequirementFeature): boolean {
  return Boolean(
    feature.feature_name ||
      feature.description ||
      feature.trigger ||
      feature.processing_logic ||
      feature.inputs.length ||
      feature.outputs.length ||
      feature.exception_cases.length,
  )
}

function pageHasContent(page: StructuredRequirementPage): boolean {
  return Boolean(
    page.page_name ||
      page.entry_point ||
      page.page_elements.length ||
      page.button_actions.length,
  )
}
