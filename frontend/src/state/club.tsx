import { createContext, useContext, useState, type ReactNode } from 'react'
import type { components } from '@/api/schema'

export type ClubProfile = components['schemas']['ClubProfile']

type ClubCtx = {
  club: ClubProfile | null
  requestClub: ClubProfile | null
  isSample: boolean
  setClub: (club: ClubProfile) => void
  resetToSample: () => void
}

const ClubContext = createContext<ClubCtx | null>(null)

const STORAGE_KEY = 'club_footprint_v1'

function loadFromStorage(): ClubProfile | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as ClubProfile) : null
  } catch {
    return null
  }
}

function saveToStorage(club: ClubProfile | null): void {
  try {
    if (club) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(club))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  } catch {
    /* storage unavailable */
  }
}

export function ClubProvider({ children }: { children: ReactNode }) {
  const [club, setClubState] = useState<ClubProfile | null>(loadFromStorage)

  const setClub = (c: ClubProfile) => {
    setClubState(c)
    saveToStorage(c)
  }

  const resetToSample = () => {
    setClubState(null)
    saveToStorage(null)
  }

  return (
    <ClubContext.Provider
      value={{
        club,
        requestClub: club,
        isSample: club === null,
        setClub,
        resetToSample,
      }}
    >
      {children}
    </ClubContext.Provider>
  )
}

export function useClub(): ClubCtx {
  const ctx = useContext(ClubContext)
  if (!ctx) throw new Error('useClub must be used within ClubProvider')
  return ctx
}
