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

// ---- Club action plan ----

export function useActionPlan() {
  return useQuery({
    queryKey: ['club', 'actions'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/club/actions')
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}

export function useClubBaseline() {
  return useQuery({
    queryKey: ['club', 'baseline'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/club/baseline')
      if (error) throw error
      return data
    },
    staleTime: Infinity,
  })
}
