"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { projectsApi, Project } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.list().then(r => setProjects(r.data)).finally(() => setLoading(false));
  }, []);

  const active   = projects.filter(p => p.status === "active").length;
  const withArea = projects.filter(p => p.has_area).length;
  const analyzed = projects.filter(p => p.has_analysis).length;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-neutral-100">
          Bem-vindo, <span className="text-gold-gradient">{user?.name.split(" ")[0]}</span> 👋
        </h1>
        <p className="text-neutral-400 text-sm mt-1">Painel de controle · LAB AI GOLD</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: "Projetos ativos",  value: active,   icon: "📁", color: "text-gold-400" },
          { label: "Com área enviada", value: withArea, icon: "🗺️", color: "text-blue-400" },
          { label: "Analisados",       value: analyzed, icon: "⚡", color: "text-green-400" },
        ].map(s => (
          <div key={s.label} className="card flex items-center gap-4">
            <span className="text-3xl">{s.icon}</span>
            <div>
              <div className={`text-3xl font-bold ${s.color}`}>{loading ? "—" : s.value}</div>
              <div className="text-xs text-neutral-500 mt-0.5">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick action */}
      <div className="card border-gold-700/25 bg-gold-900/10 flex items-center justify-between">
        <div>
          <div className="font-semibold text-neutral-200">Criar novo projeto</div>
          <div className="text-sm text-neutral-400 mt-0.5">Faça upload de uma área KML/KMZ e inicie a análise</div>
        </div>
        <Link href="/dashboard/projects" className="btn-gold flex-shrink-0">
          Ir para Projetos →
        </Link>
      </div>

      {/* Recent */}
      {projects.length > 0 && (
        <div className="mt-8">
          <h2 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-4">Projetos recentes</h2>
          <div className="space-y-2">
            {projects.slice(0, 5).map(p => (
              <Link key={p.id} href={`/dashboard/projects/${p.id}`}
                    className="flex items-center justify-between card hover:border-gold-700/40 transition-colors group">
                <div className="flex items-center gap-3">
                  <span className="text-lg">{p.has_analysis ? "⚡" : p.has_area ? "🗺️" : "📁"}</span>
                  <div>
                    <div className="text-sm font-medium text-neutral-200 group-hover:text-gold-400 transition-colors">{p.name}</div>
                    <div className="text-xs text-neutral-500">{new Date(p.created_at).toLocaleDateString("pt-BR")}</div>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full border ${
                  p.has_analysis ? "badge-low" : p.has_area ? "badge-medium" : "bg-dark-600 text-neutral-400 border-dark-500"
                }`}>
                  {p.has_analysis ? "Analisado" : p.has_area ? "Área enviada" : "Novo"}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
