"use client";

import { useState } from "react";
import { runJob } from "@/lib/api";

type JobLog = {
  id: number;
  job_name: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  records_processed: number;
  error_message: string;
};

const jobs = ["news", "weather", "traffic", "risk", "alerts", "geospatial"];

export function JobRunnerClient({ initialLogs }: { initialLogs: JobLog[] }) {
  const [logs, setLogs] = useState(initialLogs);
  const [runningJob, setRunningJob] = useState("");

  async function run(jobName: string) {
    setRunningJob(jobName);
    try {
      const result = await runJob(jobName);
      setLogs((current) => [result as JobLog, ...current]);
    } finally {
      setRunningJob("");
    }
  }

  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {jobs.map((job) => (
          <button
            className="rounded-md bg-civic-blue px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
            disabled={runningJob === job}
            key={job}
            onClick={() => run(job)}
          >
            Run {job}
          </button>
        ))}
      </div>
      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              <th className="py-2">Job</th>
              <th>Status</th>
              <th>Started</th>
              <th>Completed</th>
              <th>Records</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, index) => (
              <tr className="border-t border-slate-100" key={`${log.id}-${index}`}>
                <td className="py-3">{log.job_name}</td>
                <td>{log.status}</td>
                <td>{log.started_at}</td>
                <td>{log.completed_at || "-"}</td>
                <td>{log.records_processed}</td>
                <td>{log.error_message || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
