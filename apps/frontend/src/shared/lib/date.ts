/**
 * KST 포맷 유틸 (spec: 000-foundation)
 */
export function formatToKST(iso: string): string {
  const d = new Date(iso)
  const f = new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
  const parts = f.formatToParts(d)
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? ''
  const y = get('year')
  const m = get('month')
  const day = get('day')
  const h = get('hour')
  const min = get('minute')
  return `${y}. ${m}. ${day}. ${h}:${min}`
}
