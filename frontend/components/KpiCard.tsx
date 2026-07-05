import { LucideIcon } from "lucide-react";

export function KpiCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
}) {
  return (
    <div className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm text-slate-500">{label}</p>
        <Icon className="h-5 w-5 text-civic-blue" aria-hidden="true" />
      </div>
      <p className="mt-3 text-2xl font-semibold text-civic-ink">{value}</p>
    </div>
  );
}
