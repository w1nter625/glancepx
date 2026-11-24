# GlancePx — DoraHacks BUIDL copy (do not submit until approved)

Hackathon: Heads Up: Even Realities Hackathon by TVM Ventures & Daos Hub  
Page: https://dorahacks.io/hackathon/even-realities  
Deadline: **2026-11-30 03:59 SGT** (2026-11-29 23:59 Dubai / GMT+4)  
Team: solo, Wynnter (DoraHacks @wynnter)  
Nothing below has been submitted. Do not post the video to YouTube or any social platform.

---

## Paste-ready fields

### Project name
GlancePx

### One-line description / tagline
A glance-and-act market ticker for Even Realities G2: live BTC, ETH, SOL and BNB, plus a one-tap paper price alert.

### Track
**02 · Crypto & DeFi** (CoinGecko)

### GitHub repository
https://github.com/w1nter625/glancepx

### Demo video
https://github.com/w1nter625/glancepx/releases/download/demo-v1/demo.mp4

Release page (if the form wants a generic “demo link” rather than a raw file):  
https://github.com/w1nter625/glancepx/releases/tag/demo-v1

Local copy: `/workspace/competitions-2/even-glancepx/demo.mp4` (70.2 seconds, 1080p, H.264 + AAC, English `en-US-AndrewNeural` TTS, burned-in captions). No on-camera appearance. Recorded from the official Even Hub simulator (Xvfb, `--automation-port`).

### Logo / cover
- Logo (1024×1024 PNG): `/workspace/competitions-2/even-glancepx/logo.png`  
  Also in the repo: https://github.com/w1nter625/glancepx/blob/main/logo.png  
  Release asset: https://github.com/w1nter625/glancepx/releases/download/demo-v1/logo.png
- Cover (1920×1080 PNG): `/workspace/competitions-2/even-glancepx/cover.png`  
  https://github.com/w1nter625/glancepx/blob/main/cover.png  
  https://github.com/w1nter625/glancepx/releases/download/demo-v1/cover.png

Use the square logo if the form asks for a project logo. Use the 16:9 cover if it asks for a banner or cover image.

### Website / live demo (optional)
Leave blank, or use the repository URL. There is no hosted WebView demo that renders the G2 canvas; the glasses UI only appears in the Even Hub simulator or on device.

### Tags (if asked)
`even-realities` `g2` `coingecko` `crypto` `defi` `wearable`

### Detailed description (English, concise — paste into the BUIDL “project details” box)

**Problem.** Checking a price still means taking out a phone. That is exactly what G2 is for: a private, glanceable display you can act on without leaving the moment.

**Who it is for.** People who already follow BTC, ETH, SOL or BNB and want a walking-friendly ticker, not a dashboard.

**What we built.** GlancePx is a Track 02 (Crypto & DeFi) Even Hub plugin. It reads live USD quotes and 24-hour change from the public CoinGecko API — one of the apps listed for this track — and draws them on the 576×288 monochrome G2 canvas. Swipe the temple to change the focused coin. One tap opens a confirm page with a +5% paper alert already computed; a second tap stores that alert on the device. The confirm screen states clearly that no order is sent and no funds are held, which follows the hackathon money-safety rule (testnet, paper trading, or read-only data).

**How it works.** The app is a Vite + TypeScript Even Hub plugin. `createStartUpPageContainer` / `textContainerUpgrade` drive the glasses UI. Quotes refresh every 30 seconds; if CoinGecko is unreachable, GlancePx falls back to cached figures and labels the screen `cached`. No API keys are required or shipped. The demo video is a capture of the official Even Hub simulator, not a mock UI.

**What existed before 23 November 2026.** Only third-party dependencies: the official Even Hub SDK, CLI and simulator, Vite, TypeScript, and the public CoinGecko API. All GlancePx source in this repository was written during the event.

### Short “problem / audience / how it works / track” blurb
(If the form has a shorter text box, use this.)

GlancePx helps people follow crypto prices without pulling out a phone. It is a Track 02 (Crypto & DeFi) G2 app that shows live BTC, ETH, SOL and BNB quotes from CoinGecko and lets you confirm a paper +5% alert with one tap. No live orders, no custody, no API keys.

---

## DoraHacks form: fields you will likely have to fill in the browser

Inferred from DoraHacks public docs (default BUIDL form used across 1,000+ hackathons; organizers can require GitHub and a demo video) and from this event’s own rules (GitHub/GitLab/Bitbucket link required, demo video required, pick one listed track). The live form was not opened, and no BUIDL was submitted. Custom questions, if any, are only visible after login.

**Before the BUIDL form**

1. Sign in to DoraHacks as **@wynnter** (existing account). Connect GitHub `w1nter625` if the form offers it — helpful, not done from here.
2. Open https://dorahacks.io/hackathon/even-realities and click **Register** / **Join** if not already registered for this hackathon.
3. Click **Submit BUIDL** → **Create new BUIDL** (do not reuse another project).

**Typical required or expected BUIDL fields**

| Field | Required? | What to paste / upload |
|---|---|---|
| Project name | Yes (default) | `GlancePx` |
| Logo | Usually yes | `logo.png` |
| Cover / banner | Sometimes | `cover.png` |
| One-line description | Yes (default) | Tagline above |
| Project details / description | Yes (default) | Long English description above |
| Track / category | Yes for this event | **02 · Crypto & DeFi** |
| GitHub / GitLab / Bitbucket URL | **Yes** (event tag + default) | `https://github.com/w1nter625/glancepx` |
| Demo video URL | **Yes** (event tag + organizers can require it) | The `demo.mp4` release URL. DoraHacks often previews YouTube links; this file is a direct GitHub Release asset instead, by request (no YouTube / social upload). If the form rejects a non-YouTube URL, stop and ask — do not upload to YouTube unless Wynnter approves. |
| Demo / website URL | Often optional | Repo URL, or leave blank |
| Tags | Optional | See tags above |
| Team members | Yes (default) | Solo: Wynnter |
| Social links (X, Telegram, Discord, etc.) | Optional | Leave blank. Do not post from a personal account. |
| Contact email | Often yes | `w1nter625720@gmail.com` |
| Custom questions | Unknown until the form is open | Likely topics, if present: listed Track 02 app used (**CoinGecko**); whether the demo is simulator or hardware (**official Even Hub simulator**); what existed before 23 Nov (**dependencies only, listed in the description**). Optional `.ehpk` package was not built. |

**After submit (do not do this until approved)**

Organizer review is separate from the platform save. The BUIDL may not appear in the gallery until it is accepted. Demo Day for finalists is 2026-12-03 18:00–22:00 SGT and may be remote; that slot could involve a live English walkthrough. The submitted video itself does not require appearing on camera.

---

## Build notes

- Swipe on the official simulator/firmware arrives as `textEvent` `SCROLL_TOP_EVENT` (1) / `SCROLL_BOTTOM_EVENT` (2). The app was updated to handle those events (the first draft looked for names the SDK does not define).
- Simulator glasses screenshots are RGBA green with alpha; they must be composited onto black to be visible.
- Demo rebuild: `SKIP_CAPTURE=1 python3 video/build_demo.py` (reuses official-simulator shots under `/tmp/glancepx-demo/shots`). Full recapture needs the official `evenhub-simulator` with `--automation-port 9898` and Vite on port 5173.
