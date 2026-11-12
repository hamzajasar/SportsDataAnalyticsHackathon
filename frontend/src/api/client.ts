import createClient from 'openapi-fetch'
import type { paths } from './schema'

// In dev, Vite proxies /api -> FastAPI (see vite.config.ts).
// In production set VITE_API_URL to the deployed backend origin.
export const api = createClient<paths>({ baseUrl: import.meta.env.VITE_API_URL ?? '' })
