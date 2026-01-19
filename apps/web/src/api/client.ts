/** API client for backend communication */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface Production {
  code: string;
  title: string;
}

export interface ShotSummary {
  shot_code: string;
  scene: string | null;
  stage: string;
  description?: string | null;
}

export interface ShotDetail {
  shot_code: string;
  scene: string | null;
  description: string | null;
}

export interface Version {
  id: string;
  version_type: string;
  storage_uri: string;
  codec: string | null;
  container: string | null;
  fps: number | null;
  timecode_in: string | null;
  timecode_out: string | null;
  created_at: string;
}

export interface Event {
  id: string;
  event_type: string;
  version_id: string | null;
  package_id: string | null;
  actor: string | null;
  tool: string | null;
  created_at: string;
}

export interface Package {
  id: string;
  package_type: string;
  label: string;
  vendor: string | null;
  created_at: string;
}

export interface LineageNode {
  version_id: string;
  version_type: string;
  derived_from: string | null;
}

export interface AskResponse {
  template: string;
  params: Record<string, unknown>;
  answer: string;
  evidence: Record<string, unknown[]>;
  explanation: string;
}

export interface AskClarificationResponse {
  status: 'needs_clarification';
  user_message: string;
  intent_id?: string | null;
  confidence?: number | null;
  missing_params?: string[] | null;
  ambiguity?: {
    candidates?: string[];
    clarification_kind?: string;
    original_question?: string;
  } | null;
}

export interface AskUnanswerableResponse {
  status: 'unanswerable';
  error_code: string;
  message: string;
  intent_id?: string | null;
  confidence?: number | null;
}

export interface AskConfig {
  nl_enabled: boolean;
  dual_mode_ui: boolean;
  default_mode: string;
}

export interface AskError {
  httpStatus: number;
  url: string;
  code: string;
  message: string;
  rawBody?: string;
  timestamp: string;
}

// Type definitions for error envelope parsing
type ErrorDetail = { code?: string; message?: string; category?: string };

// Type guard: check if value is a record (object with string keys)
function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === 'object' && x !== null && !Array.isArray(x);
}

// Extract error detail from either envelope format
function extractErrorDetail(parsed: unknown): ErrorDetail {
  if (!isRecord(parsed)) {
    return {};
  }

  // Check for FastAPI envelope format: { detail: { code, message, category } }
  if ('detail' in parsed && isRecord(parsed.detail)) {
    return {
      code: typeof parsed.detail.code === 'string' ? parsed.detail.code : undefined,
      message: typeof parsed.detail.message === 'string' ? parsed.detail.message : undefined,
      category: typeof parsed.detail.category === 'string' ? parsed.detail.category : undefined,
    };
  }

  // Check for flattened format: { code, message, category }
  return {
    code: typeof parsed.code === 'string' ? parsed.code : undefined,
    message: typeof parsed.message === 'string' ? parsed.message : undefined,
    category: typeof parsed.category === 'string' ? parsed.category : undefined,
  };
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const fullUrl = `${API_BASE_URL}${url}`;
  const response = await fetch(fullUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    // Try to parse JSON error response per Appendix E error envelope
    let errorDetail: ErrorDetail = {};
    let rawBody: string | undefined;

    try {
      const text = await response.text();
      rawBody = text;
      if (text) {
        const parsed: unknown = JSON.parse(text);
        errorDetail = extractErrorDetail(parsed);
      }
    } catch {
      // If parsing fails, use defaults
    }

    const error: AskError = {
      httpStatus: response.status,
      url: fullUrl,
      code: errorDetail.code || 'unknown_error',
      message: errorDetail.message || `HTTP ${response.status}`,
      rawBody,
      timestamp: new Date().toISOString(),
    };

    throw error;
  }

  return response.json();
}

export const api = {
  // Productions
  getProductions: () => fetchJson<{ productions: Production[] }>('/api/productions'),

  // Shots
  getShots: (productionCode: string) =>
    fetchJson<{ shots: ShotSummary[] }>(`/api/shots?production_code=${productionCode}`),

  getShotDetail: (shotCode: string, productionCode: string) =>
    fetchJson<{ shot: ShotDetail }>(`/api/shots/${shotCode}?production_code=${productionCode}`),

  getShotLineage: (shotCode: string, productionCode: string) =>
    fetchJson<{ shot_code: string; chain: LineageNode[] }>(
      `/api/shots/${shotCode}/lineage?production_code=${productionCode}`,
    ),

  getShotEvents: (shotCode: string, productionCode: string) =>
    fetchJson<{ events: Event[] }>(
      `/api/shots/${shotCode}/events?production_code=${productionCode}`,
    ),

  // Packages
  getPackages: (productionCode: string) =>
    fetchJson<{ packages: Package[] }>(`/api/packages?production_code=${productionCode}`),

  getPackageDetail: (packageId: string) =>
    fetchJson<{
      package: Package;
      members: Array<{ version_id: string; version_type: string; storage_uri: string }>;
    }>(`/api/packages/${packageId}`),

  // Ask
  askQuestion: (
    productionCode: string,
    question: string,
    mode?: string,
    clarificationContext?: Record<string, unknown>,
    signal?: AbortSignal,
  ) =>
    fetchJson<AskResponse | AskClarificationResponse | AskUnanswerableResponse>('/api/ask', {
      method: 'POST',
      body: JSON.stringify({
        production_code: productionCode,
        question,
        mode: mode || 'deterministic',
        clarification_context: clarificationContext,
      }),
      signal,
    }),

  // Ask Config
  getAskConfig: () => fetchJson<AskConfig>('/api/config/ask'),

  // Seed
  loadSeed: (reset: boolean = false) =>
    fetchJson<{ ok: boolean; production_code: string; shots_loaded: number }>('/api/import/seed', {
      method: 'POST',
      body: JSON.stringify({ mode: reset ? 'reset_and_seed' : null }),
    }),
};
