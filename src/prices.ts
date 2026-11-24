/** CoinGecko-backed quotes and paper-alert helpers for GlancePx. */

export type CoinId = 'bitcoin' | 'ethereum' | 'solana' | 'binancecoin'

export interface CoinDef {
  id: CoinId
  symbol: string
}

export interface Quote {
  id: CoinId
  symbol: string
  usd: number
  change24h: number
}

export const COINS: readonly CoinDef[] = [
  { id: 'bitcoin', symbol: 'BTC' },
  { id: 'ethereum', symbol: 'ETH' },
  { id: 'solana', symbol: 'SOL' },
  { id: 'binancecoin', symbol: 'BNB' },
] as const

/** Conservative cached quotes used only when CoinGecko is unreachable (demo fallback). */
export const FALLBACK_QUOTES: readonly Quote[] = [
  { id: 'bitcoin', symbol: 'BTC', usd: 91234, change24h: 2.14 },
  { id: 'ethereum', symbol: 'ETH', usd: 3120.4, change24h: -0.42 },
  { id: 'solana', symbol: 'SOL', usd: 142.18, change24h: 1.83 },
  { id: 'binancecoin', symbol: 'BNB', usd: 610.2, change24h: 0.21 },
] as const

/** Default paper-alert threshold: +5%. Easy to confirm with one tap, no typing. */
export const ALERT_BPS = 500

export const COINGECKO_URL =
  'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin&vs_currencies=usd&include_24hr_change=true'

export function formatUsd(n: number): string {
  if (!Number.isFinite(n) || n < 0) return '—'
  if (n >= 1000) {
    return Math.round(n).toLocaleString('en-US')
  }
  if (n >= 1) return n.toFixed(2)
  return n.toFixed(4)
}

export function formatChange(n: number): string {
  if (!Number.isFinite(n)) return '—'
  const sign = n > 0 ? '+' : n < 0 ? '' : '+'
  return `${sign}${n.toFixed(1)}%`
}

export function alertTarget(usd: number, bps: number = ALERT_BPS): number {
  return usd * (10_000 + bps) / 10_000
}

export function nextIndex(current: number, len: number, delta: number): number {
  if (len <= 0) return 0
  return ((current + delta) % len + len) % len
}

interface CoinGeckoRow {
  usd?: number
  usd_24h_change?: number
}

export function quotesFromCoingecko(payload: unknown): Quote[] {
  if (payload === null || typeof payload !== 'object') {
    throw new Error('CoinGecko payload is not an object')
  }
  const data = payload as Record<string, CoinGeckoRow>
  const out: Quote[] = []
  for (const coin of COINS) {
    const row = data[coin.id]
    if (!row || typeof row.usd !== 'number' || !Number.isFinite(row.usd)) {
      throw new Error(`Missing USD price for ${coin.id}`)
    }
    const change = typeof row.usd_24h_change === 'number' && Number.isFinite(row.usd_24h_change)
      ? row.usd_24h_change
      : 0
    out.push({ id: coin.id, symbol: coin.symbol, usd: row.usd, change24h: change })
  }
  return out
}

export async function fetchQuotes(fetcher: typeof fetch = fetch, timeoutMs = 8000): Promise<Quote[]> {
  const ac = new AbortController()
  const timer = setTimeout(() => ac.abort(), timeoutMs)
  try {
    const res = await fetcher(COINGECKO_URL, {
      signal: ac.signal,
      headers: { accept: 'application/json' },
    })
    if (!res.ok) throw new Error(`CoinGecko HTTP ${res.status}`)
    return quotesFromCoingecko(await res.json())
  } finally {
    clearTimeout(timer)
  }
}

export function renderQuotesPage(opts: {
  quotes: readonly Quote[]
  selected: number
  live: boolean
  alertCount: number
  clock: string
}): string {
  const { quotes, selected, live, alertCount, clock } = opts
  const tag = live ? 'live' : 'cached'
  const lines = quotes.map((q, i) => {
    const mark = i === selected ? '>' : ' '
    return `${mark} ${q.symbol.padEnd(3, ' ')}  ${formatUsd(q.usd).padStart(8, ' ')}  ${formatChange(q.change24h)}`
  })
  const focus = quotes[selected]?.symbol ?? '—'
  const alerts = alertCount > 0 ? ` · ${alertCount} alert${alertCount === 1 ? '' : 's'}` : ''
  return [
    `GLANCEPX  ${clock}  ${tag}${alerts}`,
    '',
    ...lines,
    '',
    `TAP confirm +5% alert on ${focus}`,
    'SWIPE next coin · 2xTAP exit',
  ].join('\n')
}

export function renderConfirmPage(quote: Quote): string {
  const target = alertTarget(quote.usd)
  return [
    'SET PAPER ALERT',
    '',
    `${quote.symbol}  now ${formatUsd(quote.usd)}`,
    `Alert if +5%  →  ${formatUsd(target)}`,
    '',
    'Paper / on-device only. No order is sent.',
    'TAP to confirm',
    '2xTAP to cancel',
  ].join('\n')
}

export function renderDonePage(quote: Quote, target: number): string {
  return [
    'ALERT SET (paper)',
    '',
    `${quote.symbol} > ${formatUsd(target)}`,
    'Stored on this device.',
    'Will flag on the next refresh.',
    '',
    'TAP back to quotes',
  ].join('\n')
}

export function clockHm(date: Date = new Date()): string {
  const h = date.getHours().toString().padStart(2, '0')
  const m = date.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}
