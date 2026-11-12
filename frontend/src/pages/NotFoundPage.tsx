import { Link } from 'react-router-dom'
import { useT } from '@/i18n'

export function NotFoundPage() {
  const { t } = useT()
  return (
    <div className="py-24 text-center">
      <h1 className="text-2xl font-semibold">{t('notFound.title')}</h1>
      <Link to="/" className="mt-2 inline-block text-sm text-primary underline">
        {t('notFound.back')}
      </Link>
    </div>
  )
}
