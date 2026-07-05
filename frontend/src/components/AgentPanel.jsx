import { Send } from "lucide-react";
import { useState } from "react";

import { queryUrbanAgent } from "../services/api.js";

export default function AgentPanel() {
  const [query, setQuery] = useState("Where should we intervene for traffic and emergency response?");
  const [agentResponse, setAgentResponse] = useState(null);
  const [isThinking, setIsThinking] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setIsThinking(true);
    setErrorMessage("");

    try {
      const response = await queryUrbanAgent(query);
      setAgentResponse(response);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsThinking(false);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Urban Decision Intelligence Assistant</h2>

      <form className="mt-4 flex gap-2" onSubmit={handleSubmit}>
        <input
          className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-civic-signal focus:ring-2 focus:ring-blue-100"
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask about traffic, AQI, dispatch pressure..."
          value={query}
        />
        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-md bg-civic-signal text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isThinking || query.trim().length === 0}
          title="Ask assistant"
          type="submit"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>

      {errorMessage ? (
        <p className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {errorMessage}
        </p>
      ) : null}

      {agentResponse ? (
        <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm leading-6 text-slate-800">{agentResponse.answer}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs font-medium text-slate-600">
            <span className="rounded-md bg-white px-2 py-1">
              Focus: {agentResponse.data_focus}
            </span>
            <span className="rounded-md bg-white px-2 py-1">
              Confidence: {agentResponse.confidence_score}
            </span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
