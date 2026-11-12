import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { queryClient } from '@/api/queryClient'
import { en } from './en'
import { bs } from './bs'

export type Lang = 'en' | 'bs'
type Vars = Record<string, string | number>
type Dict = typeof en

export type { Dict }

const dicts: Record<Lang, Dict> = { en, bs }

// Module-level for use outside React (middleware, format.ts)
let _lang: Lang = 'en'
export function getCurrentLang(): Lang {
  return _lang
}

function detectLang(): Lang {
  try {
    const stored = localStorage.getItem('lang_pref')
    if (stored === 'en' || stored === 'bs') return stored as Lang
  } catch {
    /* storage unavailable */
  }
  const browser = navigator.language.toLowerCase()
  if (browser.startsWith('bs') || browser.startsWith('hr') || browser.startsWith('sr')) return 'bs'
  return 'en'
}

function interpolate(str: string, vars?: Vars): string {
  if (!vars) return str
  return str.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? `{${k}}`))
}

type LangCtx = {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: keyof Dict, vars?: Vars) => string
}

const LangContext = createContext<LangCtx | null>(null)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(detectLang)

  useEffect(() => {
    _lang = lang
    document.documentElement.lang = lang
  }, [lang])

  const setLang = (l: Lang) => {
    setLangState(l)
    _lang = l
    document.documentElement.lang = l
    try {
      localStorage.setItem('lang_pref', l)
    } catch {
      /* storage unavailable */
    }
    void queryClient.invalidateQueries()
  }

  const t = (key: keyof Dict, vars?: Vars): string => {
    const str =
      (dicts[lang] as Record<string, string>)[key] ?? (en as Record<string, string>)[key] ?? key
    return interpolate(str, vars)
  }

  return <LangContext.Provider value={{ lang, setLang, t }}>{children}</LangContext.Provider>
}

export function useT(): LangCtx {
  const ctx = useContext(LangContext)
  if (!ctx) throw new Error('useT must be used within LanguageProvider')
  return ctx
}
