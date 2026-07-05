"use client";

import { useState } from "react";
import { SectionCard, StatusBadge } from "./UIPrimitives";

export function AdminPreviewCard() {
  const [modal, setModal] = useState("");
  const actions = ["Invite User", "Reset Password", "Manage Roles"];
  return (
    <SectionCard title="Authority Admin Preview" badge={<StatusBadge label="Production Roadmap" tone="slate" />}>
      <p className="text-sm text-slate-600">Prototype preview for secure identity operations planned for production.</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {actions.map((action) => (
          <button className="rounded-md border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-500" key={action} onClick={() => setModal(action)} type="button">
            {action}
          </button>
        ))}
      </div>
      {modal ? (
        <div className="mt-4 rounded-md border border-blue-200 bg-blue-50 p-4">
          <StatusBadge label="Prototype Preview" tone="blue" />
          <h3 className="mt-2 font-semibold">{modal}</h3>
          <p className="mt-1 text-sm text-slate-700">This feature is intentionally disabled in the hackathon prototype. In production it would support secure invite flow, password reset, audit logging, and role management.</p>
          <button className="mt-3 rounded-md bg-white px-3 py-2 text-sm font-semibold" onClick={() => setModal("")} type="button">Close</button>
        </div>
      ) : null}
    </SectionCard>
  );
}
