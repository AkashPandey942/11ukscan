"use client";

/**
 * useUpload — custom hook for managing the PDF upload state machine.
 *
 * State transitions:
 *   idle → uploading (progress 0-100) → processing → success | error
 *
 * The hook handles:
 * - File validation (type + size check before upload)
 * - XHR upload with progress
 * - State transitions
 * - Reset functionality
 */

import { useCallback, useState } from "react";
import { uploadStatement } from "@/services/api";
import type { UploadState, UploadSuccessResponse } from "@/types/statement";

const MAX_FILE_SIZE_MB = 50;

export function useUpload() {
  const [state, setState] = useState<UploadState>({ phase: "idle" });

  const upload = useCallback(async (file: File) => {
    // Client-side pre-validation
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setState({
        phase: "error",
        message: "Please upload a PDF file.",
        code: "INVALID_FILE_TYPE",
      });
      return;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setState({
        phase: "error",
        message: `File is too large. Maximum size is ${MAX_FILE_SIZE_MB} MB.`,
        code: "FILE_TOO_LARGE",
      });
      return;
    }

    // Begin upload
    setState({ phase: "uploading", progress: 0 });

    try {
      const result = await uploadStatement(file, (percent) => {
        if (percent === 100) {
          // All bytes sent — now server is processing
          setState({ phase: "processing" });
        } else {
          setState({ phase: "uploading", progress: percent });
        }
      });

      setState({ phase: "success", data: result });
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "An unexpected error occurred. Please try again.";
      setState({ phase: "error", message });
    }
  }, []);

  const reset = useCallback(() => {
    setState({ phase: "idle" });
  }, []);

  return { state, upload, reset };
}
