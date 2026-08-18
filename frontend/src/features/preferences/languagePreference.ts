import type { LanguageCode } from '../../types/session'


export const LANGUAGE_STORAGE_KEY = 'ats-aipm-language'

type LanguagePreferenceStorage = {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
}

const SUPPORTED_LANGUAGES = new Set<LanguageCode>(['en', 'de', 'zh', 'ms'])


export function loadLanguagePreference(
  storage: LanguagePreferenceStorage | null | undefined,
): LanguageCode {
  try {
    const storedLanguage = storage?.getItem(LANGUAGE_STORAGE_KEY) ?? ''
    return SUPPORTED_LANGUAGES.has(storedLanguage as LanguageCode)
      ? storedLanguage as LanguageCode
      : 'en'
  } catch {
    return 'en'
  }
}


export function saveLanguagePreference(
  storage: LanguagePreferenceStorage | null | undefined,
  language: LanguageCode,
): void {
  if (!SUPPORTED_LANGUAGES.has(language)) {
    return
  }
  try {
    storage?.setItem(LANGUAGE_STORAGE_KEY, language)
  } catch {
    // The current selection still works when browser storage is unavailable.
  }
}
