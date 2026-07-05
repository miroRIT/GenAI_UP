"use client";

import { MapPin } from "lucide-react";
import { RiskBadge } from "./RiskBadge";
import { Ward } from "@/lib/api";

export function NcrDisasterMap({
  layers,
}: {
  layers: Array<Ward & { disaster_score: number; primary_hazards: string[] }>;
}) {
  const latitudes = layers.map((layer) => layer.latitude);
  const longitudes = layers.map((layer) => layer.longitude);
  const north = Math.max(...latitudes);
  const south = Math.min(...latitudes);
  const east = Math.max(...longitudes);
  const west = Math.min(...longitudes);

  function position(layer: Ward) {
    const x = ((layer.longitude - west) / (east - west || 1)) * 82 + 9;
    const y = (1 - (layer.latitude - south) / (north - south || 1)) * 78 + 10;
    return { left: `${x}%`, top: `${y}%` };
  }

  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">NCR Natural Disaster Prone Areas</h2>
          <p className="text-sm text-slate-500">Relative geospatial watch map for flood, heat, AQI, seismic, drought, and fire exposure.</p>
        </div>
        <span className="text-sm text-slate-500">Higher marker size = higher disaster score</span>
      </div>
      <div className="relative h-[430px] overflow-hidden rounded-lg border border-slate-200 bg-[linear-gradient(135deg,#eef7ff,#f8fbf2)]">
        <div className="absolute inset-x-[12%] top-[8%] h-[78%] rounded-[46%] border-2 border-dashed border-slate-300" />
        <div className="absolute left-[52%] top-[4%] h-[88%] w-2 rotate-[-8deg] rounded-full bg-blue-200/70" title="Yamuna corridor" />
        <div className="absolute bottom-4 left-4 rounded-md bg-white/90 px-3 py-2 text-xs text-slate-600 shadow-sm">
          Yamuna-Hindon flood corridor, Aravalli/water-stress belt, high-AQI urban core
        </div>
        {layers.map((layer) => {
          const size = Math.max(18, Math.min(46, layer.disaster_score / 2));
          return (
            <div
              className="absolute -translate-x-1/2 -translate-y-1/2"
              key={layer.ward_id}
              style={position(layer)}
              title={`${layer.ward_name}: ${layer.disaster_profile}`}
            >
              <div
                className="flex items-center justify-center rounded-full border-2 border-white bg-red-500/85 text-white shadow-lg"
                style={{ height: size, width: size }}
              >
                <MapPin className="h-4 w-4" />
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {layers.slice(0, 6).map((layer) => (
          <article className="rounded-md border border-slate-200 p-3" key={layer.ward_id}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-medium">{layer.ward_name}</h3>
                <p className="text-xs text-slate-500">{layer.state} · Disaster score {layer.disaster_score}</p>
              </div>
              <RiskBadge level={layer.risk_level} />
            </div>
            <p className="mt-2 text-sm text-slate-600">{layer.disaster_profile}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
