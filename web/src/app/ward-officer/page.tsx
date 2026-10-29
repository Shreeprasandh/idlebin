'use client';

import React from 'react';
import WardOfficerPortal from '@/components/WardOfficerPortal';

export default function WardOfficerPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold tracking-tight text-zinc-100">
          Conservancy Ward Officer Grievance & Challan Portal
        </h1>
        <p className="text-xs text-zinc-400">
          Greater Chennai Corporation (GCC) Zone 11 Valasaravakkam Conservancy administrative docket. Review citizen reports, inspect evidentiary photos, and levy statutory e-challans.
        </p>
      </div>

      <WardOfficerPortal />
    </div>
  );
}
