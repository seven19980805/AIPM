import type { ConversationChainState } from './structuredRequirement'
import type { InterviewStateV2 } from './interviewState'

export type MessageRole = 'user' | 'assistant'
export type MessageKind = 'chat' | 'design_doc' | 'prd_doc'
export type PromptTemplate = 'personal_project' | 'standard'
export type StartFunction = 'from_scratch' | 'improve_draft'
export type IntakeMode = 'scratch' | 'draft' | 'template'
export type BusinessRoute = 'production' | 'quality' | 'tdi'
export type LanguageCode = 'en' | 'de' | 'zh' | 'ms'
export type HandoffMode = 'prd_v0' | 'final_documents'
export type SessionLaunchMode = IntakeMode
export type SessionLaunchStatus = 'not_started' | 'in_progress' | 'complete'

export type SessionLaunchStage = {
  key: string
  track: string
  label: string
  status: 'current' | 'complete' | 'pending'
}

export type SessionLaunchSuggestion = {
  id: string
  label: string
  text: string
}

export type SessionLaunchSource = {
  type: IntakeMode
  id: string
  name: string
  version: string
  language: string
  start_function: StartFunction | string
  business_route: BusinessRoute | string
}

export type SessionLaunchContext = {
  version: 2
  mode: SessionLaunchMode
  business_route: BusinessRoute | string
  status: SessionLaunchStatus
  title: string
  description: string
  question: string
  stages: SessionLaunchStage[]
  suggestions: SessionLaunchSuggestion[]
  question_budget: {
    target: number
    maximum: number
    asked: number
    remaining: number
  }
  source: SessionLaunchSource
}

export type PrdV0DiscoveryExitContract = {
  contract_version?: string
  target_timebox_minutes?: number | null
  max_user_seed_rounds?: number | null
  round_1_behavior?: string
  round_2_behavior?: string
  exit_trigger?: string
  default_next_action?: string
  main_cta?: string
  unknown_policy?: string
  blocking_conflict_only?: boolean
  anti_loop_rules?: string[]
}

export type HandoffReadiness = {
  it_review_ready?: boolean
  vibe_coding_ready?: boolean
  assumption_handoff?: boolean
  target_timebox_minutes?: number | null
  max_discovery_rounds?: number | null
  discovery_budget_policy?: string
  discovery_exit_contract?: PrdV0DiscoveryExitContract
  timebox_route?: string
  action_budget_steps?: string[]
  handoff_goal?: string
  requires_full_readiness_before_handoff?: boolean
  requires_final_design_doc?: boolean
  design_doc_required_for_handoff?: boolean
  final_design_doc_missing?: boolean
  final_design_doc_followup?: string
  blocked_production_actions?: string[]
  required_review_sections?: string[]
}

export type VibeCodingStartHere = {
  handoff_mode?: HandoffMode
  timebox_route?: string
  action_budget_steps?: string[]
  discovery_exit_contract?: PrdV0DiscoveryExitContract
  first_task_card?: {
    task?: string
    start_from?: PrdV0FirstBuildSlice
    input_contracts?: string[]
    deliverables?: string[]
    stop_rules?: string[]
  }
  must_read?: string[]
  first_steps?: string[]
  smoke_tests?: string[]
  guardrails?: string[]
}

export type PrdV0CriticalDecision = {
  key:
    | 'business_action'
    | 'primary_user_or_owner'
    | 'source_of_truth'
    | 'integration_writeback_boundary'
    | 'acceptance_evidence'
  label?: string
  status?: 'pending_or_assumed' | 'confirmed' | 'conflict'
  review_question?: string
  default_v0_handling?: string
}

export type PrdV0FirstBuildSlice = {
  first_page?: string
  first_api?: string
  mock_data_object?: string
  first_smoke_test?: string
  blocked_action?: string
  scope_lock?: string
  assumptions_file?: string
}

export type PrdV0AssumptionsFileSeed = {
  filename?: string
  mime_type?: string
  source?: string
  must_create_before_scope_expansion?: boolean
  content?: string
}

export type PrdV0MockDataSeed = {
  filename?: string
  mime_type?: string
  source?: string
  object_name?: string
  fields?: string[]
  rows?: Array<Record<string, unknown>>
  first_api?: string
  first_page?: string
  first_smoke_test?: string
  blocked_action?: string
  must_create_before_ui?: boolean
  content?: string
}

export type HandoffArtifact = {
  kind?: 'prd' | 'design' | 'assumptions' | 'mock_data' | string
  filename?: string
  mime_type?: string
  role?: string
  delivery?: 'download' | 'local_path' | 'inline_file' | string
  download_url?: string
  path?: string
  required_before?: string
  object_name?: string
  first_api?: string
  first_page?: string
  first_smoke_test?: string
  content?: string
}

export type PrdV0AcceptanceEvidencePacket = {
  proof_target?: string
  first_smoke_test?: string
  evidence_artifacts?: string[]
  source_to_confirm?: string
  owner_to_confirm?: string
  blocked_action_check?: string
  handoff_gate?: string
}

export type PrdV0DefaultSeedQualityGate = {
  seed_origin?: 'default_expert_seed' | 'user_seed' | string
  input_quality?: string
  top_open_question?: string
  requires_business_owner_confirmation?: boolean
  no_production_writeback_before_approval?: boolean
  allowed_vibe_coding_scope?: string
  blocked_until_approval?: string[]
  required_confirmations?: string[]
  quality_rule?: string
}

export type PrdV0HandoffManifest = {
  manifest_version?: string
  handoff_goal?: string
  target_timebox_minutes?: number | null
  max_discovery_rounds?: number | null
  source_packet_ref?: string
  quality_gate_ref?: string
  discovery_exit_contract?: PrdV0DiscoveryExitContract
  start_from?: {
    first_page?: string
    first_api?: string
    mock_data_object?: string
    first_smoke_test?: string
    blocked_action?: string
    scope_lock?: string
  }
  required_artifacts?: Array<{
    kind?: string
    filename?: string
    field?: string
    required_before?: string
  }>
  quality_gate?: {
    seed_origin?: string
    top_open_question?: string
    allowed_vibe_coding_scope?: string
    no_production_writeback_before_approval?: boolean
    requires_business_owner_confirmation?: boolean
  }
  assumptions_file?: string
  mock_data_file?: string
  handoff_artifact_kinds?: string[]
  blocked_before_approval?: string[]
  done_when?: string[]
  seed_count?: number
  input_quality?: string
}

export type ChatMessagePayload = {
  message_id?: number
  role: MessageRole
  content: string
  display_content?: string
  thinking?: string
  kind?: MessageKind
  download_url?: string
  download_filename?: string
  created_at?: string
}

export type ChatMessage = {
  role: MessageRole
  content: string
  thinking?: string
  createdAt?: string
  kind?: MessageKind
  downloadUrl?: string
  downloadFilename?: string
  prdV0Ready?: boolean
  streaming?: boolean
}

export type SessionSummary = {
  session_id: string
  title: string
  language?: LanguageCode
  prompt_template: PromptTemplate
  applied_template_id: string
  applied_template_name: string
  start_function?: StartFunction
  intake_mode?: IntakeMode
  business_route?: BusinessRoute
  created_at: string
  updated_at: string
  message_count: number
  last_message_preview: string
}

export type SessionDetail = {
  session_id: string
  title: string
  language: LanguageCode
  prompt_template: PromptTemplate
  applied_template_id: string
  applied_template_name: string
  start_function?: StartFunction
  intake_mode?: IntakeMode
  business_route?: BusinessRoute
  created_at: string
  updated_at: string
  messages: ChatMessagePayload[]
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: ConversationChainState
  interview_state?: InterviewStateV2
  launch_context?: SessionLaunchContext
}

export type GeneratedDocumentResponse = {
  session_id: string
  document_markdown: string
  document_type?: string
  filename?: string
  download_url?: string
  saved_at?: string
  status: string
  prd_v0_ready?: boolean
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: ConversationChainState
  interview_state?: InterviewStateV2
}

export type MessageResponse = {
  assistant_message: string
  assistant_thinking?: string
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: ConversationChainState
  interview_state?: InterviewStateV2
  session_id?: string
  message_count?: number
}

export type ImplementationContextResponse = {
  session_id: string
  title: string
  documents_ready: boolean
  handoff_mode?: HandoffMode
  missing_documents?: Array<'prd' | 'design'>
  prd_v0_ready?: boolean
  handoff_readiness?: HandoffReadiness
  vibe_coding_start_here?: VibeCodingStartHere
  prd_v0_critical_decisions?: PrdV0CriticalDecision[]
  prd_v0_first_build_slice?: PrdV0FirstBuildSlice
  prd_v0_acceptance_evidence_packet?: PrdV0AcceptanceEvidencePacket
  prd_v0_default_seed_quality_gate?: PrdV0DefaultSeedQualityGate
  prd_v0_handoff_manifest?: PrdV0HandoffManifest
  prd_v0_assumptions_file_seed?: PrdV0AssumptionsFileSeed
  prd_v0_mock_data_seed?: PrdV0MockDataSeed
  handoff_artifacts?: HandoffArtifact[]
  documents?: {
    prd: {
      filename: string
      path: string
    }
    design?: {
      filename: string
      path: string
    }
  }
  implementation_prompt?: string
}

export type CodingHandoffCreateResponse = {
  handoff_token: string
  expires_at: string
  documents_ready?: boolean
  handoff_mode?: HandoffMode
  prd_v0_ready?: boolean
  handoff_readiness?: HandoffReadiness
  vibe_coding_start_here?: VibeCodingStartHere
  prd_v0_critical_decisions?: PrdV0CriticalDecision[]
  prd_v0_first_build_slice?: PrdV0FirstBuildSlice
  prd_v0_acceptance_evidence_packet?: PrdV0AcceptanceEvidencePacket
  prd_v0_default_seed_quality_gate?: PrdV0DefaultSeedQualityGate
  prd_v0_handoff_manifest?: PrdV0HandoffManifest
  prd_v0_assumptions_file_seed?: PrdV0AssumptionsFileSeed
  prd_v0_mock_data_seed?: PrdV0MockDataSeed
  handoff_artifacts?: HandoffArtifact[]
  open_url?: string
}
