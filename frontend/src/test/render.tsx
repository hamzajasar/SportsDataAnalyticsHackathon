import type { ReactNode } from 'react'
import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { LanguageProvider } from '@/i18n'

/** Render a component with the same providers the app uses (React Query + Router). */
export function renderWithProviders(ui: ReactNode, { route = '/' } = {}) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <LanguageProvider>
        <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
      </LanguageProvider>
    </QueryClientProvider>,
  )
}
