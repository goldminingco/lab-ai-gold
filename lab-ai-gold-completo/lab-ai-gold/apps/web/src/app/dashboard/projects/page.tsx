"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { projectsApi, Project } from "@/lib/api";

function CreateModal({ onClose, onCreate }: { onClose: () => void; onCreate: (p: Project) => void }) {
  const [form, setForm] = useState({ name: "", description: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const { data } = await projectsApi.create(form);
      onCreate(data); onClose();
    } catch (err: any) { setError(err.response?.data?.detail ?? "Erro ao criar projeto"); }
    finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="card w-full max-w-md mx-4 border-dark-400" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold text-neutral-100 mb-5">Novo Projeto</h2>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">Nome do projeto *</label>
            <input className="input" placeholder="ex: Serra Dourada Norte" required
              value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-300 mb-1.5">Descrição (opcional)</label>
            <textarea className="input resize-none h-20" placeholder="Área de prospecção no Pará..."
              value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          {error && <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">{error}</div>}
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="btn-outline flex-1 justify-center">Cancelar</button>
            <button type="submit" disabled={loading} className="btn-gold flex-1 justify-center">
              {loading ? "Criando..." : "Criar projeto"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading]   = useState(true);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    projectsApi.list().then(r => setProjects(r.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-neutral-100">Projetos</h1>
          <p className="text-neutral-400 text-sm mt-1">{projects.length} projeto{projects.length !== 1 ? "s" : ""}</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-gold">+ Novo projeto</button>
      </div>

      {loading ? (
        <div className="text-center py-20 text-neutral-500">Carregando...</div>
      ) : projects.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📁</div>
          <div className="text-neutral-400 font-medium">Nenhum projeto ainda</div>
          <p className="text-neutral-500 text-sm mt-1 mb-6">Crie seu primeiro projeto para começar a prospecção</p>
          <button onClick={() => setShowModal(true)} className="btn-gold">Criar primeiro projeto</button>
        </div>
      ) : (
        <div className="grid gap-4">
          {projects.map(p => (
            <Link key={p.id} href={`/dashboard/projects/${p.id}`}
                  className="card flex items-center justify-between hover:border-gold-700/40 transition-all group cursor-pointer">
              <div className="flex items-center gap-4">
                <div className={`w-11 h-11 rounded-lg flex items-center justify-center text-xl
                  ${p.has_analysis ? "bg-green-500/10 border border-green-500/20"
                    : p.has_area ? "bg-yellow-500/10 border border-yellow-500/20"
                    : "bg-dark-600 border border-dark-500"}`}>
                  {p.has_analysis ? "⚡" : p.has_area ? "🗺️" : "📁"}
                </div>
                <div>
                  <div className="font-semibold text-neutral-100 group-hover:text-gold-400 transition-colors">{p.name}</div>
                  {p.description && <div className="text-sm text-neutral-500 mt-0.5 line-clamp-1">{p.description}</div>}
                  <div className="text-xs text-neutral-600 mt-1">{new Date(p.created_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" })}</div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
                  p.has_analysis ? "badge-low" : p.has_area ? "badge-medium" : "bg-dark-600 text-neutral-400 border-dark-500"
                }`}>
                  {p.has_analysis ? "✓ Analisado" : p.has_area ? "Área enviada" : "Pendente"}
                </span>
                <span className="text-neutral-600 group-hover:text-gold-500 transition-colors">→</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {showModal && (
        <CreateModal onClose={() => setShowModal(false)} onCreate={p => setProjects(ps => [p, ...ps])} />
      )}
    </div>
  );
}
