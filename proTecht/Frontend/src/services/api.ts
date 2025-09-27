// Simple API client for proTecht AC endpoints
export const API_BASE = (import.meta as any).env.VITE_API_BASE ?? 'http://localhost:8000/api';
export const WS_BASE = (import.meta as any).env.VITE_WS_BASE ?? (API_BASE.replace(/^http/, 'ws').replace(/\/api$/, '') + '/ws');

export interface AWSService {
  id: 'iam-config' | 'identity-center' | 'aws-config' | 's3-policies' | 'kms' | 'cloudtrail' | 'waf' | 'guardduty' | 'security-hub' | 'vpc-cloudfront';
  title: string;
  lastUpdated: string;
  status: 'Current' | 'Warning' | 'Error' | string;
  kpis: Record<string, number | string | boolean>;
  mappedControls: string[];
  evidenceSnippet?: string;
}

export interface ACControl {
  id: string;
  name: string;
  status: 'pass' | 'partial' | 'fail' | 'unknown';
  score: number;
  confidence: number;
  reasons: string[];
  missingEvidence: string[];
  evidenceSources: string[];
  technicalResult: Record<string, unknown>;
}

export async function getAWSServices(): Promise<AWSService[]> {
  const res = await fetch(`${API_BASE}/evidence/aws/services`);
  if (!res.ok) throw new Error('Failed to load services');
  const json = await res.json();
  return json.data as AWSService[];
}

export async function getServiceDetail(id: AWSService['id']): Promise<Record<string, unknown>> {
  const map: Record<string, string> = {
    'iam-config': 'iam',
    'identity-center': 'sso',
    'aws-config': 'config',
    's3-policies': 's3',
    'security-hub': 'security_hub',
    'vpc-cloudfront': 'vpc_cloudfront',
  };
  const target = map[id] ?? id;
  const res = await fetch(`${API_BASE}/evidence/aws/services/${target}`);
  if (!res.ok) throw new Error('Failed to load service detail');
  const json = await res.json();
  return json.data as Record<string, unknown>;
}

export async function recollectAWS(regions?: string): Promise<{ status: string; collected_keys: string[]; timestamp: string }> {
  const url = new URL(`${API_BASE}/evidence/aws/recollect`);
  if (regions) url.searchParams.set('regions', regions);
  const headers: Record<string, string> = {};
  const token = localStorage.getItem('jwt');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(url, { method: 'POST', headers });
  if (!res.ok) throw new Error('Re-collect failed');
  return res.json() as Promise<{ status: string; collected_keys: string[]; timestamp: string }>;
}

// Realtime progress websocket
export function connectProgress(onEvent: (ev: any) => void): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/progress`);
  ws.onmessage = (msg) => {
    try {
      const data = JSON.parse(msg.data);
      onEvent(data);
    } catch {}
  };
  return ws;
}

// Polling recollect with embedded progress array
export async function recollectWithProgress(regions: string): Promise<{progress: any[]}> {
  const response = await fetch(`${API_BASE}/evidence/aws/recollect?regions=${encodeURIComponent(regions)}`, { method: 'POST' });
  if (!response.ok) throw new Error('Re-collect failed');
  const data = await response.json();
  return { progress: data.progress ?? [] };
}

export async function getACControls(): Promise<ACControl[]> {
  const res = await fetch(`${API_BASE}/controls`);
  if (!res.ok) throw new Error('Failed to load controls');
  const json = await res.json();
  return json.data as ACControl[];
}

export async function getACControlDetail(controlId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/controls/${controlId}`);
  if (!res.ok) throw new Error('Failed to load control detail');
  const json = await res.json();
  return json.data;
}

export async function uploadPolicy(file: File, policyName?: string): Promise<any> {
  const form = new FormData();
  form.append('file', file);
  if (policyName) form.append('policy_name', policyName);
  const headers: Record<string, string> = {};
  const token = localStorage.getItem('jwt');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/policies/upload`, { method: 'POST', body: form, headers });
  if (!res.ok) throw new Error('Policy upload failed');
  return res.json();
}

export async function reanalyzePolicy(policyId: string): Promise<any> {
  const headers: Record<string, string> = {};
  const token = localStorage.getItem('jwt');
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/policies/${policyId}/reanalyze`, { method: 'POST', headers });
  if (!res.ok) throw new Error('Policy reanalysis failed');
  return res.json();
}

export interface PolicyItem {
  id: string;
  name: string;
  controlsMapped: string[];
  lastAnalyzed: string;
  status: string;
  type: 'non-technical' | 'mixed' | string;
  summary?: string;
  reasons?: string[];
  missing?: string[];
  recommendations?: string[];
  citations?: string[];
}

export async function getPolicies(): Promise<PolicyItem[]> {
  const res = await fetch(`${API_BASE}/policies`);
  if (!res.ok) throw new Error('Failed to load policies');
  const json = await res.json();
  return json.data as PolicyItem[];
}

export async function exportServices(): Promise<void> {
  window.open(`${API_BASE}/export/services`, '_blank');
}

export async function exportControls(): Promise<void> {
  window.open(`${API_BASE}/export/controls`, '_blank');
}

export async function exportService(serviceId: string): Promise<void> {
  window.open(`${API_BASE}/export/service/${serviceId}`, '_blank');
}

export async function getAIAnalysisControls(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/analysis/controls`);
  if (!res.ok) throw new Error('Failed to load AI analysis');
  const json = await res.json();
  return json.data as any[];
}

export async function getAIAnalysisControl(controlId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/analysis/controls/${controlId}`);
  if (!res.ok) throw new Error(`Failed to load AI analysis for ${controlId}`);
  const json = await res.json();
  return json.data;
}


