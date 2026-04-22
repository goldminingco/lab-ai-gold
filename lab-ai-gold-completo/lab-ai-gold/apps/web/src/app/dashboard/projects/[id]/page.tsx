"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { projectsApi, Project, ProjectArea, Analysis, AnalysisPoint } from "@/lib/api";
import api from "@/lib/api";

// MapLibre só no cliente
const AnalysisMap = dynamic(() => import("@/components/map/AnalysisMap"), { ssr: false, loading: () => (
  <div className="w-full h-full flex items-center justify-center bg-dark-800 rounded-xl">
    <div className="text-neutral-500 text-sm">Carregando mapa...</div>
  </div>
)});

// ─── Sub-componentes ──────────────────────────────────────────────────────────
function PointCard({ pt }: { pt: AnalysisPoint }) {
  const [open, setOpen] = useState(false);
  const pct = Math.round(pt.score * 100);
  const badgeCls = pt.priority === "high" ? "badge-high" : pt.priority === "medium" ? "badge-medium" : "badge-low";
  const label = pt.priority === "high" ? "Alta" : pt.priority === "medium" ? "Média" : "Baixa";
  const barColor = pt.priority === "high" ? "bg-red-500" : pt.priority === "medium" ? "bg-yellow-500" : "bg-green-500";

  return (
    <div className="card p-4 hover:border-dark-400 transition-colors">
      <div className="flex items-center justify-between cursor-pointer" onClick={() => setOpen(o => !o)}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
               style={{ background: pt.color }}>
            {pt.label}
          </div>
          <div>
            <div className="text-sm font-medium text-neutral-200">Ponto {pt.rank}</div>
            <div className={`text-xs mt-0.5 ${badgeCls}`}>{label} prioridade</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold" style={{ color: pt.color }}>{pct}%</div>
          <div className="text-xs text-neutral-600">{open ? "▲" : "▼"}</div>
        </div>
      </div>
      {/* Barra de score */}
      <div className="mt-3 h-1.5 rounded-full bg-dark-600">
        <div className={`h-1.5 rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      {/* Justificativas */}
      {open && (
        <ul className="mt-3 space-y-1.5">
          {pt.reasons_json.map((r, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-neutral-400">
              <span className="text-gold-600 mt-0.5 flex-shrink-0">◆</span>
              {r}
            </li>
          ))}
          <li className="flex items-center gap-2 text-xs text-neutral-600 mt-1">
            <span>📍</span>
            <span className="font-mono">{pt.lat.toFixed(5)}, {pt.lng.toFixed(5)}</span>
          </li>
        </ul>
      )}
    </div>
  );
}

function UploadZone({ projectId, onUploaded }: { projectId: string; onUploaded: (a: ProjectArea) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const handleFile = async (file: File) => {
    setError(""); setLoading(true);
    try {
      const { data } = await projectsApi.uploadArea(projectId, file);
      if (data.parse_status === "error") setError(data.parse_error ?? "Erro no parse do arquivo");
      else onUploaded(data);
    } catch (e: any) { setError(e.response?.data?.detail ?? "Erro no upload"); }
    finally { setLoading(false); }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault(); setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => inputRef.current?.click()}
      className={`cursor-pointer rounded-xl border-2 border-dashed transition-all p-10 text-center
        ${dragging ? "border-gold-500 bg-gold-500/10" : "border-dark-500 hover:border-gold-700 hover:bg-dark-700/50"}`}
    >
      <input ref={inputRef} type="file" accept=".kml,.kmz" className="hidden"
        onChange={e => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
      <div className="text-4xl mb-3">{loading ? "⏳" : "📎"}</div>
      <div className="font-medium text-neutral-300">{loading ? "Processando arquivo..." : "Arraste ou clique para enviar"}</div>
      <div className="text-sm text-neutral-500 mt-1">Aceita .kml e .kmz · máx 50MB</div>
      {error && <div className="mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-2">{error}</div>}
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router  = useRouter();

  const [project,  setProject]  = useState<Project | null>(null);
  const [area,     setArea]     = useState<ProjectArea | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading,  setLoading]  = useState(true);
  const [analyzing,setAnalyzing]= useState(false);
  const [tab,      setTab]      = useState<"map" | "points">("map");
  const [error,    setError]    = useState("");

  useEffect(() => {
    Promise.all([
      projectsApi.get(id),
      projectsApi.getArea(id).catch(() => ({ data: null })),
      projectsApi.getLatestAnalysis(id).catch(() => ({ data: null })),
    ]).then(([p, a, an]) => {
      setProject(p.data);
      setArea(a.data);
      setAnalysis(an.data);
    }).catch(() => router.push("/dashboard/projects"))
      .finally(() => setLoading(false));
  }, [id]);

  const runAnalysis = async () => {
    setError(""); setAnalyzing(true);
    try {
      const { data } = await projectsApi.runAnalysis(id);
      setAnalysis(data);
      setTab("map");
    } catch (e: any) { setError(e.response?.data?.detail ?? "Erro na análise"); }
    finally { setAnalyzing(false); }
  };

  if (loading) return (
    <div className="p-8 text-center">
      <div className="text-gold-400 animate-pulse">Carregando projeto...</div>
    </div>
  );

  if (!project) return null;

  const highPts   = analysis?.points.filter(p => p.priority === "high")   ?? [];
  const mediumPts = analysis?.points.filter(p => p.priority === "medium") ?? [];
  const lowPts    = analysis?.points.filter(p => p.priority === "low")    ?? [];
  const allPts    = [...highPts, ...mediumPts, ...lowPts];

  return (
    <div className="flex flex-col h-screen">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-dark-600 bg-dark-800 flex-shrink-0">
        <div className="flex items-center gap-3">
          <Link href="/dashboard/projects" className="text-neutral-500 hover:text-neutral-300 text-sm">← Projetos</Link>
          <span className="text-dark-500">/</span>
          <h1 className="font-semibold text-neutral-100">{project.name}</h1>
          {project.description && <span className="text-sm text-neutral-500 hidden md:block">· {project.description}</span>}
        </div>
        <div className="flex items-center gap-2">
          {analysis && (
            <button
              onClick={async () => {
                setError("");
                try {
                  const res = await api.get(
                    `/api/v1/projects/${id}/analyses/${analysis.id}/report`,
                    { responseType: "blob" }
                  );
                  const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
                  const a = document.createElement("a");
                  a.href = url; a.download = `labai-${project.name.toLowerCase().replace(/\s+/g,"-")}.pdf`;
                  a.click(); URL.revokeObjectURL(url);
                } catch { setError("Erro ao gerar PDF"); }
              }}
              className="btn-outline text-sm px-3 py-2"
            >
              📄 PDF
            </button>
          )}
          <Link href={`/dashboard/projects/${id}/history`} className="btn-outline text-sm px-3 py-2">
            📊 Histórico
          </Link>
          {area && area.parse_status === "ok" && (
            <button onClick={runAnalysis} disabled={analyzing}
              className="btn-gold text-sm px-4 py-2">
              {analyzing ? "⏳ Analisando..." : "⚡ " + (analysis ? "Re-analisar" : "Analisar área")}
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mx-6 mt-4 text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 flex-shrink-0">
          {error}
        </div>
      )}

      {/* ── Body ──────────────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Left panel ──────────────────────────────────────────────────── */}
        <div className="w-80 flex-shrink-0 border-r border-dark-600 flex flex-col bg-dark-800 overflow-hidden">

          {/* Área info */}
          <div className="p-4 border-b border-dark-600">
            <div className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Área de interesse</div>
            {!area ? (
              <UploadZone projectId={id} onUploaded={a => { setArea(a); }} />
            ) : area.parse_status === "error" ? (
              <div className="space-y-2">
                <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg p-3">{area.parse_error}</div>
                <UploadZone projectId={id} onUploaded={a => setArea(a)} />
              </div>
            ) : (
              <div className="card p-3 border-green-500/20 bg-green-500/5">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-green-400">✓</span>
                  <span className="text-sm font-medium text-neutral-200 truncate">{area.original_filename}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-neutral-500">
                  <span>📐 {area.area_ha?.toFixed(1) ?? "—"} ha</span>
                  <span>📍 {area.centroid_lat?.toFixed(4)}, {area.centroid_lng?.toFixed(4)}</span>
                </div>
                <button onClick={() => document.getElementById("reupload-input")?.click()}
                        className="mt-2 text-xs text-neutral-600 hover:text-gold-400 transition-colors">
                  ↩ Trocar arquivo
                </button>
                <input id="reupload-input" type="file" accept=".kml,.kmz" className="hidden"
                  onChange={async e => {
                    const f = e.target.files?.[0]; if (!f) return;
                    try {
                      const { data } = await projectsApi.uploadArea(id, f);
                      setArea(data); setAnalysis(null);
                    } catch (err: any) { setError(err.response?.data?.detail ?? "Erro"); }
                  }} />
              </div>
            )}
          </div>

          {/* Análise */}
          {analysis && (
            <div className="flex-1 overflow-y-auto">
              {/* Tabs */}
              <div className="flex border-b border-dark-600">
                {(["map", "points"] as const).map(t => (
                  <button key={t} onClick={() => setTab(t)}
                    className={`flex-1 py-3 text-sm font-medium transition-colors
                      ${tab === t ? "text-gold-400 border-b-2 border-gold-500" : "text-neutral-500 hover:text-neutral-300"}`}>
                    {t === "map" ? "🗺️ Mapa" : "📍 Pontos"}
                  </button>
                ))}
              </div>

              {tab === "points" && (
                <div className="p-3 space-y-2">
                  {/* Legenda */}
                  <div className="flex gap-2 flex-wrap mb-3">
                    <span className="badge-high">🔴 Alta ({highPts.length})</span>
                    <span className="badge-medium">🟡 Média ({mediumPts.length})</span>
                    <span className="badge-low">🟢 Baixa ({lowPts.length})</span>
                  </div>
                  {allPts.map(pt => <PointCard key={pt.id} pt={pt} />)}
                  <div className="card border-yellow-700/20 bg-yellow-900/10 p-3 text-xs text-yellow-600 mt-2">
                    ⚠️ Resultados probabilísticos. Não garantem presença de ouro.
                  </div>
                </div>
              )}
            </div>
          )}

          {/* CTA para analisar */}
          {!analysis && area?.parse_status === "ok" && (
            <div className="p-4">
              <div className="text-xs text-neutral-500 text-center mb-3">Área enviada! Pronto para analisar.</div>
              <button onClick={runAnalysis} disabled={analyzing} className="btn-gold w-full justify-center">
                {analyzing ? "⏳ Processando..." : "⚡ Iniciar análise geoespacial"}
              </button>
            </div>
          )}
        </div>

        {/* ── Mapa ──────────────────────────────────────────────────────────── */}
        <div className="flex-1 relative">
          {tab === "map" || !analysis ? (
            area?.parse_status === "ok" ? (
              <AnalysisMap area={area} points={analysis?.points ?? []} />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-center p-8">
                <div className="text-6xl mb-4">🗺️</div>
                <div className="text-neutral-400 font-medium text-lg mb-2">Nenhuma área carregada</div>
                <p className="text-neutral-500 text-sm max-w-sm">
                  Envie um arquivo KML ou KMZ no painel lateral para visualizar sua área de prospecção no mapa.
                </p>
              </div>
            )
          ) : null}
        </div>
      </div>
    </div>
  );
}
