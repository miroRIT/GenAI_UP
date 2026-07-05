"use client";

import { ErrorState } from "@/components/UIPrimitives";

export default function Error() {
  return <main className="mx-auto max-w-7xl px-5 py-6"><ErrorState label="Demo Mode could not load. Verify backend API is running." /></main>;
}
