import type { ConversationChainState } from './structuredRequirement'

export type MessageRole = 'user' | 'assistant'
export type MessageKind = 'chat' | 'design_doc' | 'prd_doc'
export type PromptTemplate = 'personal_project' | 'standard'
export type LanguageCode = 'en' | 'de' | 'zh' | 'ms'

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
  streaming?: boolean
}

export type SessionSummary = {
  session_id: string
  title: string
  prompt_template: PromptTemplate
  applied_template_id: string
  applied_template_name: string
  created_at: string
  updated_at: string
  message_count: number
  last_message_preview: string
}

export type SessionDetail = {
  session_id: string
  title: string
  prompt_template: PromptTemplate
  applied_template_id: string
  applied_template_name: string
  created_at: string
  updated_at: string
  messages: ChatMessagePayload[]
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: ConversationChainState
}

export type GeneratedDocumentResponse = {
  session_id: string
  document_markdown: string
  document_type?: string
  filename?: string
  download_url?: string
  saved_at?: string
  status: string
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: ConversationChainState
}

export type MessageResponse = {
  assistant_message: string
  assistant_thinking?: string
  summary?: unknown
  structured_requirement_model?: unknown
  structured_requirement_sync_status?: 'ready' | 'stale' | 'missing'
  conversation_chain_state?: ConversationChainState
  session_id?: string
  message_count?: number
}

export type ImplementationContextResponse = {
  session_id: string
  title: string
  documents_ready: boolean
  missing_documents?: Array<'prd' | 'design'>
  documents?: {
    prd: {
      filename: string
      path: string
    }
    design: {
      filename: string
      path: string
    }
  }
  implementation_prompt?: string
}

export type CodingHandoffCreateResponse = {
  handoff_token: string
  expires_at: string
  open_url?: string
}
