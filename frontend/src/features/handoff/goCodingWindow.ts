export type GoCodingWindow = {
  opener: unknown
  readonly closed?: boolean
  location: {
    replace(url: string): void
  }
  close(): void
}

type OpenWindow = (url?: string | URL, target?: string) => GoCodingWindow | null
type ReachabilityFetch = (input: string, init: RequestInit) => Promise<unknown>


export function buildGoCodingTargetUrl(
  baseUrl: string,
  handoffToken: string,
  pmApiBaseUrl: string,
): string {
  const targetUrl = new URL(baseUrl)
  targetUrl.searchParams.set('source', 'rqmd')
  targetUrl.searchParams.set('handoff_token', handoffToken)
  targetUrl.searchParams.set('pm_api_base_url', pmApiBaseUrl)
  return targetUrl.toString()
}


export function reserveGoCodingWindow(openWindow: OpenWindow): GoCodingWindow | null {
  const popup = openWindow('about:blank', '_blank')
  if (popup) {
    popup.opener = null
  }
  return popup
}


export async function isGoCodingTargetReachable(
  targetUrl: string,
  fetcher: ReachabilityFetch = window.fetch.bind(window),
  timeoutMs = 2500,
): Promise<boolean> {
  const controller = new AbortController()
  const timeout = globalThis.setTimeout(() => controller.abort(), timeoutMs)
  try {
    await fetcher(targetUrl, {
      method: 'HEAD',
      mode: 'no-cors',
      cache: 'no-store',
      signal: controller.signal,
    })
    return true
  } catch {
    return false
  } finally {
    globalThis.clearTimeout(timeout)
  }
}


export function navigateGoCodingWindow(popup: GoCodingWindow, targetUrl: string): void {
  if (popup.closed) {
    throw new Error('The Go Coding window was closed before the handoff was ready.')
  }
  popup.location.replace(targetUrl)
}


export function closeGoCodingWindow(popup: GoCodingWindow): void {
  if (!popup.closed) {
    popup.close()
  }
}
