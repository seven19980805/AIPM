import type { LanguageCode } from '../../types/session'
import type { InterviewReplyContext } from '../../types/interviewState'

export type MessageRequestInput = {
  message: string
  displayMessage: string
  language: LanguageCode
  replyContext?: InterviewReplyContext
}

export type MessageRequestBody = {
  message: string
  display_message: string
  language: LanguageCode
  reply_context?: InterviewReplyContext
}

export function buildMessageRequestBody(input: MessageRequestInput): MessageRequestBody {
  const body: MessageRequestBody = {
    message: input.message,
    display_message: input.displayMessage || input.message,
    language: input.language,
  }
  if (input.replyContext) {
    body.reply_context = {
      decision_id: input.replyContext.decision_id,
      action: input.replyContext.action,
      ...(input.replyContext.proposal_id
        ? { proposal_id: input.replyContext.proposal_id }
        : {}),
    }
  }
  return body
}
