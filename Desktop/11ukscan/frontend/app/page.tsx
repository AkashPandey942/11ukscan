"use client";

import { useUpload } from "@/hooks/useUpload";
import { UploadZone } from "@/components/UploadZone";
import { ProcessingCard } from "@/components/ProcessingCard";
import { ResultCard } from "@/components/ResultCard";

export default function DashboardPage() {
  const { state, upload, reset } = useUpload();

  const isIdle = state.phase === "idle";
  const isUploading = state.phase === "uploading";
  const isProcessing = state.phase === "processing";
  const isSuccess = state.phase === "success";
  const isError = state.phase === "error";

  const isBusy = isUploading || isProcessing;

  return (
    <main className="min-h-screen bg-[#0a0a14] relative overflow-hidden">
      {/* ── Background ambient glows ── */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-violet-600/10 blur-[120px]" />
        <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-indigo-600/10 blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] rounded-full bg-violet-900/5 blur-[100px]" />
        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      {/* ── Header ── */}
      <header className="relative z-10 border-b border-white/5 bg-white/2 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Logo mark */}
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-900/40">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-base font-bold text-white tracking-tight">BankScan</h1>
              <p className="text-xs text-white/40 leading-none">Statement Parser</p>
            </div>
          </div>

          {/* Status badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-white/60 font-medium">Monzo Business</span>
          </div>
        </div>
      </header>

      {/* ── Main content ── */}
      <div className="relative z-10 max-w-2xl mx-auto px-6 py-16">

        {/* Hero text */}
        {isIdle && (
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-xs font-medium mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
              Monzo Business Statements Supported
            </div>
            <h2 className="text-4xl sm:text-5xl font-bold text-white mb-4 leading-tight tracking-tight">
              Parse your bank{" "}
              <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
                statement instantly
              </span>
            </h2>
            <p className="text-lg text-white/50 max-w-md mx-auto leading-relaxed">
              Upload your Monzo Business PDF and download a structured CSV or
              Excel file in seconds.
            </p>
          </div>
        )}

        {/* Upload zone */}
        {isIdle && (
          <UploadZone onFile={upload} disabled={isBusy} />
        )}

        {/* Processing indicator */}
        {(isUploading || isProcessing) && (
          <ProcessingCard
            phase={isUploading ? "uploading" : "processing"}
            progress={isUploading && state.phase === "uploading" ? state.progress : 0}
          />
        )}

        {/* Success result */}
        {isSuccess && state.phase === "success" && (
          <ResultCard data={state.data} onReset={reset} />
        )}

        {/* Error state */}
        {isError && state.phase === "error" && (
          <div className="w-full rounded-2xl border border-red-500/30 bg-red-500/10 p-8 text-center">
            <div className="flex justify-center mb-4">
              <div className="w-14 h-14 rounded-full bg-red-500/20 flex items-center justify-center">
                <svg className="w-7 h-7 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-red-300 mb-2">Processing Failed</h3>
            <p className="text-sm text-red-200/70 mb-6 max-w-md mx-auto">{state.message}</p>
            <button
              onClick={reset}
              id="retry-btn"
              className={[
                "px-8 py-3 rounded-xl font-semibold text-sm",
                "bg-red-500/20 hover:bg-red-500/30",
                "border border-red-500/30 text-red-300",
                "transition-all duration-200 hover:scale-[1.02]",
              ].join(" ")}
            >
              Try Again
            </button>
          </div>
        )}

        {/* Feature cards — shown only on idle */}
        {isIdle && (
          <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                icon: "🔒",
                title: "Secure",
                desc: "Files processed locally. Never stored permanently.",
              },
              {
                icon: "⚡",
                title: "Instant",
                desc: "60 pages processed in under 30 seconds.",
              },
              {
                icon: "📊",
                title: "Structured",
                desc: "Clean CSV + styled Excel with summary sheet.",
              },
            ].map(({ icon, title, desc }) => (
              <div
                key={title}
                className="p-4 rounded-xl border border-white/5 bg-white/3 hover:bg-white/5 transition-colors duration-200"
              >
                <div className="text-2xl mb-2">{icon}</div>
                <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
                <p className="text-xs text-white/40 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-white/5 mt-16">
        <div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between flex-wrap gap-4">
          <p className="text-xs text-white/30">
            © 2026 BankScan · Enterprise PDF Parser
          </p>
          <p className="text-xs text-white/20">
            Supports Monzo Business · More banks coming soon
          </p>
        </div>
      </footer>
    </main>
  );
}
