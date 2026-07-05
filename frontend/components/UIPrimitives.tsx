import { LucideIcon } from "lucide-react";
import { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  children?: ReactNode;
}) {
  return (
    <header className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-civic-blue">{eyebrow}</p>
        <h1 className="mt-1 text-3xl font-bold text-civic-ink md:text-4xl">{title}</h1>
        {description ? <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p> : null}
      </div>
      {children}
    </header>
  );
}

export function CommandCenterShell({ children }: { children: ReactNode }) {
  return <div className="mx-auto max-w-7xl px-5 py-6 md:py-8">{children}</div>;
}

export function SectionCard({ title, children, badge }: { title?: string; children: ReactNode; badge?: ReactNode }) {
  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm md:p-5">
      {title ? (
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-civic-ink">{title}</h2>
          {badge}
        </div>
      ) : null}
      {children}
    </section>
  );
}

export function MetricCard({ icon: Icon, label, value, hint }: { icon?: LucideIcon; label: string; value: string | number; hint?: string }) {
  return (
    <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      {Icon ? <Icon className="h-5 w-5 text-civic-blue" /> : null}
      <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-civic-ink">{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-500">{hint}</p> : null}
    </div>
  );
}

export function StatusBadge({ label, tone = "slate" }: { label: string; tone?: "green" | "yellow" | "orange" | "red" | "blue" | "slate" }) {
  const toneClass = {
    green: "bg-emerald-100 text-emerald-700",
    yellow: "bg-yellow-100 text-yellow-800",
    orange: "bg-orange-100 text-orange-700",
    red: "bg-red-100 text-red-700",
    blue: "bg-blue-100 text-blue-700",
    slate: "bg-slate-100 text-slate-700",
  }[tone];
  return <span className={`inline-flex rounded-md px-2 py-1 text-xs font-semibold ${toneClass}`}>{label}</span>;
}

export function DemoBadge({ label = "Demo Scenario" }: { label?: string }) {
  return <StatusBadge label={label} tone="blue" />;
}

export function ProviderBadge({ live = false }: { live?: boolean }) {
  return <StatusBadge label={live ? "Live Provider" : "Simulated Provider"} tone={live ? "green" : "yellow"} />;
}

export function LoadingState({ label = "Loading CivicIQ data..." }: { label?: string }) {
  return <div className="rounded-lg border border-civic-line bg-white p-6 text-sm text-slate-600 shadow-sm">{label}</div>;
}

export function ErrorState({ label = "API unavailable. Start the backend and refresh this page." }: { label?: string }) {
  return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-700">{label}</div>;
}

export function EmptyState({ label }: { label: string }) {
  return <div className="rounded-lg border border-dashed border-slate-300 bg-white p-6 text-center text-sm text-slate-500">{label}</div>;
}
