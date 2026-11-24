import {
  waitForEvenAppBridge,
  TextContainerProperty,
  CreateStartUpPageContainer,
  TextContainerUpgrade,
  OsEventTypeList,
} from '@evenrealities/even_hub_sdk'
import {
  type Quote,
  FALLBACK_QUOTES,
  alertTarget,
  clockHm,
  fetchQuotes,
  renderConfirmPage,
  renderDonePage,
  renderQuotesPage,
  nextIndex,
} from './prices'

type Page = 'quotes' | 'confirm' | 'done'

const REFRESH_MS = 30_000
const MAIN_ID = 1
const MAIN_NAME = 'main'

const bridge = await waitForEvenAppBridge()

let page: Page = 'quotes'
let selected = 0
let quotes: Quote[] = FALLBACK_QUOTES.map((q) => ({ ...q }))
let live = false
let lastTarget = 0
const alerts: { symbol: string; target: number; setAt: number }[] = []

function screenText(): string {
  if (page === 'confirm') {
    const q = quotes[selected]
    return q ? renderConfirmPage(q) : 'No quote selected.\n2xTAP to go back.'
  }
  if (page === 'done') {
    const q = quotes[selected]
    return q ? renderDonePage(q, lastTarget) : 'Alert saved.\nTAP to go back.'
  }
  return renderQuotesPage({
    quotes,
    selected,
    live,
    alertCount: alerts.length,
    clock: clockHm(),
  })
}

async function paint(rebuild = false): Promise<void> {
  const content = screenText()
  if (rebuild) {
    await bridge.createStartUpPageContainer(
      new CreateStartUpPageContainer({
        containerTotalNum: 1,
        textObject: [
          new TextContainerProperty({
            xPosition: 0,
            yPosition: 0,
            width: 576,
            height: 288,
            borderWidth: 0,
            borderColor: 5,
            paddingLength: 4,
            containerID: MAIN_ID,
            containerName: MAIN_NAME,
            content,
            isEventCapture: 1,
          }),
        ],
      }),
    )
    return
  }
  await bridge.textContainerUpgrade(
    new TextContainerUpgrade({
      containerID: MAIN_ID,
      containerName: MAIN_NAME,
      content,
    }),
  )
}

async function refreshQuotes(): Promise<void> {
  try {
    quotes = await fetchQuotes()
    live = true
  } catch (err) {
    live = false
    console.warn('CoinGecko fetch failed, using cached quotes', err)
  }
  if (page === 'quotes') await paint()
}

function eventTypeOf(envelope?: { eventType?: OsEventTypeList }): OsEventTypeList | null {
  // CLICK_EVENT is 0; protobuf omits zero-value fields, so a single tap
  // arrives as an envelope whose eventType is undefined.
  if (!envelope) return null
  return envelope.eventType ?? OsEventTypeList.CLICK_EVENT
}

function isSwipeNext(type: OsEventTypeList | null): boolean {
  if (type === null) return false
  const enumObj = OsEventTypeList as unknown as Record<string, number>
  const names = ['SWIPE_UP_EVENT', 'SWIPE_DOWN_EVENT', 'SLIDE_UP_EVENT', 'SLIDE_DOWN_EVENT', 'SCROLL_EVENT']
  return names.some((name) => type === enumObj[name])
}

function onTap(): void {
  if (page === 'quotes') {
    page = 'confirm'
    void paint()
    return
  }
  if (page === 'confirm') {
    const q = quotes[selected]
    if (!q) return
    lastTarget = alertTarget(q.usd)
    alerts.push({ symbol: q.symbol, target: lastTarget, setAt: Date.now() })
    page = 'done'
    void paint()
    return
  }
  page = 'quotes'
  void paint()
}

function onDoubleTap(): void {
  if (page === 'quotes') {
    // Root page must show the system exit-confirmation dialog (mode 1).
    bridge.shutDownPageContainer(1)
    return
  }
  page = 'quotes'
  void paint()
}

function onSwipe(delta: number): void {
  if (page !== 'quotes') return
  selected = nextIndex(selected, quotes.length, delta)
  void paint()
}

const created = await bridge.createStartUpPageContainer(
  new CreateStartUpPageContainer({
    containerTotalNum: 1,
    textObject: [
      new TextContainerProperty({
        xPosition: 0,
        yPosition: 0,
        width: 576,
        height: 288,
        borderWidth: 0,
        borderColor: 5,
        paddingLength: 4,
        containerID: MAIN_ID,
        containerName: MAIN_NAME,
        content: screenText(),
        isEventCapture: 1,
      }),
    ],
  }),
)

if (created !== 0) {
  console.error('createStartUpPageContainer failed:', created)
}

const unsubscribe = bridge.onEvenHubEvent((event) => {
  const sysType = eventTypeOf(event.sysEvent)
  const textType = eventTypeOf(event.textEvent)

  if (sysType === OsEventTypeList.DOUBLE_CLICK_EVENT || textType === OsEventTypeList.DOUBLE_CLICK_EVENT) {
    onDoubleTap()
    return
  }

  if (isSwipeNext(sysType) || isSwipeNext(textType)) {
    const enumObj = OsEventTypeList as unknown as Record<string, number>
    const down = [enumObj.SWIPE_DOWN_EVENT, enumObj.SLIDE_DOWN_EVENT].includes(
      (sysType ?? textType) as number,
    )
    onSwipe(down ? 1 : -1)
    return
  }

  if (sysType === OsEventTypeList.CLICK_EVENT || textType === OsEventTypeList.CLICK_EVENT) {
    onTap()
    return
  }

  if (sysType === OsEventTypeList.SYSTEM_EXIT_EVENT || sysType === OsEventTypeList.ABNORMAL_EXIT_EVENT) {
    unsubscribe()
  }
})

void refreshQuotes()
setInterval(() => {
  void refreshQuotes()
}, REFRESH_MS)
