export function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-civic-ink">{title}</h2>
      {children}
    </section>
  );
}
