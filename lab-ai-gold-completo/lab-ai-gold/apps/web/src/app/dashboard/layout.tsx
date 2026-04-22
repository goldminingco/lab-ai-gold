"use client";
import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

function NavItem({ href, icon, label, active }: { href: string; icon: string; label: string; active: boolean }) {
  return (
    <Link href={href} className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
      ${active ? "bg-gold-500/15 text-gold-400 border border-gold-500/25" : "text-neutral-400 hover:text-neutral-200 hover:bg-dark-600"}`}>
      <span className="text-base">{icon}</span>
      {label}
    </Link>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const path = usePathname();

  useEffect(() => {
    if (!loading && !user) router.push("/auth/login");
  }, [user, loading, router]);

  if (loading || !user) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-3">⬡</div>
        <div className="text-gold-400 animate-pulse text-sm font-medium">Carregando LAB AI GOLD...</div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-dark-800 border-r border-dark-600 flex flex-col flex-shrink-0">
        {/* Logo */}
        <div className="px-4 py-5 border-b border-dark-600">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gold-gradient flex items-center justify-center"
                 style={{ boxShadow: "0 0 12px rgba(245,158,11,0.35)" }}>
              <span className="text-dark-900 font-bold text-sm">⬡</span>
            </div>
            <div>
              <div className="text-sm font-bold text-gold-gradient">LAB AI GOLD</div>
              <div className="text-xs text-neutral-500">v0.4.0 · Fase 1</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          <div className="text-xs font-semibold text-neutral-600 uppercase tracking-wider px-3 mb-2">Principal</div>
          <NavItem href="/dashboard"          icon="🏠" label="Painel"    active={path === "/dashboard"} />
          <NavItem href="/dashboard/projects" icon="📁" label="Projetos"  active={path.startsWith("/dashboard/projects")} />

          {user.role === "admin" && (
            <>
              <div className="text-xs font-semibold text-neutral-600 uppercase tracking-wider px-3 mt-4 mb-2">Admin</div>
              <NavItem href="/dashboard/admin" icon="⚙️" label="Usuários" active={path === "/dashboard/admin"} />
            </>
          )}
        </nav>

        {/* Área KML de teste */}
        <div className="px-3 pb-3">
          <a href="/area-teste.kml" download
             className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-neutral-500 hover:text-gold-400 hover:bg-dark-700 transition-colors border border-dashed border-dark-500 hover:border-gold-700/40">
            <span>📎</span>
            Baixar KML de teste
          </a>
        </div>

        {/* User */}
        <div className="px-3 py-4 border-t border-dark-600">
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-700">
            <div className="w-8 h-8 rounded-full bg-gold-800/40 border border-gold-700/40 flex items-center justify-center text-gold-400 text-sm font-bold">
              {user.name[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium text-neutral-200 truncate">{user.name}</div>
              <div className="text-xs text-neutral-500 truncate capitalize">{user.role}</div>
            </div>
          </div>
          <button onClick={logout} className="mt-2 w-full text-left px-3 py-2 rounded-lg text-xs text-neutral-500 hover:text-red-400 hover:bg-red-500/10 transition-colors">
            ↩ Sair da conta
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto bg-dark-900">{children}</main>
    </div>
  );
}
