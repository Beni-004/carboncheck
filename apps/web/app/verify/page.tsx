"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { TrustScoreCard } from "@/components/trust-score-card";
import { FraudRiskList } from "@/components/fraud-risk-list";
import { ProvenanceBadges } from "@/components/provenance-badges";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { verifyCreditId } from "@/lib/api";
import { TrustScoreResult } from "@/lib/mock";
import { Loader2, ArrowLeft, AlertCircle } from "lucide-react";

export default function VerifyPage() {
  const [creditId, setCreditId] = useState("");
  const [result, setResult] = useState<TrustScoreResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verificationProgress, setVerificationProgress] = useState<string>("");
  const [elapsedTime, setElapsedTime] = useState<number>(0);

  // Progress indicator for long-running verification
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    let startTime: number | null = null;

    if (loading) {
      startTime = Date.now();
      const progressMessages = [
        "Connecting to verification engine...",
        "Analyzing ground-layer registry data...",
        "Processing satellite imagery signals...",
        "Running AI fraud detection models...",
        "Computing trust score...",
        "Finalizing verification report...",
      ];

      let messageIndex = 0;
      setVerificationProgress(progressMessages[0]);

      intervalId = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime!) / 1000);
        setElapsedTime(elapsed);

        // Update progress message every 3 seconds
        if (elapsed > 0 && elapsed % 3 === 0) {
          messageIndex = Math.min(messageIndex + 1, progressMessages.length - 1);
          setVerificationProgress(progressMessages[messageIndex]);
        }
      }, 1000);
    } else {
      setVerificationProgress("");
      setElapsedTime(0);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!creditId.trim()) {
      setError("Please enter a credit ID");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setElapsedTime(0);

    try {
      const data = await verifyCreditId(creditId.trim());
      setResult(data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to verify credit ID";
      setError(errorMessage);
      
      // Log error for debugging
      console.error("Verification error:", err);
    } finally {
      setLoading(false);
      setVerificationProgress("");
      setElapsedTime(0);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-secondary/10">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to home
          </Link>
          <h1 className="text-4xl font-bold mb-2">Verify Single Credit</h1>
          <p className="text-muted-foreground">
            Paste a carbon credit ID below to instantly check its authenticity
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Enter Credit ID</CardTitle>
              <CardDescription>
                Format: e.g., VCS-2024-001 or GOLD-2023-556
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Input
                    placeholder="VCS-2024-001"
                    value={creditId}
                    onChange={(e) => setCreditId(e.target.value)}
                    disabled={loading}
                    autoFocus
                    className="text-base"
                  />
                </div>
                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Verification Failed</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                {loading && verificationProgress && (
                  <Alert>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <AlertTitle>Deep Analysis in Progress</AlertTitle>
                    <AlertDescription>
                      {verificationProgress}
                      <br />
                      <span className="text-xs text-muted-foreground">
                        Elapsed: {elapsedTime}s (AI and satellite analysis may take 10-20s)
                      </span>
                    </AlertDescription>
                  </Alert>
                )}
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full"
                  size="lg"
                >
                  {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {loading ? "Verifying..." : "Verify Credit"}
                </Button>
              </form>
            </CardContent>
          </Card>

          {result && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <TrustScoreCard
                creditId={result.creditId}
                trustScore={result.trustScore}
                verdict={result.verdict}
                checks={result.checks}
              />

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Credit Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Category
                      </p>
                      <p className="font-semibold">{result.category}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Issuer
                      </p>
                      <p className="font-semibold">{result.issuer}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Vintage Year
                      </p>
                      <p className="font-semibold">{result.vintage}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        CO₂ Equivalent
                      </p>
                      <p className="font-semibold">
                        {result.co2Equivalent} tonnes
                      </p>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <p className="text-xs text-muted-foreground uppercase tracking-wide mb-2">
                      Data Provenance
                    </p>
                    <ProvenanceBadges
                      dataMode={result.dataMode}
                      fallbackUsed={result.fallbackUsed}
                      dataFreshness={result.dataFreshness}
                      verifiedAt={result.verifiedAt}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Fraud Assessment</CardTitle>
                </CardHeader>
                <CardContent>
                  <FraudRiskList risks={result.fraudRisks} />
                </CardContent>
              </Card>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={() => {
                    setCreditId("");
                    setResult(null);
                  }}
                  variant="outline"
                  className="flex-1"
                  size="lg"
                >
                  Verify Another
                </Button>
                <Link href="/verify/bulk" className="flex-1">
                  <Button className="w-full" size="lg">
                    Verify Multiple Credits →
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {!result && !loading && (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-6">
                Enter a credit ID above and click "Verify Credit" to get started
              </p>
              <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
                <div>
                  <p className="mb-2">Try these examples:</p>
                  <code className="block font-mono text-foreground/70">
                    VCS-2024-001
                  </code>
                </div>
                <div>
                  <p className="mb-2"></p>
                  <code className="block font-mono text-foreground/70">
                    GOLD-2023-556
                  </code>
                </div>
                <div>
                  <p className="mb-2"></p>
                  <code className="block font-mono text-foreground/70">
                    ACR-2021-999
                  </code>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
