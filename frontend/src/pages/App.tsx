import { FormEvent, useEffect, useMemo, useState } from "react";
import { Activity, BarChart3, Clock, Copy, Gauge, Link2, Loader2, MousePointerClick, Shield } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, type AnalyticsRead, type LinkListItem, type LinkRead } from "../lib/api";

export function App() {
  const [links, setLinks] = useState<LinkListItem[]>([]);
  const [created, setCreated] = useState<LinkRead | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsRead | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const totalClicks = useMemo(() => links.reduce((sum, link) => sum + link.click_count, 0), [links]);

  async function refreshLinks() {
    setLinks(await api.listLinks());
  }

  useEffect(() => {
    refreshLinks().catch((err) => setError(err instanceof Error ? err.message : "Could not load links."));
  }, []);

  async function createLink(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const payload = {
        original_url: String(form.get("original_url")),
        custom_alias: String(form.get("custom_alias") || "") || undefined,
        expires_at: String(form.get("expires_at") || "") || undefined,
      };
      const result = await api.createLink(payload);
      setCreated(result);
      setAnalytics(await api.getAnalytics(result.code));
      await refreshLinks();
      event.currentTarget.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create short link.");
    } finally {
      setLoading(false);
    }
  }

  async function selectAnalytics(code: string) {
    setAnalytics(await api.getAnalytics(code));
  }

  async function copy(value: string) {
    await navigator.clipboard.writeText(value);
  }

  return (
    <main className="min-h-screen text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center bg-indigo-700 text-white">
              <Link2 size={22} />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">LinkForge</h1>
              <p className="text-sm text-slate-500">Distributed URL shortener with rate limiting and analytics</p>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="tag">Base62</span>
            <span className="tag">Redis-ready</span>
            <span className="tag">PostgreSQL-ready</span>
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[380px_1fr]">
        <aside className="space-y-6">
          <form onSubmit={createLink} className="panel space-y-4">
            <div className="flex items-center gap-3">
              <Shield className="text-indigo-700" />
              <h2 className="text-lg font-semibold">Create short URL</h2>
            </div>
            <label className="field-label">
              Destination URL
              <input name="original_url" type="url" required placeholder="https://example.com/very/long/path" className="text-field" />
            </label>
            <label className="field-label">
              Custom alias
              <input name="custom_alias" placeholder="launch-demo" className="text-field" />
            </label>
            <label className="field-label">
              Expiry
              <input name="expires_at" type="datetime-local" className="text-field" />
            </label>
            {error && <div className="border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
            <button className="primary-button w-full" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Link2 size={18} />}
              Shorten URL
            </button>
          </form>

          {created && (
            <div className="panel">
              <p className="text-sm font-semibold text-indigo-700">Latest short URL</p>
              <div className="mt-3 flex items-center gap-2">
                <a className="min-w-0 flex-1 truncate text-lg font-semibold" href={created.short_url} target="_blank" rel="noreferrer">
                  {created.short_url}
                </a>
                <button className="ghost-button" onClick={() => copy(created.short_url)} title="Copy short URL">
                  <Copy size={16} />
                </button>
              </div>
            </div>
          )}
        </aside>

        <section className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <Metric icon={<Link2 size={20} />} label="Short links" value={String(links.length)} />
            <Metric icon={<MousePointerClick size={20} />} label="Total clicks" value={String(totalClicks)} />
            <Metric icon={<Gauge size={20} />} label="Create limit" value="20/min" />
          </div>

          <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
            <div className="panel">
              <div className="mb-4 flex items-center gap-2">
                <Activity size={18} />
                <h2 className="font-semibold">Recent links</h2>
              </div>
              <div className="space-y-3">
                {links.length === 0 && <p className="text-sm text-slate-500">Create a short URL to see it here.</p>}
                {links.map((link) => (
                  <button key={link.code} className="w-full border border-slate-200 bg-slate-50 p-4 text-left transition hover:border-indigo-700" onClick={() => selectAnalytics(link.code)}>
                    <div className="flex items-center justify-between gap-3">
                      <span className="truncate font-semibold">{link.short_url}</span>
                      <span className="tag">{link.click_count} clicks</span>
                    </div>
                    <p className="mt-2 truncate text-sm text-slate-500">{link.original_url}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="mb-4 flex items-center gap-2">
                <BarChart3 size={18} />
                <h2 className="font-semibold">Analytics</h2>
              </div>
              {analytics ? (
                <div className="space-y-5">
                  <div className="grid grid-cols-2 gap-3">
                    <Metric compact icon={<MousePointerClick size={18} />} label="Total" value={String(analytics.total_clicks)} />
                    <Metric compact icon={<Clock size={18} />} label="24h" value={String(analytics.clicks_last_24h)} />
                  </div>
                  <div className="h-56">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analytics.top_referrers.length ? analytics.top_referrers : [{ referer: "Direct", clicks: analytics.total_clicks }]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="referer" />
                        <YAxis allowDecimals={false} />
                        <Tooltip />
                        <Bar dataKey="clicks" fill="#4338ca" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-2">
                    {analytics.recent_clicks.map((click, index) => (
                      <div key={`${click.created_at}-${index}`} className="border border-slate-200 p-3 text-sm">
                        <p className="font-medium">{click.ip_address}</p>
                        <p className="text-slate-500">{new Date(click.created_at).toLocaleString()}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500">Select a link to inspect click analytics.</p>
              )}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

function Metric({ icon, label, value, compact = false }: { icon: JSX.Element; label: string; value: string; compact?: boolean }) {
  return (
    <div className={compact ? "border border-slate-200 bg-slate-50 p-3" : "metric"}>
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center bg-indigo-50 text-indigo-800">{icon}</div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
          <p className={compact ? "text-xl font-semibold" : "text-3xl font-semibold"}>{value}</p>
        </div>
      </div>
    </div>
  );
}
