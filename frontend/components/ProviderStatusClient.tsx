"use client";

import { useEffect, useState } from "react";
import { getProviderStatus, ProviderStatus, testProvider } from "@/lib/api";

const providerTypes = ["all", "news", "weather", "traffic", "geospatial"];

export function ProviderStatusClient() {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [message, setMessage] = useState("");

  async function load() {
    setProviders(await getProviderStatus());
  }

  useEffect(() => {
    load().catch(() => setMessage("Provider status is unavailable."));
  }, []);

  async function runTest(providerType: string) {
    setMessage(`Testing ${providerType} provider...`);
    await testProvider(providerType);
    await load();
    setMessage(`Provider test complete: ${providerType}`);
  }

  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-wrap gap-2">
        {providerTypes.map((providerType) => (
          <button className="rounded-md bg-civic-blue px-3 py-2 text-sm font-semibold text-white" key={providerType} onClick={() => runTest(providerType)} type="button">
            Test {providerType}
          </button>
        ))}
      </div>
      {message ? <p className="mb-3 rounded-md bg-slate-50 p-3 text-sm">{message}</p> : null}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              <th className="py-2">Provider</th>
              <th>Type</th>
              <th>Configured</th>
              <th>Health</th>
              <th>Last Success</th>
              <th>Last Failure</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {providers.map((provider) => (
              <tr className="border-t border-slate-100" key={provider.provider_name}>
                <td className="py-3 font-medium">{provider.provider_name}</td>
                <td>{provider.provider_type}</td>
                <td>{provider.configured ? "Yes" : "No"}</td>
                <td>{provider.health_status}</td>
                <td>{provider.last_success_at || "-"}</td>
                <td>{provider.last_failure_at || "-"}</td>
                <td>{provider.last_error || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
