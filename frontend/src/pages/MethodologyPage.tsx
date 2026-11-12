import type { ReactNode } from 'react'
import { AlertTriangle, Database, FlaskConical, HeartHandshake, Target, Users } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { projectContent } from '@/content/project'
import { useT } from '@/i18n'

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: typeof Database
  title: string
  children: ReactNode
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Icon className="size-4 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="text-sm">{children}</CardContent>
    </Card>
  )
}

function Facts({ items }: { items: { label: string; value: string }[] }) {
  return (
    <dl className="grid gap-2">
      {items.map((i) => (
        <div key={i.label} className="grid gap-0.5 sm:grid-cols-[120px_1fr] sm:gap-3">
          <dt className="text-muted-foreground">{i.label}</dt>
          <dd>{i.value}</dd>
        </div>
      ))}
    </dl>
  )
}

export function MethodologyPage() {
  const { t, lang } = useT()
  const p = projectContent[lang] ?? projectContent.en

  return (
    <div className="space-y-6">
      <PageHeader title={t('method.title')} description={p.pitch} />
      <div className="grid gap-4 lg:grid-cols-2">
        <Section icon={Target} title={t('method.problem')}>
          <Facts
            items={[
              { label: t('method.for'), value: p.problem.who },
              { label: t('method.decision'), value: p.problem.decision },
            ]}
          />
        </Section>
        <Section icon={Database} title={t('method.data')}>
          <Facts items={p.data} />
        </Section>
        <Section icon={FlaskConical} title={t('method.method')}>
          <Facts items={p.method} />
        </Section>
        <Section icon={AlertTriangle} title={t('method.limitations')}>
          <ul className="list-disc space-y-1 pl-4">
            {p.limitations.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </Section>
        <Section icon={HeartHandshake} title={t('method.impact')}>
          <Facts items={p.impact} />
        </Section>
        <Section icon={Users} title={t('method.team')}>
          <ul className="space-y-1">
            {p.team.map((m) => (
              <li key={m.name + m.role}>
                <span className="font-medium">{m.name}</span>{' '}
                <span className="text-muted-foreground">– {m.role}</span>
              </li>
            ))}
          </ul>
        </Section>
      </div>
    </div>
  )
}
