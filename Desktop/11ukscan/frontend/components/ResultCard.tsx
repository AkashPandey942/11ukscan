"use client";

/**
 * ResultCard — displays the parsed statement summary and download buttons.
 * Shown after successful processing.
 */

import { UploadSuccessResponse } from "@/types/statement";
import { getCSVDownloadUrl, getExcelDownloadUrl } from "@/services/api";

interface ResultCardProps {
  data: UploadSuccessResponse;
  onReset: () => void;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export function ResultCard({ data, onReset }: ResultCardProps) {
  const { statement_info: info, transaction_count, page_count, warnings, job_id } = data;

  const csvUrl = getCSVDownloadUrl(job_id);
  const excelUrl = getExcelDownloadUrl(job_id);

  return (
    <div className="w-full space-y-4">
      {/* Success banner */}
      <div className="flex items-center gap-3 px-5 py-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
          <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-emerald-300">Statement processed successfully</p>
          <p className="text-xs text-emerald-400/70">{data.bank_name} · {page_count} pages · {transaction_count} transactions</p>
        </div>
      </div>

      {/* Account details grid */}
      <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden">
        {/* Card header */}
        <div className="px-6 py-4 bg-gradient-to-r from-violet-600/20 to-indigo-600/20 border-b border-white/10">
          <h3 className="text-sm font-semibold text-white/80 uppercase tracking-widest">Account Details</h3>
        </div>
        <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            { label: "Account Holder", value: info.account_holder },
            { label: "Bank", value: info.bank_name },
            { label: "Account Number", value: info.account_number || "—" },
            { label: "Sort Code", value: info.sort_code || "—" },
            { label: "Period Start", value: formatDate(info.period_start) },
            { label: "Period End", value: formatDate(info.period_end) },
            { label: "Statement Type", value: info.statement_type },
            { label: "Transactions", value: transaction_count.toString() },
          ].map(({ label, value }) => (
            <div key={label} className="flex flex-col gap-0.5">
              <span className="text-xs text-white/40 uppercase tracking-wider">{label}</span>
              <span className="text-sm font-medium text-white">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4">
          <p className="text-xs font-semibold text-amber-300 uppercase tracking-wider mb-2">
            ⚠ {warnings.length} parsing warning{warnings.length > 1 ? "s" : ""}
          </p>
          <ul className="space-y-1">
            {warnings.map((w, i) => (
              <li key={i} className="text-xs text-amber-200/70 leading-relaxed">• {w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Download buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <a
          href={csvUrl}
          download={`statement_${job_id}.csv`}
          id="download-csv-btn"
          className={[
            "flex items-center justify-center gap-3",
            "px-6 py-4 rounded-xl font-semibold text-sm",
            "bg-gradient-to-r from-violet-600 to-violet-700",
            "hover:from-violet-500 hover:to-violet-600",
            "text-white shadow-lg shadow-violet-900/40",
            "transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]",
            "border border-violet-500/30",
          ].join(" ")}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download CSV
        </a>

        <a
          href={excelUrl}
          download={`statement_${job_id}.xlsx`}
          id="download-excel-btn"
          className={[
            "flex items-center justify-center gap-3",
            "px-6 py-4 rounded-xl font-semibold text-sm",
            "bg-gradient-to-r from-emerald-600 to-teal-700",
            "hover:from-emerald-500 hover:to-teal-600",
            "text-white shadow-lg shadow-emerald-900/40",
            "transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]",
            "border border-emerald-500/30",
          ].join(" ")}
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download Excel
        </a>
      </div>

      {/* Process another */}
      <button
        onClick={onReset}
        id="process-another-btn"
        className={[
          "w-full py-3 rounded-xl text-sm font-medium",
          "text-white/50 border border-white/10",
          "hover:text-white hover:border-white/30 hover:bg-white/5",
          "transition-all duration-200",
        ].join(" ")}
      >
        ← Process another statement
      </button>
    </div>
  );
}
