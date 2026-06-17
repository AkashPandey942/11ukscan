/**
 * TypeScript type definitions for BankScan API responses.
 * These mirror the Pydantic schemas defined in backend/app/schemas/upload.py
 */

export interface StatementInfo {
  bank_name: string;
  account_holder: string;
  period_start: string; // ISO date string
  period_end: string;   // ISO date string
  account_number: string;
  sort_code: string;
  statement_type: string;
}

export interface UploadSuccessResponse {
  status: "success";
  job_id: string;
  bank_name: string;
  statement_info: StatementInfo;
  transaction_count: number;
  page_count: number;
  warnings: string[];
  download_csv: string;
  download_excel: string;
}

export interface ErrorResponse {
  status: "error";
  code: string;
  message: string;
  request_id?: string;
}

export type ApiResponse = UploadSuccessResponse | ErrorResponse;

export type UploadState =
  | { phase: "idle" }
  | { phase: "uploading"; progress: number }
  | { phase: "processing" }
  | { phase: "success"; data: UploadSuccessResponse }
  | { phase: "error"; message: string; code?: string };

/** Mirrors backend/app/schemas/admin.py::ScanSummarySchema */
export interface ScanSummary {
  job_id: string;
  bank_name: string;
  account_holder: string;
  period_start: string;
  period_end: string;
  transaction_count: number;
  page_count: number;
  warnings_count: number;
  processed_at: string;
}

/** Mirrors backend/app/schemas/admin.py::AdminStatsSchema */
export interface AdminStats {
  total_scans: number;
  total_transactions: number;
  total_warnings: number;
  banks: string[];
}

/** Mirrors backend/app/schemas/admin.py::ScanDetailSchema */
export interface ScanDetail extends ScanSummary {
  account_number: string;
  sort_code: string;
  statement_type: string;
  warnings: string[];
  total_credits: string;
  total_debits: string;
}
