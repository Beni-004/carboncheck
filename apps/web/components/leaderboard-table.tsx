"use client";

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
import { LeaderboardEntry } from "@/lib/mock";
import { AlertTriangle } from "lucide-react";

interface LeaderboardTableProps {
  entries: LeaderboardEntry[];
  category: string;
}

export function LeaderboardTable({ entries, category }: LeaderboardTableProps) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No entries found for {category}</p>
      </div>
    );
  }

  const timeAgo = (date: string) => {
    const seconds = Math.floor(
      (new Date().getTime() - new Date(date).getTime()) / 1000
    );
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50">
            <TableHead className="w-12">#</TableHead>
            <TableHead>Credit ID</TableHead>
            <TableHead className="text-center">Score</TableHead>
            <TableHead>Verdict</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Issuer</TableHead>
            <TableHead className="text-center">
              <div className="flex items-center justify-center gap-1">
                <AlertTriangle className="w-4 h-4" />
                Flags
              </div>
            </TableHead>
            <TableHead className="text-right">Last Verified</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {entries.map((entry, index) => (
            <TableRow
              key={entry.creditId}
              className={
                index % 2 === 0 ? "bg-background" : "bg-muted/20"
              }
            >
              <TableCell className="font-mono text-muted-foreground">
                {index + 1}
              </TableCell>
              <TableCell className="font-mono font-semibold">
                {entry.creditId}
              </TableCell>
              <TableCell className="text-center">
                <div className="flex justify-center">
                  <TrustScoreRing score={entry.trustScore} size="sm" />
                </div>
              </TableCell>
              <TableCell>
                <VerdictBadge verdict={entry.verdict} size="sm" />
              </TableCell>
              <TableCell className="text-sm">
                {entry.category}
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {entry.issuer}
              </TableCell>
              <TableCell className="text-center">
                <span
                  className={
                    entry.flagCount > 5
                      ? "text-red-400 font-bold text-lg"
                      : entry.flagCount > 2
                        ? "text-amber-400 font-semibold"
                        : "text-green-500"
                  }
                >
                  {entry.flagCount}
                </span>
              </TableCell>
              <TableCell className="text-right text-xs text-muted-foreground">
                {timeAgo(entry.lastVerified)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
