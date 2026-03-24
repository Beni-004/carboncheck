import { getMockResult, getMockBulkResults, getMockLeaderboard, TrustScoreResult, BulkVerifyResult, LeaderboardEntry } from "./mock";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export async function verifyCreditId(
  creditId: string
): Promise<TrustScoreResult> {
  if (!API_BASE) {
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
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.warn("API call failed, falling back to mock data", error);
    return getMockResult(creditId);
  }
}

export async function verifyBulkCredits(
  creditIds: string[]
): Promise<BulkVerifyResult> {
  if (!API_BASE) {
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
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.warn("API call failed, falling back to mock data", error);
    return getMockBulkResults(creditIds);
  }
}

export async function getLeaderboard(
  category?: string,
  limit: number = 50
): Promise<LeaderboardEntry[]> {
  if (!API_BASE) {
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
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.warn("API call failed, falling back to mock data", error);
    return getMockLeaderboard(category, limit);
  }
}
