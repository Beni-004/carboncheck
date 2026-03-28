"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { VerdictBadge } from "@/components/verdict-badge";
import { TrustScoreRing } from "@/components/trust-score-ring";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Download } from "lucide-react";
import { TrustScoreResult } from "@/lib/mock";

interface BulkFraudReportTableProps {
  results: TrustScoreResult[];
}

export function BulkFraudReportTable({ results }: BulkFraudReportTableProps) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const handleExport = () => {
    const csv = [
      ["Rank", "Credit ID", "Trust Score", "Verdict", "Category", "Issuer", "Vintage", "Fraud Risks"],
      ...results.map((r, idx) => [
        idx + 1,
        r.creditId,
        r.trustScore,
        r.verdict,
        r.category,
        r.issuer,
        r.vintage,
        r.fraudRisks.length,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `carboncheck-bulk-report-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="flex justify-end mb-4">
        <Button onClick={handleExport} variant="outline" size="sm">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className="w-12">#</TableHead>
              <TableHead>Credit ID</TableHead>
              <TableHead className="text-center">Score</TableHead>
              <TableHead>Verdict</TableHead>
              <TableHead>Category</TableHead>
              <TableHead className="text-center">Risks</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {results.map((result, index) => (
              <>
                <TableRow
                  key={result.creditId}
                  className={
                    index % 2 === 0 ? "bg-background" : "bg-muted/20"
                  }
                >
                  <TableCell className="font-mono text-muted-foreground">
                    {index + 1}
                  </TableCell>
                  <TableCell className="font-mono font-semibold">
                    {result.creditId}
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="flex justify-center">
                      <TrustScoreRing score={result.trustScore} size="sm" />
                    </div>
                  </TableCell>
                  <TableCell>
                    <VerdictBadge verdict={result.verdict} size="sm" />
                  </TableCell>
                  <TableCell className="text-sm">
                    {result.category}
                  </TableCell>
                  <TableCell className="text-center">
                    <span
                      className={
                        result.fraudRisks.length > 0
                          ? "text-red-400 font-semibold"
                          : "text-green-500"
                      }
                    >
                      {result.fraudRisks.length}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setExpandedRow(
                          expandedRow === result.creditId
                            ? null
                            : result.creditId
                        )
                      }
                    >
                      {expandedRow === result.creditId ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </Button>
                  </TableCell>
                </TableRow>

                {expandedRow === result.creditId && (
                  <TableRow>
                    <TableCell colSpan={7} className="bg-muted/10 p-6">
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">
                              Issuer
                            </p>
                            <p className="text-sm font-semibold">
                              {result.issuer}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">
                              Vintage
                            </p>
                            <p className="text-sm font-semibold">
                              {result.vintage}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">
                              CO₂ Equivalent
                            </p>
                            <p className="text-sm font-semibold">
                              {result.co2Equivalent} tonnes
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">
                              Check Results
                            </p>
                            <p className="text-sm font-semibold">
                              {result.checks.filter((c) => c.passed).length}/
                              {result.checks.length} passed
                            </p>
                          </div>
                        </div>

                        {result.fraudRisks.length > 0 && (
                          <div>
                            <p className="text-sm font-semibold mb-2">
                              Fraud Risks Detected:
                            </p>
                            <div className="space-y-2">
                              {result.fraudRisks.map((risk, idx) => (
                                <div
                                  key={idx}
                                  className="p-3 bg-red-500/10 border border-red-500/20 rounded text-sm"
                                >
                                  <p className="font-semibold text-red-300">
                                    {risk.category} ({risk.severity})
                                  </p>
                                  <p className="text-muted-foreground text-xs mt-1">
                                    {risk.description}
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {result.fraudRisks.length === 0 && (
                          <div className="p-3 bg-green-500/10 border border-green-500/20 rounded text-sm">
                            <p className="text-green-300">
                              ✓ No fraud risks detected
                            </p>
                          </div>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
