"use client";

/**
 * ProcessingCard — animated progress and spinner shown during upload/processing.
 *
 * Two phases:
 * 1. "uploading" — shows a real percentage progress bar (from XHR upload events)
 * 2. "processing" — shows an indeterminate pulse animation (server processing)
 */

interface ProcessingCardProps {
  phase: "uploading" | "processing";
  progress?: number; // 0-100, only for "uploading" phase
}

export function ProcessingCard({ phase, progress = 0 }: ProcessingCardProps) {
  const isUploading = phase === "uploading";
  const isProcessing = phase === "processing";

  return (
    <div
      className="w-full rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-8"
      role="status"
      aria-live="polite"
      aria-label={isUploading ? `Uploading: ${progress}%` : "Processing statement"}
    >
      {/* Animated icon */}
      <div className="flex justify-center mb-6">
        <div className="relative">
          {/* Outer ring */}
          <div className="w-20 h-20 rounded-full border-4 border-violet-500/20" />
          {/* Spinning arc */}
          <div className="absolute inset-0 w-20 h-20 rounded-full border-4 border-transparent border-t-violet-500 animate-spin" />
          {/* Inner icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            {isUploading ? (
              <svg className="w-8 h-8 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            ) : (
              <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            )}
          </div>
        </div>
      </div>

      {/* Status text */}
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold text-white mb-1">
          {isUploading ? "Uploading your statement..." : "Parsing transactions..."}
        </h3>
        <p className="text-sm text-white/50">
          {isUploading
            ? "Sending your PDF to BankScan"
            : "Extracting and validating all transactions"}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
        {isUploading ? (
          <div
            className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        ) : (
          /* Indeterminate shimmer bar for processing phase */
          <div className="h-full bg-gradient-to-r from-violet-500/0 via-indigo-500 to-violet-500/0 rounded-full animate-pulse w-full" />
        )}
      </div>

      {/* Progress percentage */}
      {isUploading && (
        <p className="text-center text-sm text-violet-300 font-mono mt-3">
          {progress}%
        </p>
      )}

      {/* Processing step indicators */}
      {isProcessing && (
        <div className="mt-6 space-y-2">
          {[
            "Detecting bank format...",
            "Extracting header fields...",
            "Parsing transaction table...",
            "Generating CSV & Excel exports...",
          ].map((step, i) => (
            <div
              key={step}
              className="flex items-center gap-3 text-sm text-white/40"
              style={{ animationDelay: `${i * 0.5}s` }}
            >
              <div className="w-4 h-4 rounded-full border-2 border-indigo-400/40 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-indigo-400/60 animate-pulse" />
              </div>
              {step}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
