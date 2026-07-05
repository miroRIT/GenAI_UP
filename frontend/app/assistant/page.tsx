import { ChatPanel } from "@/components/ChatPanel";
import { Nav } from "@/components/Nav";

const sampleQuestions = [
  "Which wards need urgent action this week?",
  "Why is Ward 4 classified as high risk?",
  "Are there any anomalies in air quality?",
  "Which areas have both high complaints and poor healthcare access?",
  "What should city officials prioritize tomorrow?",
];

export default function AssistantPage() {
  return (
    <main>
      <Nav />
      <div className="mx-auto grid max-w-7xl gap-6 px-5 py-6 lg:grid-cols-[0.8fr_1.2fr]">
        <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
          <h1 className="text-2xl font-bold text-civic-ink">Ask CivicIQ</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The assistant returns a structured analytical response with evidence, risk level,
            recommended actions, retrieved sources, and data limitations.
          </p>
          <div className="mt-5 space-y-2">
            {sampleQuestions.map((question) => (
              <div className="rounded-md bg-slate-50 p-3 text-sm text-slate-700" key={question}>{question}</div>
            ))}
          </div>
        </section>
        <ChatPanel />
      </div>
    </main>
  );
}
