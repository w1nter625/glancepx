# GlancePx — Heads Up hackathon submission notes

- **Hackathon:** Heads Up: Even Realities Hackathon by TVM Ventures & Daos Hub
- **Page:** https://dorahacks.io/hackathon/even-realities
- **Track:** 02 · Crypto & DeFi (CoinGecko)
- **Deadline:** 2026-11-29 23:59 Dubai time (GMT+4) = **2026-11-30 03:59 SGT**
- **Team:** solo, Wynnter
- **Repo:** (public GitHub link, filled in after the repo is created)
- **Demo video:** pending (screen recording of the official Even Hub simulator, ≤ 3 minutes, English narration + burned-in captions; no on-camera appearance)

## Short description

GlancePx is a G2 ticker for people who want prices without pulling out a phone. It shows live BTC, ETH, SOL and BNB quotes from CoinGecko on the 576×288 monochrome display, and a single tap confirms a paper +5% price alert stored on the device. No live orders, no custody, no API keys.

## How it works

1. The app talks to the glasses through the Even Hub SDK (`createStartUpPageContainer` / `textContainerUpgrade`).
2. Quotes come from `https://api.coingecko.com/api/v3/simple/price` (whitelisted in `app.json`).
3. Tap opens a confirm page with the +5% target already computed — one more tap writes the paper alert.
4. Swipe cycles the focused coin. Double-tap on the quotes page shows the system exit dialog.

## What existed before 23 Nov 2026

Only third-party dependencies: official Even Hub SDK / CLI / simulator, Vite, TypeScript, and the public CoinGecko API. All GlancePx source in this repository was written during the event.

## Demo Day

Finalists demo on 2026-12-03 14:00–18:00 Dubai time (18:00–22:00 SGT), on site or remotely. If this project is a finalist, the live remote slot needs a decision from Wynnter (it may involve a spoken English walkthrough). The submitted video itself is a pre-recorded simulator capture with captions / TTS, not a live appearance.
