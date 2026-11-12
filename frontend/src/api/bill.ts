import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { components } from '@/api/schema'
import type { ClubProfile } from '@/state/club'

export type ConfirmedBill = components['schemas']['ConfirmedBill']
export type BillAnalysis = components['schemas']['BillAnalysis']

/** Waste check, updated plan and Bosnian board text for one bill the user typed in. */
export function useAnalyseBill(
  club: ClubProfile | null,
  bill: ConfirmedBill | null,
  meanTempC: number | null,
) {
  return useQuery({
    queryKey: ['club', 'bill', club, bill, meanTempC],
    enabled: bill !== null,
    retry: false,
    queryFn: async () => {
      const { data, error } = await api.POST('/api/club/bill/analyse', {
        body: { club: club ?? null, bill: bill as ConfirmedBill, mean_temp_c: meanTempC },
      })
      if (error) throw error
      return data
    },
  })
}
