"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import api, { User } from "@/lib/api";

const ROLE_LABELS: Record<string, string> = { user: "Usuário", geologist: "Geólogo", admin: "Admin" };
const STATUS_LABELS: Record<string, string> = { active: "Ativo", inactive: "Inativo", pending: "Pendente" };

export default function AdminPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [users, setUsers]       = useState<User[]>([]);
  const [fetching, setFetching] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && user?.role !== "admin") router.push("/dashboard");
  }, [user, loading]);

  useEffect(() => {
    if (user?.role === "admin") {
      api.get<User[]>("/api/v1/admin/users")
        .then(r => setUsers(r.data))
        .finally(() => setFetching(false));
    }
  }, [user]);

  const setRole = async (userId: string, role: string) => {
    setUpdating(userId);
    try {
      const { data } = await api.patch<User>(`/api/v1/admin/users/${userId}/role?role=${role}`);
      setUsers(us => us.map(u => u.id === userId ? data : u));
    } finally { setUpdating(null); }
  };

  const setStatus = async (userId: string, status: string) => {
    setUpdating(userId);
    try {
      const { data } = await api.patch<User>(`/api/v1/admin/users/${userId}/status?status=${status}`);
      setUsers(us => us.map(u => u.id === userId ? data : u));
    } finally { setUpdating(null); }
  };

  if (loading || fetching) return <div className="p-8 text-neutral-500 text-center">Carregando...</div>;
  if (user?.role !== "admin") return null;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-neutral-100">Painel Admin</h1>
        <p className="text-neutral-400 text-sm mt-1">{users.length} usuários cadastrados</p>
      </div>

      <div className="card overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-dark-600 bg-dark-700">
              {["Usuário", "E-mail", "Role", "Status", "Cadastro", "Ações"].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-neutral-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((u, i) => (
              <tr key={u.id} className={`border-b border-dark-600 ${i % 2 === 0 ? "bg-dark-800" : "bg-dark-700/50"}`}>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-gold-800/30 border border-gold-700/30 flex items-center justify-center text-gold-400 text-xs font-bold">
                      {u.name[0].toUpperCase()}
                    </div>
                    <span className="font-medium text-neutral-200">{u.name}</span>
                    {u.id === user.id && <span className="text-xs text-gold-600">(você)</span>}
                  </div>
                </td>
                <td className="px-4 py-3 text-neutral-400 font-mono text-xs">{u.email}</td>
                <td className="px-4 py-3">
                  <select
                    value={u.role}
                    disabled={u.id === user.id || updating === u.id}
                    onChange={e => setRole(u.id, e.target.value)}
                    className="bg-dark-600 border border-dark-500 rounded px-2 py-1 text-xs text-neutral-300 focus:outline-none focus:border-gold-600 disabled:opacity-40"
                  >
                    {["user", "geologist", "admin"].map(r => (
                      <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <select
                    value={u.status}
                    disabled={u.id === user.id || updating === u.id}
                    onChange={e => setStatus(u.id, e.target.value)}
                    className="bg-dark-600 border border-dark-500 rounded px-2 py-1 text-xs text-neutral-300 focus:outline-none focus:border-gold-600 disabled:opacity-40"
                  >
                    {["active", "inactive", "pending"].map(s => (
                      <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3 text-xs text-neutral-500">
                  {new Date(u.created_at).toLocaleDateString("pt-BR")}
                </td>
                <td className="px-4 py-3 text-xs text-neutral-600">
                  {updating === u.id ? "⏳" : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
