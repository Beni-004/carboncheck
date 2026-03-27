/**
 * API Client for CarbonCheck Backend
 * Handles communication with FastAPI verification endpoints
 * Configured for multi-layer verification engine with extended timeouts
 */

import { getMockResult, getMockBulkResults, getMockLeaderboard, TrustScoreResult, BulkVerifyResult, LeaderboardEntry } from "./mock";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

// Extended timeout for new multi-layer verification engine (10-20s cold start)
const VERIFICATION_TIMEOUT_MS = 30000; // 30 seconds
const BULK_VERIFICATION_TIMEOUT_MS = 60000; // 60 seconds for bulk

interface FetchWithTimeoutOptions extends RequestInit {
  timeout?: number;
}

/**
 * Fetch wrapper with timeout support using AbortController
 */
async function fetchWithTimeout(
  url: string,
  options: FetchWithTimeoutOptions = {}
): Promise<Response> {
  const { timeout = VERIFICATION_TIMEOUT_MS, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(
        `Request timeout after ${timeout / 1000}s. The verification engine may be performing deep analysis. Please try again.`
      );
    }
    throw error;
  }
}

// Helper to log integration status
const logApiCall = (endpoint: string, useMock: boolean, error?: any) => {
  if (typeof window !== 'undefined') {
    console.log(`[CarbonCheck API] ${endpoint}:`, {
      mode: useMock ? 'MOCK' : 'LIVE',
      apiBase: API_BASE || 'NOT_SET',
      error: error?.message,
      timestamp: new Date().toISOString()
    });
  }
};

export async function verifyCreditId(
  creditId: string
): Promise<TrustScoreResult> {
  if (!API_BASE) {
    logApiCall('/api/verify', true);
    throw new Error('API_BASE not configured. Please set NEXT_PUBLIC_API_URL in .env.local');
  }

  try {
    const response = await fetchWithTimeout(`${API_BASE}/api/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ creditId }),
      timeout: VERIFICATION_TIMEOUT_MS,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `Verification failed with status ${response.status}`;
      throw new Error(errorMessage);
    }

    const data = await response.json();
    logApiCall('/api/verify', false);
    return data;
  } catch (error) {
    console.error("API call failed:", error);
    logApiCall('/api/verify', true, error);

    // Always throw the error so UI can show proper error state
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Verification request failed');
  }
}

export async function verifyBulkCredits(
  creditIds: string[]
): Promise<BulkVerifyResult> {
  if (!API_BASE) {
    logApiCall('/api/verify/bulk', true);
    throw new Error('API_BASE not configured. Please set NEXT_PUBLIC_API_URL in .env.local');
  }

  try {
    // Bulk requests may take longer, scale timeout with batch size
    const bulkTimeout = Math.max(BULK_VERIFICATION_TIMEOUT_MS, creditIds.length * 1000);
    
    const response = await fetchWithTimeout(`${API_BASE}/api/verify/bulk`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ creditIds }),
      timeout: bulkTimeout,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `Bulk verification failed with status ${response.status}`;
      throw new Error(errorMessage);
    }

    const data = await response.json();
    logApiCall('/api/verify/bulk', false);
    return data;
  } catch (error) {
    console.error("Bulk API call failed:", error);
    logApiCall('/api/verify/bulk', true, error);

    // Always throw the error so UI can show proper error state
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Bulk verification request failed');
  }
}

export async function getLeaderboard(
  category?: string,
  limit: number = 50
): Promise<LeaderboardEntry[]> {
  if (!API_BASE) {
    logApiCall('/api/leaderboard', true);
    throw new Error('API_BASE not configured. Please set NEXT_PUBLIC_API_URL in .env.local');
  }

  try {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    params.append("limit", limit.toString());

    const response = await fetchWithTimeout(`${API_BASE}/api/leaderboard?${params}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 10000, // Leaderboard should be faster
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    logApiCall('/api/leaderboard', false);
    return data;
  } catch (error) {
    console.error("Leaderboard API call failed:", error);
    logApiCall('/api/leaderboard', true, error);

    // Always throw the error so UI can show proper error state
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Leaderboard request failed');
  }
}

// Health check helper for smoke testing
export async function checkApiHealth(): Promise<{ status: string; mode: 'live' | 'mock' }> {
  if (!API_BASE) {
    return { status: 'mock_mode', mode: 'mock' };
  }

  try {
    const response = await fetchWithTimeout(`${API_BASE}/health`, {
      method: "GET",
      timeout: 5000, // Health check should be fast
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    const data = await response.json();
    return { status: data.status || 'unknown', mode: 'live' };
  } catch (error) {
    console.warn("Health check failed", error);
    return { status: 'unavailable', mode: 'mock' };
  }
}
