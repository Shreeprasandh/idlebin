'use client';

import React from 'react';
import CitizenPortal from '@/components/CitizenPortal';

export default function CitizenPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold tracking-tight text-zinc-100">
          Citizen Reverse Vending & SWM 2016 Grievances
        </h1>
        <p className="text-xs text-zinc-400">
          Deposit plastic bottles for instant UPI cash-back or report municipal solid waste infractions with photographic evidence to GCC Zone 11 Conservancy.
        </p>
      </div>

      <CitizenPortal />
    </div>
  );
}
