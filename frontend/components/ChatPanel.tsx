"use client";

import { Send } from "lucide-react";
import { useState } from "react";
import { askCivicIq } from "@/lib/api";

export function ChatPanel() {
  const [question, setQuestion] = useState("Which wards need urgent action this week?");
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
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">AI Assistant</h2>
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
      {error ? <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : null}
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
    </section>
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
