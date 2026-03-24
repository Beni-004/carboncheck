export interface TrustScoreResult {
  creditId: string;
  trustScore: number;
  verdict: "PASS" | "WARNING" | "FAIL";
  category: string;
  issuer: string;
  vintage: number;
  co2Equivalent: number;
  fraudRisks: Array<{
    category: string;
    severity: "high" | "medium" | "low";
    description: string;
    evidence?: string;
  }>;
  verifiedAt: string;
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
      fraudRisks: [],
      verifiedAt: new Date().toISOString(),
    },
    "GOLD-2023-556": {
      creditId: "GOLD-2023-556",
      trustScore: 58,
      verdict: "WARNING",
      category: "Forestry",
      issuer: "Gold Standard",
      vintage: 2022,
      co2Equivalent: 500,
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
    },
    "ACR-2021-999": {
      creditId: "ACR-2021-999",
      trustScore: 15,
      verdict: "FAIL",
      category: "Landfill Gas",
      issuer: "American Carbon Registry",
      vintage: 2019,
      co2Equivalent: 2000,
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
    },
  };

  if (mockData[creditId]) {
    return mockData[creditId];
  }

  const randomScore = Math.floor(Math.random() * 100);
  const verdict: "PASS" | "WARNING" | "FAIL" =
    randomScore > 70 ? "PASS" : randomScore > 40 ? "WARNING" : "FAIL";

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
  };
}
