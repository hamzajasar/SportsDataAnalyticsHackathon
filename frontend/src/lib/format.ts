import { getCurrentLang } from '@/i18n'

function locale(): string {
  return getCurrentLang() === 'bs' ? 'bs-BA' : 'en-GB'
}

export const formatNumber = (n: number, digits = 0) =>
  n.toLocaleString(locale(), { maximumFractionDigits: digits })

export function monthName(monthIndex: number, style: 'long' | 'short' = 'short'): string {
  return new Intl.DateTimeFormat(locale(), { month: style }).format(new Date(2000, monthIndex, 1))
}
