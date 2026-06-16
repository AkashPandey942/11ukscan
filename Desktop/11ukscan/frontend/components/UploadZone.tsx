"use client";

/**
 * UploadZone — drag-and-drop PDF upload area with file validation feedback.
 *
 * Uses native HTML5 drag events (no external dependencies).
 * Accepts drag-and-drop OR click-to-browse interactions.
 */

import { useCallback, useRef, useState } from "react";

interface UploadZoneProps {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export function UploadZone({ onFile, disabled = false }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [dragError, setDragError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    (file: File | null) => {
      setDragError(null);
      if (!file) return;
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setDragError("Only PDF files are accepted.");
        return;
      }
      onFile(file);
    },
    [onFile]
  );

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const onDragLeave = () => setIsDragging(false);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0] ?? null;
    handleFile(file);
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files?.[0] ?? null);
    // Reset input so same file can be re-uploaded
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={[
        "relative flex flex-col items-center justify-center",
        "w-full min-h-[320px] rounded-2xl border-2 border-dashed",
        "transition-all duration-300 cursor-pointer select-none",
        "group",
        isDragging
          ? "border-violet-400 bg-violet-950/40 scale-[1.01] shadow-[0_0_40px_rgba(139,92,246,0.3)]"
          : "border-white/20 bg-white/5 hover:border-violet-400/60 hover:bg-white/10",
        disabled ? "opacity-50 cursor-not-allowed" : "",
      ].join(" ")}
      role="button"
      aria-label="Upload PDF bank statement"
      id="upload-zone"
    >
      {/* Glowing background blob on drag */}
      <div
        className={[
          "absolute inset-0 rounded-2xl transition-opacity duration-500",
          "bg-gradient-to-br from-violet-600/10 to-indigo-600/10",
          isDragging ? "opacity-100" : "opacity-0",
        ].join(" ")}
      />

      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={onInputChange}
        className="hidden"
        id="pdf-file-input"
        disabled={disabled}
      />

      {/* Icon */}
      <div
        className={[
          "mb-6 p-5 rounded-full transition-all duration-300",
          "bg-gradient-to-br from-violet-500/20 to-indigo-500/20",
          "border border-white/10",
          isDragging ? "scale-110 border-violet-400/40" : "group-hover:scale-105",
        ].join(" ")}
      >
        <svg
          className={[
            "w-12 h-12 transition-colors duration-300",
            isDragging ? "text-violet-300" : "text-violet-400 group-hover:text-violet-300",
          ].join(" ")}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
          />
        </svg>
      </div>

      {/* Text */}
      <div className="text-center z-10 px-6">
        <p className="text-xl font-semibold text-white mb-2">
          {isDragging ? "Drop your PDF here" : "Drag & drop your statement"}
        </p>
        <p className="text-sm text-white/50 mb-4">
          or{" "}
          <span className="text-violet-400 underline underline-offset-2 hover:text-violet-300">
            click to browse
          </span>
        </p>

        {/* Constraints */}
        <div className="flex items-center gap-4 justify-center flex-wrap">
          {[
            { icon: "📄", label: "PDF only" },
            { icon: "📏", label: "Max 50 MB" },
            { icon: "📃", label: "Up to 60 pages" },
            { icon: "🏦", label: "Monzo Business" },
          ].map(({ icon, label }) => (
            <span
              key={label}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-white/5 text-white/60 border border-white/10"
            >
              <span>{icon}</span>
              <span>{label}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Drag error */}
      {dragError && (
        <p className="mt-4 text-sm text-red-400 font-medium z-10">{dragError}</p>
      )}
    </div>
  );
}
