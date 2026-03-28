"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { getLeaderboard } from "@/lib/api";
import { LeaderboardEntry } from "@/lib/mock";
import { Loader2, ArrowLeft, TrendingDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function LeaderboardPage() {
  const [category, setCategory] = useState<string>("all");
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  const categories = [
    { value: "all", label: "All Categories" },
    { value: "Renewable Energy", label: "Renewable Energy" },
    { value: "Forestry", label: "Forestry" },
    { value: "Landfill Gas", label: "Landfill Gas" },
    { value: "Methane", label: "Methane" },
    { value: "Soil Carbon", label: "Soil Carbon" },
  ];

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true);
      try {
        const data = await getLeaderboard(
          category === "all" ? undefined : category,
          50
        );
        setEntries(data);
      } catch (error) {
        console.error("Failed to fetch leaderboard:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, [category]);

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
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
                Fraud Leaderboard
                <TrendingDown className="w-8 h-8 text-red-500" />
              </h1>
              <p className="text-muted-foreground">
                Most-flagged carbon credits ranked by fraud risk
              </p>
            </div>
            <Badge className="bg-green-500/20 text-green-300 border-green-500/30 text-sm">
              Public · No Login Required
            </Badge>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Hall of Shame</CardTitle>
            <CardDescription>
              Credits with the highest number of fraud flags across all verifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={category} onValueChange={setCategory}>
              <TabsList className="grid w-full grid-cols-3 lg:grid-cols-6 mb-6">
                {categories.map((cat) => (
                  <TabsTrigger key={cat.value} value={cat.value}>
                    {cat.label}
                  </TabsTrigger>
                ))}
              </TabsList>

              {categories.map((cat) => (
                <TabsContent key={cat.value} value={cat.value}>
                  {loading ? (
                    <div className="flex items-center justify-center py-12">
                      <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : (
                    <LeaderboardTable entries={entries} category={cat.label} />
                  )}
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>

        <div className="mt-8 text-center">
          <p className="text-sm text-muted-foreground mb-4">
            Data refreshed every 5 minutes · Last update:{" "}
            {new Date().toLocaleTimeString()}
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/verify">
              <button className="text-sm text-blue-400 hover:text-blue-300 underline">
                Verify Your Credits →
              </button>
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
