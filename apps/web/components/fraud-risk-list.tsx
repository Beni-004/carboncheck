import { AlertCircle, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface FraudRisk {
  category: string;
  severity: "high" | "medium" | "low";
  description: string;
  evidence?: string;
}

interface FraudRiskListProps {
  risks: FraudRisk[];
}

export function FraudRiskList({ risks }: FraudRiskListProps) {
  if (risks.length === 0) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-lg bg-green-500/10 border border-green-500/30">
        <div className="text-green-500">✓</div>
        <div>
          <p className="font-semibold text-green-300">No fraud risks detected</p>
          <p className="text-sm text-green-200/70">This credit passed all checks</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-foreground">Detected Issues:</h3>
      {risks.map((risk, idx) => (
        <div
          key={idx}
          className={cn(
            "p-4 rounded-lg border",
            risk.severity === "high"
              ? "bg-red-500/10 border-red-500/30"
              : risk.severity === "medium"
                ? "bg-amber-500/10 border-amber-500/30"
                : "bg-blue-500/10 border-blue-500/30"
          )}
        >
          <div className="flex items-start gap-3">
            {risk.severity === "high" ? (
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            ) : risk.severity === "medium" ? (
              <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            ) : (
              <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm">{risk.category}</p>
              <p className="text-sm text-muted-foreground mt-1">
                {risk.description}
              </p>
              {risk.evidence && (
                <p className="text-xs text-muted-foreground/70 mt-2 italic">
                  Evidence: {risk.evidence}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
