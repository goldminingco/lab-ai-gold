import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// Injeta token em todas as requisições
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redireciona para login em 401
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      window.location.href = "/auth/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ─── Tipos ────────────────────────────────────────────────────────────────────
export interface User {
  id: string; name: string; email: string; role: string;
  status: string; created_at: string;
}

export interface TokenResponse {
  access_token: string; refresh_token: string; token_type: string; user: User;
}

export interface Project {
  id: string; user_id: string; name: string; description: string | null;
  status: string; phase: string; created_at: string;
  has_area: boolean; has_analysis: boolean;
}

export interface ProjectArea {
  id: string; project_id: string; original_filename: string;
  geojson: GeoJSON | null; area_ha: number | null;
  centroid_lat: number | null; centroid_lng: number | null;
  bounds_json: { min_lng: number; min_lat: number; max_lng: number; max_lat: number } | null;
  parse_status: "pending" | "ok" | "error"; parse_error: string | null; created_at: string;
}

export interface AnalysisPoint {
  id: string; label: string; lat: number; lng: number;
  score: number; priority: "high" | "medium" | "low";
  color: string; rank: number; reasons_json: string[];
}

export interface Analysis {
  id: string; project_id: string; phase: string; status: string;
  algorithm_version: string; summary_json: Record<string, unknown> | null;
  started_at: string | null; finished_at: string | null; created_at: string;
  points: AnalysisPoint[];
}

// ─── Funções de API ───────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { name: string; email: string; password: string }) =>
    api.post<TokenResponse>("/api/v1/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post<TokenResponse>("/api/v1/auth/login", data),
  me: () => api.get<User>("/api/v1/auth/me"),
};

export const projectsApi = {
  list: () => api.get<Project[]>("/api/v1/projects"),
  get: (id: string) => api.get<Project>(`/api/v1/projects/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post<Project>("/api/v1/projects", data),
  update: (id: string, data: Partial<Project>) =>
    api.patch<Project>(`/api/v1/projects/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/projects/${id}`),
  uploadArea: (id: string, file: File) => {
    const fd = new FormData(); fd.append("file", file);
    return api.post<ProjectArea>(`/api/v1/projects/${id}/area/upload`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getArea: (id: string) => api.get<ProjectArea | null>(`/api/v1/projects/${id}/area`),
  runAnalysis: (id: string) =>
    api.post<Analysis>(`/api/v1/projects/${id}/analyses`),
  getLatestAnalysis: (id: string) =>
    api.get<Analysis | null>(`/api/v1/projects/${id}/analyses/latest`),
};
