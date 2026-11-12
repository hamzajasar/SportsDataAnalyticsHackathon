import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { api } from './client'

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

export function useSampleStats() {
  return useQuery({
    queryKey: ['sample', 'stats'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/sample/stats')
      if (error) throw error
      return data
    },
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
