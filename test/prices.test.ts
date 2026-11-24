import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  ALERT_BPS,
  alertTarget,
  formatChange,
  formatUsd,
  nextIndex,
  quotesFromCoingecko,
  renderConfirmPage,
  renderQuotesPage,
} from '../src/prices.ts'

test('formatUsd groups thousands and keeps small prices readable', () => {
  assert.equal(formatUsd(91234.6), '91,235')
  assert.equal(formatUsd(3120.4), '3,120')
  assert.equal(formatUsd(142.18), '142.18')
  assert.equal(formatUsd(0.03456), '0.0346')
})

test('formatChange always shows a sign and one decimal', () => {
  assert.equal(formatChange(2.14), '+2.1%')
  assert.equal(formatChange(-0.42), '-0.4%')
  assert.equal(formatChange(0), '+0.0%')
})

test('alertTarget is +5% by default', () => {
  assert.equal(alertTarget(1000), 1050)
  assert.equal(alertTarget(1000, ALERT_BPS), 1050)
})

test('nextIndex wraps both ways', () => {
  assert.equal(nextIndex(0, 4, 1), 1)
  assert.equal(nextIndex(3, 4, 1), 0)
  assert.equal(nextIndex(0, 4, -1), 3)
})

test('quotesFromCoingecko reads the four track coins', () => {
  const quotes = quotesFromCoingecko({
    bitcoin: { usd: 100000, usd_24h_change: 1.5 },
    ethereum: { usd: 3000, usd_24h_change: -2 },
    solana: { usd: 150, usd_24h_change: 0 },
    binancecoin: { usd: 600, usd_24h_change: 0.25 },
  })
  assert.equal(quotes.length, 4)
  assert.equal(quotes[0].symbol, 'BTC')
  assert.equal(quotes[2].usd, 150)
})

test('quotes page is glanceable and names the focused coin', () => {
  const text = renderQuotesPage({
    quotes: [
      { id: 'bitcoin', symbol: 'BTC', usd: 100000, change24h: 1.5 },
      { id: 'ethereum', symbol: 'ETH', usd: 3000, change24h: -2 },
      { id: 'solana', symbol: 'SOL', usd: 150, change24h: 0 },
      { id: 'binancecoin', symbol: 'BNB', usd: 600, change24h: 0.25 },
    ],
    selected: 0,
    live: true,
    alertCount: 0,
    clock: '14:32',
  })
  assert.match(text, /GLANCEPX  14:32  live/)
  assert.match(text, /> BTC/)
  assert.match(text, /TAP confirm \+5% alert on BTC/)
})

test('confirm page is a one-tap paper write, not a live order', () => {
  const text = renderConfirmPage({ id: 'bitcoin', symbol: 'BTC', usd: 100000, change24h: 1 })
  assert.match(text, /SET PAPER ALERT/)
  assert.match(text, /105,000/)
  assert.match(text, /No order is sent/)
})
