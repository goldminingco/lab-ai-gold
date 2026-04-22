"use client";
import { useEffect, useRef } from "react";
import type { ProjectArea, AnalysisPoint } from "@/lib/api";

interface Props {
  area: ProjectArea | null;
  points: AnalysisPoint[];
}

export default function AnalysisMap({ area, points }: Props) {
  const mapRef  = useRef<HTMLDivElement>(null);
  const mapInst = useRef<any>(null);

  useEffect(() => {
    if (!mapRef.current || mapInst.current) return;

    // Importa MapLibre dinamicamente (só no browser)
    import("maplibre-gl").then(({ default: maplibregl }) => {
      // Calcula centro inicial
      let center: [number, number] = [-55, -10]; // Brasil
      let zoom = 4;

      if (area?.centroid_lng && area?.centroid_lat) {
        center = [area.centroid_lng, area.centroid_lat];
        zoom = 10;
      }

      const map = new maplibregl.Map({
        container: mapRef.current!,
        style: {
          version: 8,
          sources: {
            osm: {
              type: "raster",
              tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
              attribution: "© OpenStreetMap",
            },
          },
          layers: [{ id: "osm", type: "raster", source: "osm" }],
        },
        center,
        zoom,
      });

      map.addControl(new maplibregl.NavigationControl(), "top-right");
      map.addControl(new maplibregl.ScaleControl(), "bottom-left");

      map.on("load", () => {
        // ── Polígono da área ──────────────────────────────────────────────
        if (area?.geojson) {
          map.addSource("area", { type: "geojson", data: area.geojson as any });
          map.addLayer({
            id: "area-fill",
            type: "fill",
            source: "area",
            paint: { "fill-color": "#f59e0b", "fill-opacity": 0.12 },
          });
          map.addLayer({
            id: "area-line",
            type: "line",
            source: "area",
            paint: { "line-color": "#f59e0b", "line-width": 2, "line-opacity": 0.8 },
          });

          // Fit to bounds
          if (area.bounds_json) {
            const b = area.bounds_json;
            map.fitBounds(
              [[b.min_lng, b.min_lat], [b.max_lng, b.max_lat]],
              { padding: 60, duration: 800 }
            );
          }
        }

        // ── Pontos de análise ─────────────────────────────────────────────
        if (points.length > 0) {
          const geojsonPts: any = {
            type: "FeatureCollection",
            features: points.map(pt => ({
              type: "Feature",
              geometry: { type: "Point", coordinates: [pt.lng, pt.lat] },
              properties: {
                id: pt.id, label: pt.label, score: pt.score,
                priority: pt.priority, color: pt.color, rank: pt.rank,
                reasons: pt.reasons_json.join(" · "),
              },
            })),
          };

          map.addSource("points", { type: "geojson", data: geojsonPts });

          // Círculos coloridos
          map.addLayer({
            id: "points-circle",
            type: "circle",
            source: "points",
            paint: {
              "circle-color":        ["get", "color"],
              "circle-radius":       10,
              "circle-opacity":      0.9,
              "circle-stroke-width": 2,
              "circle-stroke-color": "#ffffff",
            },
          });

          // Labels
          map.addLayer({
            id: "points-label",
            type: "symbol",
            source: "points",
            layout: {
              "text-field":  ["get", "label"],
              "text-size":   10,
              "text-offset": [0, 0],
              "text-anchor": "center",
              "text-font":   ["Open Sans Bold", "Arial Unicode MS Bold"],
            },
            paint: { "text-color": "#ffffff" },
          });

          // Popup ao clicar
          map.on("click", "points-circle", (e: any) => {
            const feat = e.features?.[0];
            if (!feat) return;
            const p = feat.properties;
            const pct = Math.round(p.score * 100);
            const priorityLabel = p.priority === "high" ? "🔴 Alta" : p.priority === "medium" ? "🟡 Média" : "🟢 Baixa";

            new maplibregl.Popup({ className: "lab-popup" })
              .setLngLat(e.lngLat)
              .setHTML(`
                <div style="background:#1a1a1a;border:1px solid #2d2d2d;border-radius:10px;padding:14px;min-width:220px;font-family:system-ui">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                    <div style="width:10px;height:10px;border-radius:50%;background:${p.color}"></div>
                    <strong style="color:#f5f5f5;font-size:14px">${p.label}</strong>
                    <span style="margin-left:auto;font-size:12px;color:#a3a3a3">${priorityLabel}</span>
                  </div>
                  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
                    <span style="color:#a3a3a3;font-size:12px">Score de probabilidade</span>
                    <strong style="color:${p.color};font-size:18px">${pct}%</strong>
                  </div>
                  <div style="background:#111;border-radius:6px;padding:4px 6px;margin-bottom:6px">
                    <div style="height:4px;border-radius:2px;background:#2d2d2d">
                      <div style="height:4px;border-radius:2px;background:${p.color};width:${pct}%"></div>
                    </div>
                  </div>
                  <div style="font-size:11px;color:#737373;line-height:1.5">${p.reasons}</div>
                </div>
              `)
              .addTo(map);
          });

          map.on("mouseenter", "points-circle", () => { map.getCanvas().style.cursor = "pointer"; });
          map.on("mouseleave", "points-circle", () => { map.getCanvas().style.cursor = ""; });
        }
      });

      mapInst.current = map;
    });

    return () => { mapInst.current?.remove(); mapInst.current = null; };
  }, [area, points]);

  return (
    <div ref={mapRef} className="w-full h-full rounded-xl" />
  );
}
