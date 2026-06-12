<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onMounted, ref, watch } from 'vue'
import type mermaidModule from 'mermaid'

const props = withDefaults(
  defineProps<{
    source: string
  }>(),
  {
    source: '',
  },
)

const markdownRoot = ref<HTMLElement | null>(null)
const componentInstance = getCurrentInstance()
const renderedMarkdown = computed(() => renderMarkdown(props.source))
let mermaidRenderGeneration = 0
let mermaidRenderSequence = 0
let mermaidPromise: Promise<typeof mermaidModule> | null = null
let mermaidInitialized = false

onMounted(() => {
  void renderMermaidBlocks()
})

watch(
  renderedMarkdown,
  async () => {
    await nextTick()
    await renderMermaidBlocks()
  },
  { flush: 'post' },
)

function renderMarkdown(source: string): string {
  const lines = source.replace(/\r\n?/g, '\n').split('\n')
  return renderBlocks(lines)
}

function renderBlocks(lines: string[]): string {
  const blocks: string[] = []
  let index = 0

  while (index < lines.length) {
    const line = lines[index] ?? ''

    if (!line.trim()) {
      index += 1
      continue
    }

    const fenceMatch = line.match(/^\s*```([\w-]*)\s*$/)
    if (fenceMatch) {
      const language = (fenceMatch[1] ?? '').trim().toLowerCase()
      const codeLines: string[] = []
      index += 1
      while (index < lines.length && !/^\s*```\s*$/.test(lines[index] ?? '')) {
        codeLines.push(lines[index] ?? '')
        index += 1
      }
      if (index < lines.length) {
        index += 1
      }
      const code = codeLines.join('\n')
      blocks.push(language === 'mermaid' ? renderMermaidBlock(code) : renderCodeBlock(language, code))
      continue
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.+?)\s*#*\s*$/)
    if (headingMatch) {
      const level = headingMatch[1].length
      blocks.push(`<h${level}>${renderInline(headingMatch[2])}</h${level}>`)
      index += 1
      continue
    }

    if (/^\s*([-*_])(?:\s*\1){2,}\s*$/.test(line)) {
      blocks.push('<hr>')
      index += 1
      continue
    }

    if (isTableStart(lines, index)) {
      const table = collectTable(lines, index)
      blocks.push(renderTable(table.rows))
      index = table.nextIndex
      continue
    }

    const unorderedMatch = line.match(/^\s*[-*+]\s+(.+)$/)
    const orderedMatch = line.match(/^\s*\d+[.)]\s+(.+)$/)
    if (unorderedMatch || orderedMatch) {
      const ordered = Boolean(orderedMatch)
      const result = collectList(lines, index, ordered)
      blocks.push(renderList(result.items, ordered))
      index = result.nextIndex
      continue
    }

    if (/^\s*>\s?/.test(line)) {
      const quoteLines: string[] = []
      while (index < lines.length && /^\s*>\s?/.test(lines[index] ?? '')) {
        quoteLines.push((lines[index] ?? '').replace(/^\s*>\s?/, ''))
        index += 1
      }
      blocks.push(`<blockquote>${renderBlocks(quoteLines)}</blockquote>`)
      continue
    }

    const paragraphLines: string[] = []
    while (index < lines.length && lines[index]?.trim() && !isBlockBoundary(lines, index)) {
      paragraphLines.push(lines[index] ?? '')
      index += 1
    }
    blocks.push(`<p>${renderInline(paragraphLines.join(' '))}</p>`)
  }

  return blocks.join('\n')
}

async function renderMermaidBlocks() {
  const root = getMarkdownRoot()
  if (!root) {
    return
  }

  const generation = ++mermaidRenderGeneration
  const blocks = Array.from(root.querySelectorAll<HTMLElement>('[data-mermaid-source]'))
  if (!blocks.length) {
    return
  }

  const mermaid = await loadMermaid()
  for (const block of blocks) {
    const encodedSource = block.dataset.mermaidSource ?? ''
    const source = decodeMermaidSource(encodedSource)
    if (!source.trim()) {
      continue
    }

    const diagramId = `aipm-mermaid-${Date.now()}-${mermaidRenderSequence++}`
    try {
      const { svg, bindFunctions } = await mermaid.render(diagramId, source)
      if (generation !== mermaidRenderGeneration) {
        return
      }
      block.innerHTML = svg
      block.removeAttribute('data-mermaid-source')
      block.classList.add('rendered')
      bindFunctions?.(block)
    } catch (error) {
      if (generation !== mermaidRenderGeneration) {
        return
      }
      block.classList.add('error')
      block.setAttribute('title', error instanceof Error ? error.message : 'Unable to render Mermaid diagram')
    }
  }
}

function getMarkdownRoot(): HTMLElement | null {
  if (markdownRoot.value) {
    return markdownRoot.value
  }

  const instanceRoot = componentInstance?.proxy?.$el
  if (instanceRoot instanceof HTMLElement) {
    markdownRoot.value = instanceRoot
    return instanceRoot
  }

  return null
}

async function loadMermaid(): Promise<typeof mermaidModule> {
  mermaidPromise ??= import('mermaid').then((module) => module.default)
  const mermaid = await mermaidPromise
  if (!mermaidInitialized) {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: 'base',
      themeVariables: {
        primaryColor: '#eff6ff',
        primaryBorderColor: '#2563eb',
        primaryTextColor: '#1f2937',
        lineColor: '#64748b',
        fontFamily: 'Inter, system-ui, sans-serif',
      },
    })
    mermaidInitialized = true
  }
  return mermaid
}

function renderMermaidBlock(source: string): string {
  return (
    `<div class="mermaid-diagram" data-mermaid-source="${escapeAttribute(encodeURIComponent(source))}">` +
    renderCodeBlock('mermaid', source) +
    '</div>'
  )
}

function renderCodeBlock(language: string, code: string): string {
  const languageClass = language ? ` class="language-${escapeAttribute(language)}"` : ''
  return `<pre><code${languageClass}>${escapeHtml(code)}</code></pre>`
}

function decodeMermaidSource(value: string): string {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}

function isBlockBoundary(lines: string[], index: number): boolean {
  const line = lines[index] ?? ''
  return (
    /^\s*```/.test(line) ||
    /^(#{1,6})\s+/.test(line) ||
    /^\s*([-*_])(?:\s*\1){2,}\s*$/.test(line) ||
    isTableStart(lines, index) ||
    /^\s*[-*+]\s+/.test(line) ||
    /^\s*\d+[.)]\s+/.test(line) ||
    /^\s*>\s?/.test(line)
  )
}

function collectList(lines: string[], startIndex: number, ordered: boolean): { items: string[]; nextIndex: number } {
  const items: string[] = []
  let index = startIndex
  const pattern = ordered ? /^\s*\d+[.)]\s+(.+)$/ : /^\s*[-*+]\s+(.+)$/

  while (index < lines.length) {
    const match = (lines[index] ?? '').match(pattern)
    if (!match) {
      break
    }
    items.push(match[1])
    index += 1
  }

  return { items, nextIndex: index }
}

function renderList(items: string[], ordered: boolean): string {
  const tag = ordered ? 'ol' : 'ul'
  const renderedItems = items.map((item) => `<li>${renderInline(item)}</li>`).join('')
  return `<${tag}>${renderedItems}</${tag}>`
}

function isTableStart(lines: string[], index: number): boolean {
  const header = lines[index] ?? ''
  const divider = lines[index + 1] ?? ''
  return header.includes('|') && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(divider)
}

function collectTable(lines: string[], startIndex: number): { rows: string[][]; nextIndex: number } {
  const rows: string[][] = []
  let index = startIndex

  rows.push(splitTableRow(lines[index] ?? ''))
  index += 2

  while (index < lines.length && (lines[index] ?? '').includes('|') && (lines[index] ?? '').trim()) {
    rows.push(splitTableRow(lines[index] ?? ''))
    index += 1
  }

  return { rows, nextIndex: index }
}

function splitTableRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim())
}

function renderTable(rows: string[][]): string {
  if (!rows.length) {
    return ''
  }

  const header = rows[0]
  const body = rows.slice(1)
  const headerHtml = header.map((cell) => `<th>${renderInline(cell)}</th>`).join('')
  const bodyHtml = body
    .map((row) => `<tr>${row.map((cell) => `<td>${renderInline(cell)}</td>`).join('')}</tr>`)
    .join('')

  return `<div class="markdown-table-scroll"><table><thead><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`
}

function renderInline(text: string): string {
  const parts = text.split(/(`[^`]*`)/g)
  return parts
    .map((part) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return `<code>${escapeHtml(part.slice(1, -1))}</code>`
      }
      return renderInlineWithoutCode(part)
    })
    .join('')
}

function renderInlineWithoutCode(text: string): string {
  const linkRegex = /\[([^\]]+)]\(([^)\s]+)\)/g
  let result = ''
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = linkRegex.exec(text)) !== null) {
    result += renderBasicInline(text.slice(lastIndex, match.index))
    const href = sanitizeUrl(match[2])
    const label = renderBasicInline(match[1])
    result += href ? `<a href="${escapeAttribute(href)}" target="_blank" rel="noreferrer">${label}</a>` : label
    lastIndex = match.index + match[0].length
  }

  result += renderBasicInline(text.slice(lastIndex))
  return result
}

function renderBasicInline(text: string): string {
  return escapeHtml(text)
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/__([^_]+)__/g, '<strong>$1</strong>')
    .replace(/~~([^~]+)~~/g, '<del>$1</del>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
}

function sanitizeUrl(rawUrl: string): string {
  const trimmed = rawUrl.trim()
  if (/^(https?:|mailto:|tel:)/i.test(trimmed) || trimmed.startsWith('#') || trimmed.startsWith('/')) {
    return trimmed
  }
  return ''
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function escapeAttribute(value: string): string {
  return escapeHtml(value).replace(/`/g, '&#96;')
}
</script>

<template>
  <div class="markdown-renderer" v-html="renderedMarkdown"></div>
</template>

<style scoped>
.markdown-renderer {
  color: inherit;
  font-size: 0.92rem;
  line-height: 1.68;
  overflow-wrap: anywhere;
}

.markdown-renderer :deep(*) {
  max-width: 100%;
}

.markdown-renderer :deep(h1),
.markdown-renderer :deep(h2),
.markdown-renderer :deep(h3),
.markdown-renderer :deep(h4),
.markdown-renderer :deep(h5),
.markdown-renderer :deep(h6) {
  margin: 1.1em 0 0.55em;
  color: var(--ink);
  line-height: 1.25;
  letter-spacing: 0;
}

.markdown-renderer :deep(h1) {
  margin-top: 0;
  font-size: 1.42rem;
}

.markdown-renderer :deep(h2) {
  padding-top: 0.65rem;
  border-top: 1px solid var(--line);
  font-size: 1.16rem;
}

.markdown-renderer :deep(h3) {
  font-size: 1rem;
}

.markdown-renderer :deep(h4),
.markdown-renderer :deep(h5),
.markdown-renderer :deep(h6) {
  font-size: 0.94rem;
}

.markdown-renderer :deep(p),
.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol),
.markdown-renderer :deep(blockquote),
.markdown-renderer :deep(pre),
.markdown-renderer :deep(.markdown-table-scroll) {
  margin: 0.72em 0;
}

.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  padding-left: 1.35rem;
}

.markdown-renderer :deep(li + li) {
  margin-top: 0.28rem;
}

.markdown-renderer :deep(blockquote) {
  padding: 0.2rem 0 0.2rem 0.9rem;
  border-left: 4px solid rgba(37, 99, 235, 0.28);
  color: #53647d;
}

.markdown-renderer :deep(blockquote > :first-child) {
  margin-top: 0;
}

.markdown-renderer :deep(blockquote > :last-child) {
  margin-bottom: 0;
}

.markdown-renderer :deep(code) {
  padding: 0.12rem 0.34rem;
  border-radius: 6px;
  background: #eef3f8;
  color: #203047;
  font-family: var(--mono);
  font-size: 0.86em;
}

.markdown-renderer :deep(pre) {
  overflow: auto;
  padding: 0.85rem 1rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f7faff;
}

.markdown-renderer :deep(pre code) {
  display: block;
  padding: 0;
  background: transparent;
  white-space: pre;
}

.markdown-renderer :deep(.mermaid-diagram) {
  margin: 0.82em 0;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #f7faff;
  overflow: auto;
}

.markdown-renderer :deep(.mermaid-diagram.rendered) {
  display: grid;
  justify-items: center;
}

.markdown-renderer :deep(.mermaid-diagram.rendered pre) {
  display: none;
}

.markdown-renderer :deep(.mermaid-diagram svg) {
  display: block;
  width: auto;
  max-width: 100%;
  height: auto;
}

.markdown-renderer :deep(.mermaid-diagram.error) {
  border-color: rgba(220, 38, 38, 0.32);
  background: rgba(220, 38, 38, 0.06);
}

.markdown-renderer :deep(a) {
  color: var(--accent-strong);
  font-weight: 700;
  text-decoration: none;
}

.markdown-renderer :deep(a:hover) {
  text-decoration: underline;
}

.markdown-renderer :deep(.markdown-table-scroll) {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.markdown-renderer :deep(table) {
  width: 100%;
  min-width: 560px;
  border-collapse: collapse;
  background: #fff;
}

.markdown-renderer :deep(th),
.markdown-renderer :deep(td) {
  padding: 0.68rem 0.76rem;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
}

.markdown-renderer :deep(th) {
  background: #f2f6fb;
  color: var(--ink);
  font-weight: 800;
}

.markdown-renderer :deep(tr:last-child td) {
  border-bottom: 0;
}

.markdown-renderer :deep(hr) {
  height: 1px;
  margin: 1rem 0;
  border: 0;
  background: var(--line);
}
</style>
