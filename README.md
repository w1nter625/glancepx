# GlancePx

A glance-and-act market ticker for [Even Realities G2](https://www.evenrealities.com) glasses. Built for the **Heads Up: Even Realities Hackathon** (Track 02 · Crypto & DeFi).

Phones pull you out of the moment. GlancePx puts four live USD quotes (BTC, ETH, SOL, BNB) on the 576×288 monochrome display, and lets you confirm a **paper +5% price alert** with one tap — no typing, no live order, no custody.

## What it does

- **Read:** live prices and 24h change from the public [CoinGecko](https://www.coingecko.com) API (a listed Track 02 app). Refreshes every 30 seconds. If the network is down, it falls back to on-device cached quotes and labels the screen `cached`.
- **Write:** one-tap confirm of a paper alert at +5% above the current price. The alert is stored on the device only. The confirm page says so: no order is sent, no funds are held. This matches the hackathon money-safety rule (testnet / paper / read-only).
- **Input:** temple tap to confirm, swipe to change the focused coin, double-tap to exit (root page uses the system exit dialog, as required by Even Hub QA).

Voice is left out of v1. The Even Hub SDK gives raw microphone audio only; speech-to-text would need a separately hosted model. A short phrase could later confirm the same paper alert.

## Screens (simulator or G2)

1. Quotes — four coins, `>` on the focused row, `TAP confirm +5% alert on BTC`.
2. Confirm — `BTC now 91,235` / `Alert if +5% → 95,797` / `TAP to confirm`.
3. Done — `ALERT SET (paper)` / `TAP back to quotes`.

## Setup

```bash
npm install
npm test
npm run dev          # terminal 1, Vite on http://localhost:5173
npm run simulate     # terminal 2, Even Hub simulator → 576×288 canvas
```

On a real G2, enable developer mode in the Even Realities app and run `evenhub qr --url "http://<LAN-IP>:5173"`.

Hardware is not required. The official [Even Hub simulator](https://hub.evenrealities.com/docs/getting-started/overview) is enough to build and demo.

## Project layout

```
app.json          Even Hub manifest (network whitelist: api.coingecko.com)
src/prices.ts     Quote fetch, formatting, and screen copy (unit-tested)
src/main.ts       Bridge, pages, tap / swipe / double-tap
public/icon.png   24×24 greyscale icon
test/             Node tests for formatting and page copy
```

This repository was written during the hackathon build window (after 2026-11-23). It uses the official Even Hub SDK, Vite, and the public CoinGecko API. No API keys are required or shipped.

## License

MIT. See [LICENSE](LICENSE).
