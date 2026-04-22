"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) { setError("Senhas não conferem"); return; }
    setLoading(true);
    try {
      const { data } = await authApi.register({ name: form.name, email: form.email, password: form.password });
      login(data);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Erro ao criar conta");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gold-gradient flex items-center justify-center"
                 style={{ boxShadow: "0 0 20px rgba(245,158,11,0.4)" }}>
              <span className="text-dark-900 font-bold">⬡</span>
            </div>
            <span className="text-2xl font-bold text-gold-gradient">LAB AI GOLD</span>
          </div>
          <h1 className="text-2xl font-bold text-neutral-100">Criar sua conta</h1>
          <p className="text-neutral-400 text-sm mt-1">Comece a prospectar com IA</p>
        </div>

        <div className="card border-dark-500">
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">Nome completo</label>
              <input className="input" type="text" placeholder="Seu nome" required
                value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">E-mail</label>
              <input className="input" type="email" placeholder="seu@email.com" required
                value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">Senha</label>
              <input className="input" type="password" placeholder="Mínimo 6 caracteres" required
                value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">Confirmar senha</label>
              <input className="input" type="password" placeholder="Repita a senha" required
                value={form.confirm} onChange={e => setForm(f => ({ ...f, confirm: e.target.value }))} />
            </div>
            {error && (
              <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            )}
            <button type="submit" disabled={loading} className="btn-gold w-full justify-center py-3">
              {loading ? "Criando conta..." : "Criar conta gratuita"}
            </button>
          </form>
          <p className="text-center text-sm text-neutral-500 mt-5">
            Já tem conta?{" "}
            <Link href="/auth/login" className="text-gold-400 hover:text-gold-300 font-medium">Entrar</Link>
          </p>
        </div>
        <p className="text-center mt-6">
          <Link href="/" className="text-xs text-neutral-600 hover:text-neutral-400">← Voltar ao início</Link>
        </p>
      </div>
    </div>
  );
}
