import { ChatPanel } from "@/components/ChatPanel";
import { Nav } from "@/components/Nav";
import { PageHeader, SectionCard, StatusBadge } from "@/components/UIPrimitives";

export default function AssistantPage() {
  return (
    <main>
      <Nav />
      <div className="mx-auto max-w-7xl px-5 py-6">
        <PageHeader eyebrow="AI Assistant" title="Ask CivicIQ" description="Every demo response is grounded in the same seeded NCR evidence used by Demo Mode, maps, recommendations, and incident briefs." />
        <div className="grid gap-6 lg:grid-cols-[0.75fr_1.25fr]">
          <SectionCard title="Response Format" badge={<StatusBadge label="Responsible AI" tone="green" />}>
            <div className="space-y-2 text-sm text-slate-700">
              {["Executive Summary", "Evidence Used", "Risk Level", "Recommended Actions", "Responsible Departments", "Confidence", "Data Freshness", "Limitations"].map((item) => (
                <div className="rounded-md bg-slate-50 p-3" key={item}>{item}</div>
              ))}
            </div>
          </SectionCard>
          <ChatPanel />
        </div>
      </div>
    </main>
  );
}
