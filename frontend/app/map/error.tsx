"use client";

import { ErrorState } from "@/components/UIPrimitives";

export default function Error() {
  return <main className="mx-auto max-w-7xl px-5 py-6"><ErrorState label="Map incidents or boundary layers are unavailable." /></main>;
}
