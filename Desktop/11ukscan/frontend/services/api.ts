/**
 * API client for BankScan backend.
 *
 * Uses the Fetch API for upload with progress tracking via XMLHttpRequest.
 * Base URL is configured via NEXT_PUBLIC_API_BASE_URL environment variable.
 */

import { AdminStats, ScanDetail, ScanSummary } from "@/types/statement";
import { UploadSuccessResponse } from "@/types/statement";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const ADMIN_API_TOKEN = process.env.NEXT_PUBLIC_ADMIN_API_TOKEN ?? "";

/**
 * Upload a PDF file to the backend with progress tracking.
 *
 * Uses XMLHttpRequest (not fetch) because fetch doesn't support upload progress.
 *
 * @param file         The PDF File object from the file input / drop zone.
 * @param onProgress   Callback called with progress percentage (0-100).
 * @returns            Parsed UploadSuccessResponse from the API.
 * @throws             Error with message from API error response.
 */
export function uploadStatement(
  file: File,
  onProgress: (percent: number) => void
): Promise<UploadSuccessResponse> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    });

    xhr.addEventListener("load", () => {
      try {
        const data = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300 && data.status === "success") {
          resolve(data as UploadSuccessResponse);
        } else {
          reject(
            new Error(
              data.message ?? `Upload failed with status ${xhr.status}`
            )
          );
        }
      } catch {
        reject(new Error("Failed to parse server response."));
      }
    });

    xhr.addEventListener("error", () => {
      reject(new Error("Network error — could not reach the server."));
    });

    xhr.addEventListener("timeout", () => {
      reject(new Error("Upload timed out. Please try again."));
    });

    xhr.timeout = 120_000; // 2 minutes
    xhr.open("POST", `${API_BASE_URL}/api/v1/upload`);
    xhr.send(formData);
  });
}

/**
 * Build the full download URL for a CSV export.
 *
 * @param jobId  UUID string of the processing job.
 */
export function getCSVDownloadUrl(jobId: string): string {
  return `${API_BASE_URL}/api/v1/download/csv/${jobId}`;
}

/**
 * Build the full download URL for an Excel export.
 *
 * @param jobId  UUID string of the processing job.
 */
export function getExcelDownloadUrl(jobId: string): string {
  return `${API_BASE_URL}/api/v1/download/excel/${jobId}`;
}

async function adminFetch<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "X-Admin-Token": ADMIN_API_TOKEN },
      cache: "no-store",
    });
  } catch {
    throw new Error(
      `Could not reach the backend at ${API_BASE_URL}. Make sure the server is running.`
    );
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.message ?? `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

/** Fetch aggregate counters for the admin dashboard. */
export function getAdminStats(): Promise<AdminStats> {
  return adminFetch<AdminStats>("/api/v1/admin/stats");
}

/** Fetch a summary list of every scan processed since the backend process started. */
export function getAdminScans(): Promise<ScanSummary[]> {
  return adminFetch<ScanSummary[]>("/api/v1/admin/scans");
}

/** Fetch full detail (including financial totals) for one scan. */
export function getAdminScanDetail(jobId: string): Promise<ScanDetail> {
  return adminFetch<ScanDetail>(`/api/v1/admin/scans/${jobId}`);
}
