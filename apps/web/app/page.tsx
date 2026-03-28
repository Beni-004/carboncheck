'use client';

import { useEffect } from 'react';

export default function Home() {
  useEffect(() => {
    // Redirect to the beautiful landing page
    window.location.href = '/carbon2.html';
  }, []);

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-secondary/20">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">CarbonChain Verifier</h1>
        <p className="text-lg text-muted-foreground mb-8">Loading verification interface...</p>
        <a href="/carbon2.html" className="text-green-500 hover:text-green-400 underline">Click here if not redirected</a>
      </div>
    </main>
  );
}
