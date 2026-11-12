import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { renderWithProviders } from '@/test/render'
import { MethodologyPage } from './MethodologyPage'

describe('MethodologyPage', () => {
  it('renders every judging-relevant section', () => {
    renderWithProviders(<MethodologyPage />)
    for (const title of [
      'The problem',
      'Data',
      'Method & validation',
      'Limitations',
      'Impact & inclusion',
    ]) {
      expect(screen.getByText(title)).toBeInTheDocument()
    }
  })
})
