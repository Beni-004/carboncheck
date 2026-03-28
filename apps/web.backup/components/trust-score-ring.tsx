"use client";

import { cn } from "@/lib/utils";

interface TrustScoreRingProps {
  score: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function TrustScoreRing({
  score,
  size = "lg",
  className,
}: TrustScoreRingProps) {
  const getColor = (score: number) => {
    if (score >= 71) return "text-green-500";
    if (score >= 41) return "text-amber-500";
    return "text-red-500";
  };

  const sizeMap = {
    sm: { ring: 80, radius: 35, strokeWidth: 4, fontSize: "text-2xl" },
    md: { ring: 120, radius: 52.5, strokeWidth: 5, fontSize: "text-4xl" },
    lg: { ring: 180, radius: 79, strokeWidth: 6, fontSize: "text-6xl" },
  };

  const config = sizeMap[size];
  const circumference = 2 * Math.PI * config.radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <div className="relative inline-flex items-center justify-center">
        <svg
          width={config.ring}
          height={config.ring}
          className="transform -rotate-90"
        >
          <circle
            cx={config.ring / 2}
            cy={config.ring / 2}
            r={config.radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            className="text-muted/30"
          />
          <circle
            cx={config.ring / 2}
            cy={config.ring / 2}
            r={config.radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={config.strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={cn(
              "transition-all duration-500 ease-out",
              getColor(score)
            )}
          />
        </svg>

        <div className="absolute flex flex-col items-center">
          <span className={cn("font-bold leading-none", config.fontSize)}>
            {score}
          </span>
          <span className="text-xs text-muted-foreground mt-1">Score</span>
        </div>
      </div>
    </div>
  );
}
