import { screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ClubLayout } from '@/components/club/ClubLayout'
import { renderWithProviders } from '@/test/render'
import { ClubProvider } from '@/state/club'
import { OverviewPage } from '@/pages/OverviewPage'
import { AffordabilityTab } from './AffordabilityTab'
import { EnergyTab } from './EnergyTab'
import { ShareTab } from './ShareTab'
import { SourcesTab } from './SourcesTab'
import { TravelTab } from './TravelTab'

// API calls stay pending: we only check that every page renders without crashing.
beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => new Promise(() => {})),
  )
  vi.stubGlobal(
    'ResizeObserver',
    class {
      observe() {}
      unobserve() {}
      disconnect() {}
    },
  )
})
afterEach(() => vi.unstubAllGlobals())

describe('club tabs', () => {
  it('shows all tab links', () => {
    renderWithProviders(<ClubLayout />)
    for (const name of ['Overview', 'Energy', 'Travel', 'Share', 'Affordability', 'Sources'])
      expect(screen.getByRole('link', { name: new RegExp(name) })).toBeInTheDocument()
  })

  it.each([
    ['Overview', OverviewPage],
    ['Energy', EnergyTab],
    ['Travel', TravelTab],
    ['Share', ShareTab],
    ['Affordability', AffordabilityTab],
    ['Sources', SourcesTab],
  ])('%s renders', (_, Page) => {
    const { container } = renderWithProviders(
      <ClubProvider>
        <Page />
      </ClubProvider>,
    )
    expect(container.firstChild).not.toBeNull()
  })
})
