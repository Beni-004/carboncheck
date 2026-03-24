import { getMockResult, TrustScoreResult } from "./mock";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "";

export async function verifyCreditId(
  creditId: string
): Promise<TrustScoreResult> {
  if (!API_BASE) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(getMockResult(creditId)), 1500);
    });
  }

  try {
    const response = await fetch(`${API_BASE}/verify/single`, {
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
