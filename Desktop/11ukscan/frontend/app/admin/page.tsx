"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { getAdminScanDetail, getAdminScans, getAdminStats } from "@/services/api";
import { AdminStats, ScanDetail, ScanSummary } from "@/types/statement";

function StatCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/3 p-4">
      <p className="text-xs text-white/40 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${accent ?? "text-white"}`}>{value}</p>
    </div>
  );
}

function SkeletonRow() {
  return (
    <tr className="border-t border-white/5">
      {Array.from({ length: 7 }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-3 rounded bg-white/5 animate-pulse" />
        </td>
      ))}
    </tr>
  );
}

export default function AdminPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [scans, setScans] = useState<ScanSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ScanDetail | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);

  async function load(isRefresh = false) {
    if (isRefresh) setRefreshing(true);
    setError(null);
    try {
      const [statsData, scansData] = await Promise.all([getAdminStats(), getAdminScans()]);
      setStats(statsData);
      setScans(scansData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (!selectedJobId) {
      setDetail(null);
      setDetailError(null);
      return;
    }
    let cancelled = false;
    setDetail(null);
    setDetailError(null);
    getAdminScanDetail(selectedJobId)
      .then((data) => {
        if (!cancelled) setDetail(data);
      })
      .catch((err) => {
        if (!cancelled) setDetailError(err instanceof Error ? err.message : "Failed to load scan detail.");
      });
    return () => {
      cancelled = true;
    };
  }, [selectedJobId]);

  const filteredScans = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return scans;
    return scans.filter(
      (s) =>
        s.account_holder.toLowerCase().includes(q) ||
        s.bank_name.toLowerCase().includes(q) ||
        s.job_id.toLowerCase().includes(q)
    );
  }, [scans, query]);

  return (
    <main className="min-h-screen bg-[#0a0a14] text-white relative overflow-hidden">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-violet-600/10 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-indigo-600/10 blur-[120px]" />
      </div>

      <header className="relative z-10 border-b border-white/5 bg-white/2 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-900/40">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v18M3 9h18" />
              </svg>
            </div>
            <div>
              <h1 className="text-base font-bold tracking-tight">BankScan Admin</h1>
              <p className="text-xs text-white/40 leading-none">Scan activity for this server process</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => load(true)}
              disabled={refreshing}
              className="text-xs text-white/60 hover:text-white px-3 py-1.5 rounded-full border border-white/10 hover:border-white/20 transition-colors disabled:opacity-40 flex items-center gap-1.5"
            >
              <svg
                className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h5M20 20v-5h-5M4 9a9 9 0 0114-6.7M20 15a9 9 0 01-14 6.7" />
              </svg>
              Refresh
            </button>
            <Link
              href="/"
              className="text-xs text-white/40 hover:text-white/70 px-3 py-1.5 rounded-full border border-white/10 hover:border-white/20 transition-colors"
            >
              ← Back to dashboard
            </Link>
          </div>
        </div>
      </header>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">
        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300 mb-8 flex items-center justify-between gap-4">
            <span>{error}</span>
            <button
              onClick={() => load()}
              className="text-xs px-3 py-1.5 rounded-full border border-red-400/30 hover:bg-red-500/10 transition-colors shrink-0"
            >
              Retry
            </button>
          </div>
        )}

        {!error && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
              {loading || !stats ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-white/10 bg-white/3 p-4">
                    <div className="h-3 w-20 rounded bg-white/5 animate-pulse mb-2" />
                    <div className="h-7 w-12 rounded bg-white/5 animate-pulse" />
                  </div>
                ))
              ) : (
                <>
                  <StatCard label="Total Scans" value={stats.total_scans} />
                  <StatCard label="Total Transactions" value={stats.total_transactions} />
                  <StatCard
                    label="Total Warnings"
                    value={stats.total_warnings}
                    accent={stats.total_warnings > 0 ? "text-amber-400" : "text-white"}
                  />
                  <StatCard label="Banks Seen" value={stats.banks.length || "—"} />
                </>
              )}
            </div>

            <div className="flex items-center justify-between mb-3 gap-4">
              <h2 className="text-sm font-semibold text-white/70">Scans</h2>
              <div className="relative w-full max-w-xs">
                <svg
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/30"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" />
                </svg>
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search by name, bank, or job ID…"
                  className="w-full rounded-full border border-white/10 bg-white/5 pl-8 pr-4 py-1.5 text-xs text-white placeholder-white/30 outline-none focus:border-violet-500/50"
                />
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-white/5 text-white/50 text-xs uppercase tracking-wide">
                  <tr>
                    <th className="text-left px-4 py-3">Account Holder</th>
                    <th className="text-left px-4 py-3">Bank</th>
                    <th className="text-left px-4 py-3">Period</th>
                    <th className="text-right px-4 py-3">Transactions</th>
                    <th className="text-right px-4 py-3">Pages</th>
                    <th className="text-right px-4 py-3">Warnings</th>
                    <th className="text-left px-4 py-3">Processed At</th>
                  </tr>
                </thead>
                <tbody>
                  {loading &&
                    Array.from({ length: 3 }).map((_, i) => <SkeletonRow key={i} />)}

                  {!loading && filteredScans.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-4 py-10 text-center text-white/30">
                        {scans.length === 0
                          ? "No scans processed yet on this server instance."
                          : "No scans match your search."}
                      </td>
                    </tr>
                  )}

                  {!loading &&
                    filteredScans.map((scan) => (
                      <tr
                        key={scan.job_id}
                        onClick={() => setSelectedJobId(scan.job_id)}
                        className="border-t border-white/5 hover:bg-white/5 cursor-pointer transition-colors"
                      >
                        <td className="px-4 py-3 font-medium">{scan.account_holder}</td>
                        <td className="px-4 py-3 text-white/60">{scan.bank_name}</td>
                        <td className="px-4 py-3 text-white/60">
                          {scan.period_start} → {scan.period_end}
                        </td>
                        <td className="px-4 py-3 text-right">{scan.transaction_count}</td>
                        <td className="px-4 py-3 text-right">{scan.page_count}</td>
                        <td className="px-4 py-3 text-right">
                          {scan.warnings_count > 0 ? (
                            <span className="inline-flex items-center justify-center min-w-[1.5rem] rounded-full bg-amber-500/15 text-amber-400 px-2 py-0.5 text-xs font-medium">
                              {scan.warnings_count}
                            </span>
                          ) : (
                            <span className="text-white/30">0</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-white/40">
                          {new Date(scan.processed_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {/* Detail slide-over */}
      {selectedJobId && (
        <div className="fixed inset-0 z-20 flex justify-end">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setSelectedJobId(null)}
          />
          <div className="relative z-10 w-full max-w-md h-full bg-[#0a0a14] border-l border-white/10 p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold">Scan Detail</h3>
              <button
                onClick={() => setSelectedJobId(null)}
                className="w-8 h-8 rounded-full border border-white/10 hover:border-white/20 flex items-center justify-center text-white/50 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {detailError && (
              <p className="text-sm text-red-300">{detailError}</p>
            )}

            {!detail && !detailError && (
              <div className="space-y-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="h-4 rounded bg-white/5 animate-pulse" />
                ))}
              </div>
            )}

            {detail && (
              <div className="space-y-5 text-sm">
                <div>
                  <p className="text-xs text-white/40 mb-1">Account Holder</p>
                  <p className="font-medium">{detail.account_holder}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-white/40 mb-1">Bank</p>
                    <p>{detail.bank_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Statement Type</p>
                    <p>{detail.statement_type || "—"}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Account Number</p>
                    <p>{detail.account_number}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Sort Code</p>
                    <p>{detail.sort_code}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Period</p>
                    <p>{detail.period_start} → {detail.period_end}</p>
                  </div>
                  <div>
                    <p className="text-xs text-white/40 mb-1">Pages</p>
                    <p>{detail.page_count}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3">
                    <p className="text-xs text-white/40 mb-1">Total Credits</p>
                    <p className="text-emerald-400 font-semibold">£{detail.total_credits}</p>
                  </div>
                  <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3">
                    <p className="text-xs text-white/40 mb-1">Total Debits</p>
                    <p className="text-red-400 font-semibold">£{detail.total_debits}</p>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-white/40 mb-1">Transactions</p>
                  <p>{detail.transaction_count}</p>
                </div>

                {detail.warnings.length > 0 && (
                  <div>
                    <p className="text-xs text-white/40 mb-2">Warnings ({detail.warnings.length})</p>
                    <ul className="space-y-1.5">
                      {detail.warnings.map((w, i) => (
                        <li
                          key={i}
                          className="text-xs text-amber-300 bg-amber-500/10 border border-amber-500/20 rounded-lg px-3 py-2"
                        >
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="pt-2 border-t border-white/10">
                  <p className="text-xs text-white/30 break-all">Job ID: {detail.job_id}</p>
                  <p className="text-xs text-white/30">
                    Processed: {new Date(detail.processed_at).toLocaleString()}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
