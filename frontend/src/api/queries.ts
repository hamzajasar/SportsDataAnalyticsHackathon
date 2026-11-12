import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api } from './client'
import type { components } from './schema'

// Pattern: one hook per endpoint. Types come from the generated schema (`npm run gen:api`).

type ClubProfile = components['schemas']['ClubProfile']

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

// ---- Cities ----

export function useCities() {
  return useQuery({
    queryKey: ['cities'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/cities')
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}

// ---- Club static data ----

export function useSampleClub() {
  return useQuery({
    queryKey: ['club', 'sample'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/club/sample')
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}

export function useAssumptions() {
  return useQuery({
    queryKey: ['club', 'assumptions'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/club/assumptions')
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}

export function useSources() {
  return useQuery({
    queryKey: ['sources'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/sources')
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}

// ---- Club calculations (POST with club profile) ----

export function useActionPlan(club: ClubProfile | null) {
  return useQuery({
    queryKey: ['club', 'actions', club],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/actions', {
        body: { club: club ?? null },
      })
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
      const { data, error } = await api.POST('/api/club/baseline', {
        body: { club: club ?? null },
      })
      if (error) throw error
      return data
    },
  })
}

export function useEnergyProfile(club: ClubProfile | null, kwp: number) {
  return useQuery({
    queryKey: ['club', 'energy', club, kwp],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/energy', {
        body: { club: club ?? null, kwp },
      })
      if (error) throw error
      return data
    },
  })
}

export function useSeasonTravel(
  club: ClubProfile | null,
  people_per_trip: number,
  share_with_partner: boolean,
) {
  return useQuery({
    queryKey: ['club', 'travel', club, people_per_trip, share_with_partner],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/travel', {
        body: { club: club ?? null, people_per_trip, share_with_partner },
      })
      if (error) throw error
      return data
    },
  })
}

export function useAffordability(club: ClubProfile | null) {
  return useQuery({
    queryKey: ['club', 'affordability', club],
    placeholderData: keepPreviousData,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/affordability', {
        body: { club: club ?? null },
      })
      if (error) throw error
      return data
    },
  })
}

// ---- Venues & sharing ----

export function useShareSuggestions(
  lat: number | undefined,
  lon: number | undefined,
  radius_km: number,
) {
  return useQuery({
    queryKey: ['share', 'suggestions', lat, lon, radius_km],
    enabled: lat != null && lon != null,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/share/suggestions', {
        params: { query: { lat: lat!, lon: lon!, radius_km } },
      })
      if (error) throw error
      return data
    },
  })
}

export function useNearestVenues(
  lat: number | undefined,
  lon: number | undefined,
  n: number,
  leisure?: string,
) {
  return useQuery({
    queryKey: ['venues', 'nearest', lat, lon, n, leisure],
    enabled: lat != null && lon != null,
    queryFn: async () => {
      const { data, error } = await api.GET('/api/venues/nearest', {
        params: { query: { lat: lat!, lon: lon!, n, leisure } },
      })
      if (error) throw error
      return data
    },
  })
}
