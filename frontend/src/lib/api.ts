const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export type LinkRead = {
  id: number;
  code: string;
  original_url: string;
  short_url: string;
  custom_alias: string | null;
  expires_at: string | null;
  is_active: boolean;
  click_count: number;
  created_at: string;
};

export type LinkListItem = Omit<LinkRead, "id" | "custom_alias" | "is_active">;

export type AnalyticsRead = {
  code: string;
  original_url: string;
  short_url: string;
  total_clicks: number;
  clicks_last_24h: number;
  top_referrers: Array<{ referer: string; clicks: number }>;
  recent_clicks: Array<{ ip_address: string; referer: string; country: string; created_at: string }>;
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed.");
  }
  return data as T;
}

export const api = {
  createLink(payload: { original_url: string; custom_alias?: string; expires_at?: string }) {
    return request<LinkRead>("/api/links", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  },
  listLinks() {
    return request<LinkListItem[]>("/api/links");
  },
  getAnalytics(code: string) {
    return request<AnalyticsRead>(`/api/links/${code}/analytics`);
  },
};
