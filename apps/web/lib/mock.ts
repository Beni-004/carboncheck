export interface FraudCheck {
  name: string;
  passed: boolean;
  score: number;
  description: string;
  evidence?: string;
}

export interface TrustScoreResult {
  creditId: string;
  trustScore: number;
  verdict: "PASS" | "WARNING" | "FAIL";
  category: string;
  issuer: string;
  vintage: number;
  co2Equivalent: number;
  checks: FraudCheck[];
  fraudRisks: Array<{
    category: string;
    severity: "high" | "medium" | "low";
    description: string;
    evidence?: string;
  }>;
  verifiedAt: string;
  dataMode?: "live" | "fallback";
  fallbackUsed?: boolean;
  dataFreshness?: string;
}

export interface BulkVerifyResult {
  results: TrustScoreResult[];
  totalSubmitted: number;
  totalProcessed: number;
  totalErrors: number;
  errors?: Array<{
    creditId: string;
    error: string;
  }>;
}

export interface LeaderboardEntry {
  creditId: string;
  trustScore: number;
  verdict: "PASS" | "WARNING" | "FAIL";
  category: string;
  issuer: string;
  flagCount: number;
  lastVerified: string;
}

export function getMockResult(creditId: string): TrustScoreResult {
  const mockData: Record<string, TrustScoreResult> = {
    "VCS-2024-001": {
      creditId: "VCS-2024-001",
      trustScore: 92,
      verdict: "PASS",
      category: "Renewable Energy",
      issuer: "Verified Carbon Standard",
      vintage: 2023,
      co2Equivalent: 1000,
      checks: [
        {
          name: "Baseline Match",
          passed: true,
          score: 25,
          description: "Project baseline aligns with registry records",
          evidence: "Verified against VCS registry database",
        },
        {
          name: "Additionality",
          passed: true,
          score: 25,
          description: "Project would not have occurred without carbon finance",
          evidence: "Financial additionality demonstrated in project documentation",
        },
        {
          name: "Permanence Risk",
          passed: true,
          score: 22,
          description: "Low risk of emission reversals",
          evidence: "Buffer pool allocation meets VCS requirements",
        },
        {
          name: "Double Counting",
          passed: true,
          score: 20,
          description: "No evidence of duplicate claims across registries",
          evidence: "Cross-registry check completed successfully",
        },
      ],
      fraudRisks: [],
      verifiedAt: new Date().toISOString(),
      dataMode: "live",
      fallbackUsed: false,
      dataFreshness: "Real-time",
    },
    "GOLD-2023-556": {
      creditId: "GOLD-2023-556",
      trustScore: 58,
      verdict: "WARNING",
      category: "Forestry",
      issuer: "Gold Standard",
      vintage: 2022,
      co2Equivalent: 500,
      checks: [
        {
          name: "Baseline Match",
          passed: true,
          score: 25,
          description: "Project baseline aligns with registry records",
        },
        {
          name: "Additionality",
          passed: false,
          score: 8,
          description: "Weak evidence that project required carbon finance",
          evidence: "Baseline comparison suggests project may have occurred anyway",
        },
        {
          name: "Permanence Risk",
          passed: true,
          score: 20,
          description: "Moderate risk due to forestry project type",
        },
        {
          name: "Double Counting",
          passed: false,
          score: 5,
          description: "Credit appears in multiple registries",
          evidence: "Registry cross-check flagged duplicate entries",
        },
      ],
      fraudRisks: [
        {
          category: "Double Counting",
          severity: "medium",
          description:
            "Credit appears in multiple registries simultaneously",
          evidence: "Registry cross-check flagged duplicate entries",
        },
        {
          category: "Additionality",
          severity: "low",
          description: "Project may have occurred anyway without incentive",
          evidence: "Baseline comparison suggests weak additionality case",
        },
      ],
      verifiedAt: new Date().toISOString(),
      dataMode: "live",
      fallbackUsed: false,
      dataFreshness: "Real-time",
    },
    "ACR-2021-999": {
      creditId: "ACR-2021-999",
      trustScore: 15,
      verdict: "FAIL",
      category: "Landfill Gas",
      issuer: "American Carbon Registry",
      vintage: 2019,
      co2Equivalent: 2000,
      checks: [
        {
          name: "Baseline Match",
          passed: false,
          score: 5,
          description: "Project data conflicts with registry records",
          evidence: "Significant discrepancies in reported emissions reductions",
        },
        {
          name: "Additionality",
          passed: false,
          score: 3,
          description: "Project lacks financial additionality proof",
          evidence: "No evidence project required carbon finance to proceed",
        },
        {
          name: "Permanence Risk",
          passed: false,
          score: 2,
          description: "High risk of emission reversals",
        },
        {
          name: "Double Counting",
          passed: false,
          score: 5,
          description: "Credit already retired in another registry",
          evidence: "Found in retirement database with date 2022-03-15",
        },
      ],
      fraudRisks: [
        {
          category: "Retirement Status",
          severity: "high",
          description: "Credit has already been retired and cannot be sold",
          evidence: "Found in retirement database with retirement date 2022-03-15",
        },
        {
          category: "Registry Suspension",
          severity: "high",
          description: "Issuer temporarily suspended from issuing new credits",
          evidence: "ACR announced moratorium on new credit issuance",
        },
      ],
      verifiedAt: new Date().toISOString(),
      dataMode: "fallback",
      fallbackUsed: true,
      dataFreshness: "Cached (2 hours old)",
    },
  };

  if (mockData[creditId]) {
    return mockData[creditId];
  }

  const randomScore = Math.floor(Math.random() * 100);
  const verdict: "PASS" | "WARNING" | "FAIL" =
    randomScore > 70 ? "PASS" : randomScore > 40 ? "WARNING" : "FAIL";

  const baselineScore = Math.floor(Math.random() * 25) + 1;
  const additionalityScore = Math.floor(Math.random() * 25) + 1;
  const permanenceScore = Math.floor(Math.random() * 25) + 1;
  const doubleCountScore = Math.floor(Math.random() * 25) + 1;

  return {
    creditId,
    trustScore: randomScore,
    verdict,
    category: ["Renewable Energy", "Forestry", "Landfill Gas", "Methane"][
      Math.floor(Math.random() * 4)
    ],
    issuer: [
      "Verified Carbon Standard",
      "Gold Standard",
      "American Carbon Registry",
    ][Math.floor(Math.random() * 3)],
    vintage: 2020 + Math.floor(Math.random() * 4),
    co2Equivalent: Math.floor(Math.random() * 2000) + 100,
    checks: [
      {
        name: "Baseline Match",
        passed: baselineScore > 15,
        score: baselineScore,
        description: baselineScore > 15 
          ? "Project baseline aligns with registry records"
          : "Project data conflicts with registry records",
      },
      {
        name: "Additionality",
        passed: additionalityScore > 15,
        score: additionalityScore,
        description: additionalityScore > 15
          ? "Project would not have occurred without carbon finance"
          : "Weak evidence that project required carbon finance",
      },
      {
        name: "Permanence Risk",
        passed: permanenceScore > 15,
        score: permanenceScore,
        description: permanenceScore > 15
          ? "Low risk of emission reversals"
          : "High risk of emission reversals",
      },
      {
        name: "Double Counting",
        passed: doubleCountScore > 15,
        score: doubleCountScore,
        description: doubleCountScore > 15
          ? "No evidence of duplicate claims"
          : "Credit appears in multiple registries",
      },
    ],
    fraudRisks:
      randomScore > 70
        ? []
        : [
            {
              category: "Sample Risk",
              severity: "medium",
              description: "Generic fraud indicator for demo purposes",
            },
          ],
    verifiedAt: new Date().toISOString(),
    dataMode: "live",
    fallbackUsed: false,
    dataFreshness: "Real-time",
  };
}

export function getMockBulkResults(creditIds: string[]): BulkVerifyResult {
  const results: TrustScoreResult[] = [];
  const errors: Array<{ creditId: string; error: string }> = [];

  creditIds.forEach((id, index) => {
    // Simulate 5% error rate for demo
    if (Math.random() < 0.05) {
      errors.push({
        creditId: id,
        error: "Invalid credit ID format or not found in registry",
      });
    } else {
      results.push(getMockResult(id));
    }
  });

  // Sort by trust score ascending (worst first)
  results.sort((a, b) => a.trustScore - b.trustScore);

  return {
    results,
    totalSubmitted: creditIds.length,
    totalProcessed: results.length,
    totalErrors: errors.length,
    errors: errors.length > 0 ? errors : undefined,
  };
}

export function getMockLeaderboard(
  category?: string,
  limit: number = 50
): LeaderboardEntry[] {
  const categories = ["Renewable Energy", "Forestry", "Landfill Gas", "Methane", "Soil Carbon"];
  const issuers = ["Verified Carbon Standard", "Gold Standard", "American Carbon Registry", "Climate Action Reserve"];

  const entries: LeaderboardEntry[] = Array.from({ length: 100 }, (_, i) => {
    const score = Math.floor(Math.random() * 100);
    const cat = categories[Math.floor(Math.random() * categories.length)];
    
    return {
      creditId: `${cat.substring(0, 3).toUpperCase()}-${2020 + Math.floor(i / 20)}-${String(i + 1).padStart(3, '0')}`,
      trustScore: score,
      verdict: score > 70 ? "PASS" : score > 40 ? "WARNING" : "FAIL",
      category: cat,
      issuer: issuers[Math.floor(Math.random() * issuers.length)],
      flagCount: Math.floor((100 - score) / 10) + Math.floor(Math.random() * 5),
      lastVerified: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
    };
  });

  let filtered = entries;
  if (category) {
    filtered = entries.filter(e => e.category === category);
  }

  // Sort by flag count descending (most flagged first)
  filtered.sort((a, b) => b.flagCount - a.flagCount);

  return filtered.slice(0, limit);
}
