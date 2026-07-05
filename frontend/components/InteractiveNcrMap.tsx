"use client";

import L from "leaflet";
import { GeoJSON, LayersControl, MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { GeoIncident } from "@/lib/api";

const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

const severityColor: Record<string, string> = {
  Low: "#059669",
  Medium: "#CA8A04",
  High: "#EA580C",
  Critical: "#DC2626",
};

export function InteractiveNcrMap({
  geojson,
  incidents,
}: {
  geojson: Record<string, unknown>;
  incidents: GeoIncident[];
}) {
  const grouped = {
    Weather: incidents.filter((incident) => ["Flood", "Heatwave"].includes(incident.category)),
    Traffic: incidents.filter((incident) => incident.category === "Traffic"),
    AQI: incidents.filter((incident) => incident.category === "AQI/Public Health"),
    "Fire/Industrial": incidents.filter((incident) => incident.category === "Fire/Industrial"),
    "News incidents": incidents.filter((incident) => incident.incident_id.startsWith("news")),
    Alerts: incidents,
  };

  return (
    <section className="rounded-lg border border-civic-line bg-white p-4 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold">Interactive NCR Geospatial Map</h2>
        <p className="text-sm text-slate-500">
          OpenStreetMap tiles with simplified NCR district GeoJSON boundaries and provider/fallback incident markers.
        </p>
      </div>
      <div className="h-[560px] overflow-hidden rounded-lg border border-slate-200">
        <MapContainer center={[28.62, 77.22]} zoom={8} scrollWheelZoom className="h-full w-full">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <LayersControl position="topright">
            <LayersControl.Overlay checked name="District boundaries">
              <GeoJSON
                data={geojson as never}
                style={() => ({ color: "#2563EB", weight: 2, fillOpacity: 0.08 })}
                onEachFeature={(feature, layer) => {
                  const props = feature.properties || {};
                  layer.bindPopup(
                    `<strong>${props.district_name}</strong><br/>${props.state}<br/>Population: ${Number(
                      props.population || 0,
                    ).toLocaleString()}<br/>${props.disaster_profile}`,
                  );
                }}
              />
            </LayersControl.Overlay>
            {Object.entries(grouped).map(([layerName, layerIncidents]) => (
              <LayersControl.Overlay checked={layerName === "Alerts"} name={layerName} key={layerName}>
                <>
                  {layerIncidents.map((incident) => (
                    <Marker
                      icon={markerIcon}
                      key={`${layerName}-${incident.incident_id}`}
                      position={[incident.latitude, incident.longitude]}
                    >
                      <Popup>
                        <div>
                          <p className="font-semibold">{incident.title}</p>
                          <p>{incident.district_name}</p>
                          <p>{incident.category}</p>
                          <p style={{ color: severityColor[incident.severity] || "#CA8A04" }}>
                            {incident.severity}
                          </p>
                          <p>{incident.summary}</p>
                          <p className="font-medium">{incident.recommended_action}</p>
                          <p className="text-xs">{incident.source}</p>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </>
              </LayersControl.Overlay>
            ))}
          </LayersControl>
        </MapContainer>
      </div>
    </section>
  );
}
