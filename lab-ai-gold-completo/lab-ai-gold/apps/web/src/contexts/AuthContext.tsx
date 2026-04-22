"use client";
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { authApi, TokenResponse, User } from "@/lib/api";

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (res: TokenResponse) => void;
  logout: () => void;
}

const Ctx = createContext<AuthCtx>({ user: null, loading: true, login: () => {}, logout: () => {} });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) { setLoading(false); return; }
    authApi.me()
      .then((r) => setUser(r.data))
      .catch(() => { localStorage.clear(); })
      .finally(() => setLoading(false));
  }, []);

  const login = (res: TokenResponse) => {
    localStorage.setItem("access_token",  res.access_token);
    localStorage.setItem("refresh_token", res.refresh_token);
    localStorage.setItem("user", JSON.stringify(res.user));
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setUser(null);
    window.location.href = "/auth/login";
  };

  return <Ctx.Provider value={{ user, loading, login, logout }}>{children}</Ctx.Provider>;
}

export const useAuth = () => useContext(Ctx);
