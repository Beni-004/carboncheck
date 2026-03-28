"use client";

import { Badge } from "@/components/ui/badge";
import { Database, Clock, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProvenanceBadgesProps {
  dataMode?: "live" | "fallback";
  fallbackUsed?: boolean;
  dataFreshness?: string;
  verifiedAt: string;
}

export function ProvenanceBadges({
  dataMode = "live",
  fallbackUsed = false,
  dataFreshness = "Real-time",
  verifiedAt,
}: ProvenanceBadgesProps) {
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
    <div className="flex flex-wrap gap-2 items-center">
      <Badge
        className={cn(
          "flex items-center gap-1.5",
          fallbackUsed
            ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
            : "bg-green-500/20 text-green-300 border-green-500/30"
        )}
      >
        <Database className="w-3 h-3" />
        {dataMode === "live" ? "Live Data" : "Cached Data"}
      </Badge>

      <Badge className="flex items-center gap-1.5 bg-blue-500/20 text-blue-300 border-blue-500/30">
        <Clock className="w-3 h-3" />
        {dataFreshness}
      </Badge>

      {fallbackUsed && (
        <Badge className="flex items-center gap-1.5 bg-amber-500/20 text-amber-300 border-amber-500/30">
          <AlertTriangle className="w-3 h-3" />
          Fallback Mode
        </Badge>
      )}

      <span className="text-xs text-muted-foreground ml-2">
        Verified {timeAgo(verifiedAt)}
      </span>
    </div>
  );
}
