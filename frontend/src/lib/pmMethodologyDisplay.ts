import type { PMMethodologyCheck, PMMethodologyState } from '../types/structuredRequirement'

export type PMMethodologyDisplayState = {
  readyCount: number
  missingCount: number
  checks: PMMethodologyCheck[]
  showNextQuestions: boolean
}

export function summarizePMMethodologyDisplay(
  state: PMMethodologyState,
  structuredReadyToGenerate: boolean,
): PMMethodologyDisplayState {
  const checks = [...state.checks].sort(
    (left, right) => methodologyStatusPriority(left.status) - methodologyStatusPriority(right.status),
  )

  if (structuredReadyToGenerate) {
    return {
      readyCount: state.checks.length,
      missingCount: 0,
      checks: checks.filter((check) => check.ready).slice(0, 4),
      showNextQuestions: false,
    }
  }

  return {
    readyCount: state.checks.filter((check) => check.ready).length,
    missingCount: state.missing_evidence.length,
    checks: checks.slice(0, 4),
    showNextQuestions: true,
  }
}

function methodologyStatusPriority(status: PMMethodologyCheck['status']): number {
  if (status === 'conflict') {
    return 0
  }
  if (status === 'missing') {
    return 1
  }
  if (status === 'partial') {
    return 2
  }
  return 3
}
