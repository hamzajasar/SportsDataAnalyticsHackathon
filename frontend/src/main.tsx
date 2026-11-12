import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { TooltipProvider } from '@/components/ui/tooltip'
import { queryClient } from '@/api/queryClient'
import { LanguageProvider } from '@/i18n'
import { ClubProvider } from '@/state/club'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <LanguageProvider>
        <TooltipProvider>
          <ClubProvider>
            <App />
          </ClubProvider>
        </TooltipProvider>
      </LanguageProvider>
    </QueryClientProvider>
  </StrictMode>,
)
