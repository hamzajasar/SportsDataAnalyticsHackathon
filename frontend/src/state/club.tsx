import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'
import { useSampleClub, type ClubProfile } from '@/api/queries'
import { toProfile } from '@/lib/club'

const STORAGE_KEY = 'club-profile-v1'

type ClubState = {
  /** The club every tab calculates for (sample club until the user edits it). */
  club: ClubProfile | null
  /** Send this to the API: null = sample club (backend marks results as illustrative). */
  requestClub: ClubProfile | null
  isSample: boolean
  isLoading: boolean
  setClub: (c: ClubProfile) => void
  resetToSample: () => void
}

const ClubContext = createContext<ClubState | null>(null)

function readSaved(): ClubProfile | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as ClubProfile) : null
  } catch {
    return null
  }
}

export function ClubProvider({ children }: { children: ReactNode }) {
  const sample = useSampleClub()
  const [custom, setCustom] = useState<ClubProfile | null>(readSaved)

  const setClub = useCallback((c: ClubProfile) => {
    setCustom(c)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(c))
    } catch {
      /* storage unavailable: edits still work for this session */
    }
  }, [])

  const resetToSample = useCallback(() => {
    setCustom(null)
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      /* ignore */
    }
  }, [])

  const value = useMemo<ClubState>(() => {
    const sampleProfile = sample.data ? toProfile(sample.data) : null
    return {
      club: custom ?? sampleProfile,
      requestClub: custom,
      isSample: custom === null,
      isLoading: custom === null && sample.isLoading,
      setClub,
      resetToSample,
    }
  }, [custom, sample.data, sample.isLoading, setClub, resetToSample])

  return <ClubContext.Provider value={value}>{children}</ClubContext.Provider>
}

// oxlint-disable-next-line react/only-export-components -- hook belongs with its provider
export function useClub(): ClubState {
  const ctx = useContext(ClubContext)
  if (!ctx) throw new Error('useClub must be used inside <ClubProvider>')
  return ctx
}
