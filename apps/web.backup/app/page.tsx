import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Shield, FileSearch, TrendingUp } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-green-400 to-emerald-600 bg-clip-text text-transparent">
            CarbonCheck
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Trust Score for Carbon Credits. Detect fraud before you buy.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/verify">
              <Button size="lg" className="text-lg px-8">
                Verify Credits
              </Button>
            </Link>
            <Link href="/leaderboard">
              <Button size="lg" variant="outline" className="text-lg px-8">
                View Leaderboard
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <Card className="border-green-500/20">
            <CardHeader>
              <Shield className="w-12 h-12 mb-4 text-green-500" />
              <CardTitle>Stop Bad Purchases</CardTitle>
              <CardDescription>
                Paste one credit ID and get instant fraud detection in under 5 seconds
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/verify">
                <Button variant="ghost" className="w-full">
                  Try Single Verify →
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="border-amber-500/20">
            <CardHeader>
              <FileSearch className="w-12 h-12 mb-4 text-amber-500" />
              <CardTitle>Audit at Scale</CardTitle>
              <CardDescription>
                Submit up to 50 credits and receive ranked fraud report with evidence
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/verify/bulk">
                <Button variant="ghost" className="w-full">
                  Try Bulk Audit →
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="border-blue-500/20">
            <CardHeader>
              <TrendingUp className="w-12 h-12 mb-4 text-blue-500" />
              <CardTitle>Public Leaderboard</CardTitle>
              <CardDescription>
                See the most-flagged credits by category in near real-time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/leaderboard">
                <Button variant="ghost" className="w-full">
                  View Rankings →
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
