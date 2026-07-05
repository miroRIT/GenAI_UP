"use client";

import dynamic from "next/dynamic";
import { GeoIncident } from "@/lib/api";

const InteractiveNcrMap = dynamic(
  () => import("./InteractiveNcrMap").then((module) => module.InteractiveNcrMap),
  { ssr: false },
);

export function MapShell({
  geojson,
  incidents,
}: {
  geojson: Record<string, unknown>;
  incidents: GeoIncident[];
}) {
  return <InteractiveNcrMap geojson={geojson} incidents={incidents} />;
}
