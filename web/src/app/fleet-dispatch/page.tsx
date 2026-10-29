'use client';

import React from 'react';
import MunicipalFleetMap from '@/components/MunicipalFleetMap';

export default function FleetDispatchPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold tracking-tight text-zinc-100">
          Municipal Fleet Surveillance & Smart Dispatch
        </h1>
        <p className="text-xs text-zinc-400">
          Real-time GIS surveillance grid across Greater Chennai Corporation (GCC) Zone 11. Automated Haversine TSP routing for collection vehicles.
        </p>
      </div>

      <MunicipalFleetMap />
    </div>
  );
}
