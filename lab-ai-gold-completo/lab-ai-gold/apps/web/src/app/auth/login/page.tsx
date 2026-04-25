"use client";
import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const { data } = await authApi.login(form);
      login(data);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Erro ao fazer login");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
                          <Image src="/logo.png" alt="LAB AI GOLD" width={40} height={40} className="rounded-xl" priority />
            <span className="text-2xl font-bold text-gold-gradient">LAB AI GOLD</span>
          </div>
          <h1 className="text-2xl font-bold text-neutral-100">Entrar na plataforma</h1>
          <p className="text-neutral-400 text-sm mt-1">Análise geoespacial de prospecção</p>
        </div>

        <div className="card border-dark-500">
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">E-mail</label>
              <input className="input" type="email" placeholder="seu@email.com" required
                value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-neutral-300 mb-1.5">Senha</label>
              <input className="input" type="password" placeholder="••••••••" required
                value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
            </div>
            {error && (
              <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
                {error}
              </div>
            )}
            <button type="submit" disabled={loading} className="btn-gold w-full justify-center py-3">
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
          <p className="text-center text-sm text-neutral-500 mt-5">
            Não tem conta?{" "}
            <Link href="/auth/register" className="text-gold-400 hover:text-gold-300 font-medium">
              Criar conta grátis
            </Link>
          </p>
        </div>
        <p className="text-center mt-6">
          <Link href="/" className="text-xs text-neutral-600 hover:text-neutral-400">← Voltar ao início</Link>
        </p>
      </div>
    </div>
  );
}
