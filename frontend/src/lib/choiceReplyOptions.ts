export type ChoiceReplyOption = {
  key: 'A' | 'B' | 'C' | 'D'
  label: string
  value: string
}

const CHOICE_OPTION_BOUNDARY_PATTERN = String.raw`[\s:：?？。；;]`
const CHOICE_OPTION_KEY_PATTERN = String.raw`[ABCD]`
const PRD_V0_CHOICE_NOTE_PATTERN = /\bPRD V0\s+(?:fast path|schnellpfad|laluan pantas|快速路径)[\s\S]*$/i

export function extractChoiceReplyOptions(content: string): ChoiceReplyOption[] {
  const options: ChoiceReplyOption[] = []
  const seen = new Set<string>()
  const normalized = content.replace(/\r\n?/g, '\n')
  const boundary = CHOICE_OPTION_BOUNDARY_PATTERN
  const choiceRegex = new RegExp(
    `(?:^|${boundary})(?:[-*]\\s*)?(?:\\*\\*)?(${CHOICE_OPTION_KEY_PATTERN})(?:\\*\\*)?\\s*[\\.)、:：-]\\s*([\\s\\S]*?)(?=(?:${boundary}|^)(?:[-*]\\s*)?(?:\\*\\*)?${CHOICE_OPTION_KEY_PATTERN}(?:\\*\\*)?\\s*[\\.)、:：-]\\s*|\\n\\s*\\n|$)`,
    'gi',
  )

  for (const match of normalized.matchAll(choiceRegex)) {
    const key = match[1].toUpperCase() as ChoiceReplyOption['key']
    if (seen.has(key)) {
      continue
    }
    const label = cleanChoiceReplyLabel(match[2])
    if (!label) {
      continue
    }
    options.push({
      key,
      label,
      value: `${key}. ${label}`,
    })
    seen.add(key)
    if (options.length >= 4) {
      break
    }
  }

  return options.length >= 2 ? options : []
}

function cleanChoiceReplyLabel(rawLabel: string): string {
  return rawLabel
    .replace(/\*\*/g, '')
    .replace(PRD_V0_CHOICE_NOTE_PATTERN, '')
    .replace(/\s+/g, ' ')
    .replace(/^["'“”]+|["'“”]+$/g, '')
    .trim()
}
