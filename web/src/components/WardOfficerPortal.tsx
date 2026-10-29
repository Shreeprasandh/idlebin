'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { ViolationReport } from '@/types/idlebin';
import { getViolations, updateViolationStatus } from '@/lib/data-service';
import { ShieldCheck, FileText, CheckCircle, XCircle, AlertCircle, Eye, Stamp } from 'lucide-react';

export default function WardOfficerPortal() {
  const [violations, setViolations] = useState<ViolationReport[]>([]);
  const [selectedViolation, setSelectedViolation] = useState<ViolationReport | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    getViolations().then((data) => {
      setViolations(data);
      if (data.length > 0) setSelectedViolation(data[0]);
    });
  }, []);

  const handleIssueChallan = async (v: ViolationReport) => {
    setIsProcessing(true);
    const challanId = `CHN-Z11-CH-${Math.floor(10000 + Math.random() * 90000)}`;
    await updateViolationStatus(v.id, 'CONFIRMED_FINE_ISSUED', challanId);

    setViolations((prev) =>
      prev.map((item) =>
        item.id === v.id
          ? { ...item, status: 'CONFIRMED_FINE_ISSUED', challanId, reviewedAt: new Date().toISOString() }
          : item
      )
    );
    setSelectedViolation((prev) =>
      prev && prev.id === v.id
        ? { ...prev, status: 'CONFIRMED_FINE_ISSUED', challanId, reviewedAt: new Date().toISOString() }
        : prev
    );
    setIsProcessing(false);
  };

  const handleDismiss = async (v: ViolationReport) => {
    setIsProcessing(true);
    await updateViolationStatus(v.id, 'DISMISSED');
    setViolations((prev) =>
      prev.map((item) =>
        item.id === v.id
          ? { ...item, status: 'DISMISSED', reviewedAt: new Date().toISOString() }
          : item
      )
    );
    setSelectedViolation((prev) =>
      prev && prev.id === v.id ? { ...prev, status: 'DISMISSED' } : prev
    );
    setIsProcessing(false);
  };

  // Metrics
  const pendingCount = violations.filter((v) => v.status === 'PENDING_REVIEW').length;
  const issuedFinesSum = violations
    .filter((v) => v.status === 'CONFIRMED_FINE_ISSUED')
    .reduce((acc, curr) => acc + curr.fineInr, 0);

  return (
    <div className="flex flex-col gap-5">
      
      {/* Header & Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500">
            Pending Officer Review
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-amber-400">{pendingCount}</span>
            <span className="text-xs text-zinc-400">grievances in queue</span>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500">
            Statutory Fines Levied
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-400">INR {issuedFinesSum.toLocaleString()}</span>
            <span className="text-xs text-zinc-400">GCC Zone 11 Treasury</span>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
          <div className="text-[10px] font-mono uppercase tracking-wider text-zinc-500">
            SWM 2016 Enforcement Parity
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-cyan-400">100%</span>
            <span className="text-xs text-zinc-400">GPS Evidence Audit</span>
          </div>
        </div>
      </div>

      {/* Main Split Review Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        
        {/* Left: Grievance Queue Table */}
        <div className="lg:col-span-2 rounded-xl border border-zinc-800 bg-zinc-950 p-4 shadow-xl">
          <div className="border-b border-zinc-800 pb-3 flex items-center justify-between">
            <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
              <FileText className="h-4 w-4 text-emerald-400" />
              SWM 2016 Grievance Docket (Zone 11 Valasaravakkam)
            </h3>
            <span className="font-mono text-xs text-zinc-500">
              Total: {violations.length} reports
            </span>
          </div>

          <div className="mt-3 divide-y divide-zinc-800/80 overflow-hidden">
            {violations.map((v) => {
              const isSelected = selectedViolation?.id === v.id;
              return (
                <div
                  key={v.id}
                  onClick={() => setSelectedViolation(v)}
                  className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 transition-colors cursor-pointer rounded-lg ${
                    isSelected ? 'bg-zinc-800/90' : 'hover:bg-zinc-900/60'
                  }`}
                >
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-zinc-200">{v.id}</span>
                      <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] font-mono text-zinc-400">
                        Ward {v.ward}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-mono font-medium ${
                          v.status === 'CONFIRMED_FINE_ISSUED'
                            ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                            : v.status === 'DISMISSED'
                            ? 'bg-zinc-800 text-zinc-400'
                            : 'bg-amber-950/80 text-amber-400 border border-amber-800/60'
                        }`}
                      >
                        {v.status === 'CONFIRMED_FINE_ISSUED'
                          ? 'Challan Issued'
                          : v.status === 'DISMISSED'
                          ? 'Dismissed'
                          : 'Pending Review'}
                      </span>
                    </div>
                    <div className="text-xs text-zinc-300 font-medium">{v.category}</div>
                    <div className="text-[11px] text-zinc-500 truncate">{v.location}</div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="font-mono text-xs font-bold text-amber-400">
                        INR {v.fineInr}
                      </div>
                      <div className="text-[10px] font-mono text-zinc-500">{v.ruleCode}</div>
                    </div>
                    <Eye className="h-4 w-4 text-zinc-500" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Evidentiary Audit & e-Challan Issuance Panel */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4 shadow-xl flex flex-col justify-between">
          <div>
            <div className="border-b border-zinc-800 pb-3 flex items-center justify-between">
              <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400">
                Evidentiary Audit Desk
              </span>
              <Stamp className="h-4 w-4 text-emerald-400" />
            </div>

            {selectedViolation ? (
              <div className="mt-4 flex flex-col gap-4 text-xs">
                
                {/* Evidence Image */}
                <div className="relative h-44 w-full overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900">
                  <Image
                    src={selectedViolation.evidenceUrl || '/defaultimage.jpeg'}
                    alt="Evidentiary proof photo"
                    fill
                    className="object-cover"
                  />
                  <div className="absolute bottom-2 left-2 rounded bg-zinc-950/80 px-2 py-0.5 font-mono text-[10px] text-zinc-300 backdrop-blur-sm">
                    Preloaded: defaultimage.jpeg
                  </div>
                </div>

                {/* Details */}
                <div className="flex flex-col gap-2 font-mono">
                  <div className="rounded border border-zinc-900 bg-zinc-900/40 p-2 text-zinc-400">
                    <div className="text-[10px] text-zinc-500">Statutory Infraction</div>
                    <div className="text-zinc-200 font-bold mt-0.5">{selectedViolation.category}</div>
                  </div>
                  <div className="rounded border border-zinc-900 bg-zinc-900/40 p-2 text-zinc-400">
                    <div className="text-[10px] text-zinc-500">Rule Cited</div>
                    <div className="text-amber-400 font-bold mt-0.5">{selectedViolation.ruleCode}</div>
                  </div>
                  <div className="rounded border border-zinc-900 bg-zinc-900/40 p-2 text-zinc-400">
                    <div className="text-[10px] text-zinc-500">Location Record</div>
                    <div className="text-zinc-300 mt-0.5">{selectedViolation.location}</div>
                  </div>
                  {selectedViolation.challanId && (
                    <div className="rounded border border-emerald-900/50 bg-emerald-950/30 p-2 text-emerald-300">
                      <div className="text-[10px] text-emerald-500">GCC e-Challan Reference</div>
                      <div className="font-bold mt-0.5">{selectedViolation.challanId}</div>
                    </div>
                  )}
                </div>

              </div>
            ) : (
              <div className="mt-10 text-center text-zinc-500 text-xs">
                Select a grievance from the left to view evidence and issue challan.
              </div>
            )}
          </div>

          {/* Action buttons */}
          {selectedViolation && (
            <div className="mt-5 flex flex-col gap-2 border-t border-zinc-800 pt-3">
              {selectedViolation.status === 'PENDING_REVIEW' ? (
                <>
                  <button
                    onClick={() => handleIssueChallan(selectedViolation)}
                    disabled={isProcessing}
                    className="flex items-center justify-center gap-2 rounded-lg border border-emerald-500/40 bg-emerald-600/20 py-2.5 text-xs font-bold text-emerald-300 hover:bg-emerald-600/30 hover:border-emerald-500 transition-all"
                  >
                    <CheckCircle className="h-4 w-4" />
                    <span>Issue GCC e-Challan (INR {selectedViolation.fineInr})</span>
                  </button>
                  <button
                    onClick={() => handleDismiss(selectedViolation)}
                    disabled={isProcessing}
                    className="flex items-center justify-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900 py-2 text-xs font-medium text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
                  >
                    <XCircle className="h-3.5 w-3.5" />
                    <span>Dismiss Grievance</span>
                  </button>
                </>
              ) : (
                <div className="rounded-lg bg-zinc-900 p-2.5 text-center font-mono text-xs text-zinc-400">
                  Status: <strong>{selectedViolation.status}</strong>
                </div>
              )}
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
