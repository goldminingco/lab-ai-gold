"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { projectsApi, Analysis } from "@/lib/api";
import api from "@/lib/api";

export default function HistoryPage() {
  const { id } = useParams<{ id: string }>();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading]   = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    api.get<Analysis[]>(`/api/v1/projects/${id}/analyses`)
      .then(r => setAnalyses(r.data))
      .finally(() => setLoading(false));
  }, [id]);

  const downloadPdf = async (analysisId: string, projectName: string) => {
    setDownloading(analysisId);
    try {
      const res = await api.get(
        `/api/v1/projects/${id}/analyses/${analysisId}/report`,
        { responseType: "blob" }
      );
      const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      const a = document.createElement("a");
      a.href = url;
      a.download = `labai-${projectName.toLowerCase().replace(/\s+/g, "-")}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) { alert("Erro ao gerar PDF"); }
    finally { setDownloading(null); }
  };

  return (
    <div className="p-8">
      <div className="flex items-center gap-3 mb-8">
        <Link href={`/dashboard/projects/${id}`} className="text-neutral-500 hover:text-neutral-300 text-sm">← Projeto</Link>
        <span className="text-dark-500">/</span>
        <h1 className="text-2xl font-bold text-neutral-100">Histórico de Análises</h1>
      </div>

      {loading ? (
        <div className="text-neutral-500 text-center py-16">Carregando...</div>
      ) : analyses.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-5xl mb-4">📊</div>
          <div className="text-neutral-400">Nenhuma análise executada ainda</div>
          <Link href={`/dashboard/projects/${id}`} className="btn-gold mt-4 inline-flex">Ir para o projeto</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {analyses.map((a, idx) => {
            const summary = a.summary_json as any;
            const isLatest = idx === 0;
            return (
              <div key={a.id} className={`card ${isLatest ? "border-gold-700/40 bg-gold-900/5" : ""}`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg ${
                      a.status === "done" ? "bg-green-500/15 border border-green-500/25" : "bg-red-500/15 border border-red-500/25"
                    }`}>
                      {a.status === "done" ? "⚡" : "❌"}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-neutral-200">
                          Análise {a.algorithm_version.toUpperCase()}
                        </span>
                        {isLatest && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gold-500/20 text-gold-400 border border-gold-500/30">
                            mais recente
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-neutral-500 mt-0.5">
                        {new Date(a.created_at).toLocaleDateString("pt-BR", {
                          day: "2-digit", month: "short", year: "numeric",
                          hour: "2-digit", minute: "2-digit"
                        })}
                        {a.finished_at && a.started_at && (
                          <span className="ml-2 text-neutral-600">
                            · {((new Date(a.finished_at).getTime() - new Date(a.started_at).getTime()) / 1000).toFixed(1)}s
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    {summary && a.status === "done" && (
                      <div className="flex gap-2 text-xs">
                        <span className="badge-high">🔴 {summary.high ?? 3}</span>
                        <span className="badge-medium">🟡 {summary.medium ?? 4}</span>
                        <span className="badge-low">🟢 {summary.low ?? 3}</span>
                      </div>
                    )}
                    {a.status === "done" && (
                      <button
                        onClick={() => downloadPdf(a.id, "projeto")}
                        disabled={downloading === a.id}
                        className="btn-outline text-xs px-3 py-1.5"
                      >
                        {downloading === a.id ? "⏳" : "📄 PDF"}
                      </button>
                    )}
                  </div>
                </div>

                {summary && (
                  <div className="mt-4 pt-4 border-t border-dark-600 grid grid-cols-3 gap-4 text-xs">
                    <div className="text-center">
                      <div className="text-gold-400 font-bold text-lg">{Math.round((summary.top_score ?? 0) * 100)}%</div>
                      <div className="text-neutral-500">Score máximo</div>
                    </div>
                    <div className="text-center">
                      <div className="text-neutral-200 font-bold text-lg">{Math.round((summary.avg_score ?? 0) * 100)}%</div>
                      <div className="text-neutral-500">Score médio</div>
                    </div>
                    <div className="text-center">
                      <div className="text-neutral-200 font-bold text-lg">{summary.area_ha?.toFixed(0) ?? "—"}</div>
                      <div className="text-neutral-500">Hectares</div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
