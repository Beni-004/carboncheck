"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { BulkFraudReportTable } from "@/components/bulk-fraud-report-table";
import { verifyBulkCredits } from "@/lib/api";
import { BulkVerifyResult } from "@/lib/mock";
import { Loader2, ArrowLeft, Upload, AlertCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function BulkVerifyPage() {
  const [creditIds, setCreditIds] = useState("");
  const [result, setResult] = useState<BulkVerifyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const ids = creditIds
      .split("\n")
      .map((id) => id.trim())
      .filter((id) => id.length > 0);

    if (ids.length === 0) {
      setError("Please enter at least one credit ID");
      return;
    }

    if (ids.length > 50) {
      setError("Maximum 50 credit IDs allowed per batch");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await verifyBulkCredits(ids);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to verify credits"
      );
    } finally {
      setLoading(false);
    }
  };

  const currentCount = creditIds
    .split("\n")
    .filter((id) => id.trim().length > 0).length;

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
          <h1 className="text-4xl font-bold mb-2">Bulk Credit Verification</h1>
          <p className="text-muted-foreground">
            Submit up to 50 credit IDs and receive a ranked fraud report
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Enter Credit IDs</CardTitle>
              <CardDescription>
                One credit ID per line (max 50). Results will be ranked by risk.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Textarea
                    placeholder="VCS-2024-001&#10;GOLD-2023-556&#10;ACR-2021-999&#10;..."
                    value={creditIds}
                    onChange={(e) => setCreditIds(e.target.value)}
                    disabled={loading}
                    rows={10}
                    className="font-mono text-sm"
                  />
                  <div className="flex items-center justify-between mt-2">
                    <p className="text-xs text-muted-foreground">
                      {currentCount} / 50 credits
                    </p>
                    {currentCount > 50 && (
                      <p className="text-xs text-red-400 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        Maximum 50 credits exceeded
                      </p>
                    )}
                  </div>
                </div>
                {error && <p className="text-sm text-red-400">{error}</p>}
                <Button
                  type="submit"
                  disabled={loading || currentCount === 0 || currentCount > 50}
                  className="w-full"
                  size="lg"
                >
                  {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {loading ? (
                    <>Processing {currentCount} credits...</>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Verify {currentCount} Credit{currentCount !== 1 ? "s" : ""}
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {result && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <Card>
                <CardHeader>
                  <CardTitle>Bulk Verification Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Submitted
                      </p>
                      <p className="text-2xl font-bold">
                        {result.totalSubmitted}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Processed
                      </p>
                      <p className="text-2xl font-bold text-green-500">
                        {result.totalProcessed}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        Errors
                      </p>
                      <p className="text-2xl font-bold text-red-500">
                        {result.totalErrors}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                        High Risk
                      </p>
                      <p className="text-2xl font-bold text-amber-500">
                        {
                          result.results.filter((r) => r.verdict === "FAIL")
                            .length
                        }
                      </p>
                    </div>
                  </div>

                  {result.errors && result.errors.length > 0 && (
                    <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                      <p className="text-sm font-semibold text-red-300 mb-2">
                        Processing Errors:
                      </p>
                      <div className="space-y-1">
                        {result.errors.map((err, idx) => (
                          <p key={idx} className="text-xs text-red-200/70">
                            <span className="font-mono">{err.creditId}</span>:{" "}
                            {err.error}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Ranked Fraud Report</CardTitle>
                    <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                      Sorted by Risk (Worst First)
                    </Badge>
                  </div>
                  <CardDescription>
                    Credits ranked by trust score - lowest scores indicate highest fraud risk
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <BulkFraudReportTable results={result.results} />
                </CardContent>
              </Card>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={() => {
                    setCreditIds("");
                    setResult(null);
                  }}
                  variant="outline"
                  className="flex-1"
                  size="lg"
                >
                  Verify Another Batch
                </Button>
                <Link href="/verify" className="flex-1">
                  <Button variant="outline" className="w-full" size="lg">
                    Single Verify
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {!result && !loading && (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-6">
                Paste credit IDs above (one per line) and click verify to get started
              </p>
              <div className="text-xs text-muted-foreground space-y-2">
                <p>
                  Try these examples (copy and paste into the box above):
                </p>
                <code className="block font-mono text-foreground/70 bg-muted p-4 rounded-lg text-left max-w-md mx-auto">
                  VCS-2024-001
                  <br />
                  GOLD-2023-556
                  <br />
                  ACR-2021-999
                </code>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
