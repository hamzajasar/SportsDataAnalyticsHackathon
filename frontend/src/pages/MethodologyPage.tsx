import type { ReactNode } from 'react'
import { AlertTriangle, Database, FlaskConical, HeartHandshake, Target, Users } from 'lucide-react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { project } from '@/content/project'

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
  return (
    <div className="space-y-6">
      <PageHeader title="How it works" description={project.pitch} />
      <div className="grid gap-4 lg:grid-cols-2">
        <Section icon={Target} title="The problem">
          <Facts
            items={[
              { label: 'For', value: project.problem.who },
              { label: 'Decision', value: project.problem.decision },
            ]}
          />
        </Section>
        <Section icon={Database} title="Data">
          <Facts items={project.data} />
        </Section>
        <Section icon={FlaskConical} title="Method & validation">
          <Facts items={project.method} />
        </Section>
        <Section icon={AlertTriangle} title="Limitations">
          <ul className="list-disc space-y-1 pl-4">
            {project.limitations.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
        </Section>
        <Section icon={HeartHandshake} title="Impact & inclusion">
          <Facts items={project.impact} />
        </Section>
        <Section icon={Users} title="Team">
          <ul className="space-y-1">
            {project.team.map((m) => (
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
