"use client";

import { ErrorState } from "@/components/UIPrimitives";

export default function Error() {
  return <main className="mx-auto max-w-7xl px-5 py-6"><ErrorState label="Dashboard API unavailable. Start the FastAPI backend and refresh." /></main>;
}
