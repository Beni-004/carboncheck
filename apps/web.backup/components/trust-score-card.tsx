"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrustScoreRing } from "@/components/trust-score-ring";
import { VerdictBadge } from "@/components/verdict-badge";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface FraudCheck {
  name: string;
  passed: boolean;
  score: number;
  description: string;
  evidence?: string;
}

interface TrustScoreCardProps {
  creditId: string;
  trustScore: number;
  verdict: "PASS" | "WARNING" | "FAIL";
  checks: FraudCheck[];
}

export function TrustScoreCard({
  creditId,
  trustScore,
  verdict,
  checks,
}: TrustScoreCardProps) {
  return (
    <Card>
      <CardHeader className="text-center">
        <CardTitle className="mb-6">Trust Score Result</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-center">
          <TrustScoreRing score={trustScore} size="lg" />
        </div>
        
        <div className="flex flex-col items-center gap-4">
          <VerdictBadge verdict={verdict} size="lg" />
          <p className="text-sm text-muted-foreground text-center">
            Credit ID: <span className="font-mono text-foreground">{creditId}</span>
          </p>
        </div>

        <div className="border-t pt-6 mt-6">
          <h3 className="text-lg font-semibold mb-4">Check Breakdown</h3>
          <div className="space-y-3">
            {checks.map((check, index) => (
              <div
                key={index}
                className={cn(
                  "flex items-start gap-3 p-3 rounded-lg border",
                  check.passed
                    ? "bg-green-500/5 border-green-500/20"
                    : "bg-red-500/5 border-red-500/20"
                )}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {check.passed ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <p className="font-semibold text-sm">{check.name}</p>
                    <span
                      className={cn(
                        "text-xs font-bold px-2 py-1 rounded",
                        check.passed
                          ? "bg-green-500/20 text-green-300"
                          : "bg-red-500/20 text-red-300"
                      )}
                    >
                      {check.score}/25
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {check.description}
                  </p>
                  {check.evidence && (
                    <p className="text-xs text-muted-foreground/70 mt-1 italic">
                      {check.evidence}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="text-xs text-center text-muted-foreground border-t pt-4">
          <p>
            Trust Score = Sum of individual check scores (max 100)
          </p>
          <p className="mt-1">
            PASS: 71-100 · WARNING: 41-70 · FAIL: 0-40
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
