import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface VerdictBadgeProps {
  verdict: "PASS" | "WARNING" | "FAIL";
  size?: "sm" | "md" | "lg";
}

export function VerdictBadge({ verdict, size = "md" }: VerdictBadgeProps) {
  const variantMap = {
    PASS: "bg-green-500/20 text-green-300 border-green-500/30",
    WARNING: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    FAIL: "bg-red-500/20 text-red-300 border-red-500/30",
  };

  const sizeMap = {
    sm: "text-xs px-2 py-1",
    md: "text-sm px-3 py-1.5",
    lg: "text-base px-4 py-2",
  };

  return (
    <Badge
      className={cn(
        "font-bold tracking-widest border",
        variantMap[verdict],
        sizeMap[size]
      )}
    >
      {verdict}
    </Badge>
  );
}
