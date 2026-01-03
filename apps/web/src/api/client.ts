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
  params: Record<string, any>;
  answer: string;
  evidence: Record<string, any[]>;
  explanation: string;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP ${response.status}`);
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
  askQuestion: (productionCode: string, question: string) =>
    fetchJson<AskResponse>('/api/ask', {
      method: 'POST',
      body: JSON.stringify({ production_code: productionCode, question }),
    }),

  // Seed
  loadSeed: (reset: boolean = false) =>
    fetchJson<{ ok: boolean; production_code: string; shots_loaded: number }>('/api/import/seed', {
      method: 'POST',
      body: JSON.stringify({ mode: reset ? 'reset_and_seed' : null }),
    }),
};
