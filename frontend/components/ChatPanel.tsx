"use client";

import { Send } from "lucide-react";
import { useState } from "react";
import { askCivicIq } from "@/lib/api";
import { ErrorState, LoadingState, SectionCard, StatusBadge } from "./UIPrimitives";

const sampleQuestions = [
  "Why is Gurugram critical right now?",
  "What evidence supports the Delhi public health alert?",
  "Which NCR districts need action in the next 24 hours?",
  "Generate a leadership summary for the NCR crisis.",
  "Which department should handle the Noida industrial risk?",
];

export function ChatPanel() {
  const [question, setQuestion] = useState(sampleQuestions[0]);
  const [response, setResponse] = useState<Awaited<ReturnType<typeof askCivicIq>> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function submitQuestion(event: React.FormEvent) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      setResponse(await askCivicIq(question));
    } catch {
      setError("CivicIQ could not answer right now. Check that the backend is running.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <SectionCard title="AI Assistant" badge={<StatusBadge label="Seeded Evidence" tone="blue" />}>
      <div className="mb-4 flex flex-wrap gap-2">
        {sampleQuestions.map((sample) => (
          <button className="rounded-md bg-slate-100 px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-200" key={sample} onClick={() => setQuestion(sample)} type="button">
            {sample}
          </button>
        ))}
      </div>
      <form className="mt-4 flex gap-2" onSubmit={submitQuestion}>
        <input
          className="min-w-0 flex-1 rounded-md border border-civic-line px-3 py-2 text-sm outline-none focus:border-civic-blue focus:ring-2 focus:ring-blue-100"
          onChange={(event) => setQuestion(event.target.value)}
          value={question}
        />
        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-md bg-civic-blue text-white disabled:opacity-60"
          disabled={isLoading || question.trim().length === 0}
          title="Ask CivicIQ"
          type="submit"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
      {isLoading ? <div className="mt-4"><LoadingState label="CivicIQ is grounding the response in seeded NCR evidence..." /></div> : null}
      {error ? <div className="mt-4"><ErrorState label={error} /></div> : null}
      {response ? (
        <div className="mt-4 space-y-4">
          <div className="rounded-md border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-800">
            {response.answer}
          </div>
          <div>
            <h3 className="text-sm font-semibold">Recommended Actions</h3>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {response.recommended_actions.slice(0, 5).map((action) => <li key={action}>{action}</li>)}
            </ul>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <InfoList title="Sources" items={response.sources.map((source) => `${source.source} · ${source.chunk_id}`)} />
            <InfoList title="Limitations" items={response.data_limitations} />
          </div>
        </div>
      ) : null}
    </SectionCard>
  );
}

function InfoList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <h3 className="text-sm font-semibold">{title}</h3>
      <ul className="mt-2 space-y-1 text-xs text-slate-600">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}
