import { getMockResult, getMockBulkResults, getMockLeaderboard, TrustScoreResult, BulkVerifyResult, LeaderboardEntry } from "./mock";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

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
    return new Promise((resolve) => {
      setTimeout(() => resolve(getMockResult(creditId)), 1500);
    });
  }

  try {
    const response = await fetch(`${API_BASE}/api/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ creditId }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    logApiCall('/api/verify', false);
    return data;
  } catch (error) {
    console.warn("API call failed, falling back to mock data", error);
    logApiCall('/api/verify', true, error);
    return getMockResult(creditId);
  }
}

export async function verifyBulkCredits(
  creditIds: string[]
): Promise<BulkVerifyResult> {
  if (!API_BASE) {
    logApiCall('/api/verify/bulk', true);
    return new Promise((resolve) => {
      setTimeout(() => resolve(getMockBulkResults(creditIds)), 2500);
    });
  }

  try {
    const response = await fetch(`${API_BASE}/api/verify/bulk`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ creditIds }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    logApiCall('/api/verify/bulk', false);
    return data;
  } catch (error) {
    console.warn("API call failed, falling back to mock data", error);
    logApiCall('/api/verify/bulk', true, error);
    return getMockBulkResults(creditIds);
  }
}

export async function getLeaderboard(
  category?: string,
  limit: number = 50
): Promise<LeaderboardEntry[]> {
  if (!API_BASE) {
    logApiCall('/api/leaderboard', true);
    return new Promise((resolve) => {
      setTimeout(() => resolve(getMockLeaderboard(category, limit)), 800);
    });
  }

  try {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    params.append("limit", limit.toString());

    const response = await fetch(`${API_BASE}/api/leaderboard?${params}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    logApiCall('/api/leaderboard', false);
    return data;
  } catch (error) {
    console.warn("API call failed, falling back to mock data", error);
    logApiCall('/api/leaderboard', true, error);
    return getMockLeaderboard(category, limit);
  }
}

// Health check helper for smoke testing
export async function checkApiHealth(): Promise<{ status: string; mode: 'live' | 'mock' }> {
  if (!API_BASE) {
    return { status: 'mock_mode', mode: 'mock' };
  }

  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: "GET",
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
