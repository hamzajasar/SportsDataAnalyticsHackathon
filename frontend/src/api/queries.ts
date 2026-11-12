import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api } from './client'
import type { components } from './schema'

// Pattern: one hook per endpoint. Types come from the generated schema (`npm run gen:api`).

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/health')
      if (error) throw error
      return data
    },
    refetchInterval: 10_000,
  })
}

// ---- Datasets (generic explorer over data/raw) ----

export type DatasetPreviewParams = {
  limit?: number
  offset?: number
  sort?: string | null
  desc?: boolean
}

export function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/datasets')
      if (error) throw error
      return data
    },
  })
}

export function useDatasetPreview(id: string | undefined, params: DatasetPreviewParams = {}) {
  return useQuery({
    queryKey: ['datasets', id, 'preview', params],
    enabled: !!id,
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/datasets/preview', {
        params: { query: { id: id!, ...params } },
      })
      if (error) throw error
      return data
    },
  })
}

export function useDatasetSummary(id: string | undefined) {
  return useQuery({
    queryKey: ['datasets', id, 'summary'],
    enabled: !!id,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/datasets/summary', {
        params: { query: { id: id! } },
      })
      if (error) throw error
      return data
    },
  })
}

// ---- Sustainability (Topic 6) ----

export type TripRequest = components['schemas']['TripRequest']

export function useGridIntensity(countries: string[], fromYear = 2010) {
  return useQuery({
    queryKey: ['sustainability', 'grid', countries, fromYear],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/sustainability/grid-intensity', {
        params: { query: { countries, from_year: fromYear } },
      })
      if (error) throw error
      return data
    },
  })
}

export function useElectricityMix(country = 'BIH') {
  return useQuery({
    queryKey: ['sustainability', 'mix', country],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/sustainability/electricity-mix', {
        params: { query: { country } },
      })
      if (error) throw error
      return data
    },
  })
}

export function useEmissionFactors(category?: string) {
  return useQuery({
    queryKey: ['sustainability', 'factors', category],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/sustainability/factors', {
        params: { query: { category } },
      })
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}

export function useTripComparison(req: TripRequest, enabled = true) {
  return useQuery({
    queryKey: ['sustainability', 'trip', req],
    enabled,
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/sustainability/trip', { body: req })
      if (error) throw error
      return data
    },
  })
}

// ---- Club (profile, baseline, action plan, sources) ----

export type ClubProfile = components['schemas']['ClubProfile']

/** Body for club calculations: `club: null` = the illustrative sample club. */
function clubBody(club: ClubProfile | null) {
  return club ? { club } : {}
}

export function useSampleClub() {
  return useQuery({
    queryKey: ['club', 'sample'],
    staleTime: Infinity,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/club/sample')
      if (error) throw error
      return data
    },
  })
}

export function useClubBaseline(club: ClubProfile | null) {
  return useQuery({
    queryKey: ['club', 'baseline', club],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/baseline', { body: clubBody(club) })
      if (error) throw error
      return data
    },
  })
}

export function useActionPlan(club: ClubProfile | null) {
  return useQuery({
    queryKey: ['club', 'actions', club],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/actions', { body: clubBody(club) })
      if (error) throw error
      return data
    },
  })
}

export function useSources() {
  return useQuery({
    queryKey: ['sources'],
    staleTime: Infinity,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/sources')
      if (error) throw error
      return data
    },
  })
}

export function useShareSuggestions(
  lat: number | undefined,
  lon: number | undefined,
  radiusKm = 10,
) {
  return useQuery({
    queryKey: ['share', lat, lon, radiusKm],
    enabled: lat !== undefined && lon !== undefined,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/share/suggestions', {
        params: { query: { lat: lat!, lon: lon!, radius_km: radiusKm, n: 6 } },
      })
      if (error) throw error
      return data
    },
  })
}
