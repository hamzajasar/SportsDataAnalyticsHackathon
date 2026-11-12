/** Human-readable message from fetch errors, FastAPI `{detail}` bodies, or Errors. */
export function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (error && typeof error === 'object' && 'detail' in error) {
    const d = (error as { detail: unknown }).detail
    return typeof d === 'string' ? d : JSON.stringify(d)
  }
  return 'Request failed. Is the backend running (make dev)?'
}
