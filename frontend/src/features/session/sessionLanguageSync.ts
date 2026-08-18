import type { LanguageCode } from '../../types/session'


export type SessionLanguageSyncInput = {
  sessionId: string
  /** The language the user just picked. */
  language: LanguageCode
  /** The language the server currently holds for this session. */
  serverLanguage: LanguageCode
}

export type SessionLanguageSyncOutcome =
  | { status: 'skipped'; reason: 'no-session' | 'unchanged' }
  | { status: 'applied'; language: LanguageCode; detail: unknown }
  | { status: 'stale' }
  | { status: 'failed'; revertTo: LanguageCode; error: unknown }

export type PatchSessionLanguage = (
  sessionId: string,
  language: LanguageCode,
) => Promise<unknown>


/**
 * Persist the session content language, but only on an explicit user switch.
 *
 * The content language decides which language the canonical model is extracted
 * in, so it must never be written just because a session was opened or
 * refreshed. Rapid switching is resolved by ticket: only the newest request may
 * change anything, so a slow earlier response can neither win nor revert a
 * choice the user has already replaced.
 */
export function createSessionLanguageSync(patch: PatchSessionLanguage) {
  let latestTicket = 0

  return async function syncSessionLanguage(
    input: SessionLanguageSyncInput,
  ): Promise<SessionLanguageSyncOutcome> {
    if (!input.sessionId) {
      return { status: 'skipped', reason: 'no-session' }
    }
    if (input.language === input.serverLanguage) {
      return { status: 'skipped', reason: 'unchanged' }
    }

    const ticket = ++latestTicket
    try {
      const detail = await patch(input.sessionId, input.language)
      if (ticket !== latestTicket) {
        return { status: 'stale' }
      }
      return { status: 'applied', language: input.language, detail }
    } catch (error) {
      if (ticket !== latestTicket) {
        return { status: 'stale' }
      }
      // The server still holds the previous language, so the UI follows it back.
      return { status: 'failed', revertTo: input.serverLanguage, error }
    }
  }
}
