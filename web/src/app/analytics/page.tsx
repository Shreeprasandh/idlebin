'use client';

import React from 'react';
import FillTrajectoryChart from '@/components/FillTrajectoryChart';

export default function AnalyticsPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold tracking-tight text-zinc-100">
          Predictive Analytics & Municipal Economic Benchmark
        </h1>
        <p className="text-xs text-zinc-400">
          2nd-order polynomial fill modeling, dynamic overflow threshold prediction, and comparative CapEx/OpEx breakdown for decentralized municipal compactor grids.
        </p>
      </div>

      <FillTrajectoryChart />
    </div>
  );
}
