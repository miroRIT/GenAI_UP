"use client";

import { useState } from "react";
import { login } from "@/lib/api";

const demoUsers = [
  ["admin@civiciq.demo", "Admin@12345", "Admin"],
  ["officer@civiciq.demo", "Officer@12345", "District Officer"],
  ["analyst@civiciq.demo", "Analyst@12345", "Analyst"],
  ["viewer@civiciq.demo", "Viewer@12345", "Viewer"],
];

export function AuthPanel() {
  const [email, setEmail] = useState(demoUsers[0][0]);
  const [password, setPassword] = useState(demoUsers[0][1]);
  const [message, setMessage] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    try {
      const result = await login(email, password);
      localStorage.setItem("civiciq_token", result.access_token);
      localStorage.setItem("civiciq_user", JSON.stringify(result.user));
      setMessage(`Logged in as ${result.user.full_name} (${result.user.role})`);
    } catch {
      setMessage("Login failed. Check backend and credentials.");
    }
  }

  return (
    <section className="rounded-lg border border-civic-line bg-white p-5 shadow-sm">
      <h1 className="text-2xl font-bold">Authority Login</h1>
      <form className="mt-5 grid gap-3" onSubmit={submit}>
        <input className="rounded-md border border-civic-line px-3 py-2" value={email} onChange={(event) => setEmail(event.target.value)} />
        <input className="rounded-md border border-civic-line px-3 py-2" value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
        <button className="rounded-md bg-civic-blue px-4 py-2 font-semibold text-white" type="submit">Login</button>
      </form>
      {message ? <p className="mt-4 rounded-md bg-slate-50 p-3 text-sm">{message}</p> : null}
      <div className="mt-6 grid gap-2 text-sm">
        {demoUsers.map(([demoEmail, demoPassword, role]) => (
          <button
            className="rounded-md border border-slate-200 p-3 text-left hover:bg-slate-50"
            key={demoEmail}
            onClick={() => {
              setEmail(demoEmail);
              setPassword(demoPassword);
            }}
            type="button"
          >
            {role}: {demoEmail}
          </button>
        ))}
      </div>
    </section>
  );
}
