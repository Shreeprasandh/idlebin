'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { Coins, QrCode, Upload, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';
import { addViolation, recordRvmDeposit } from '@/lib/data-service';

export default function CitizenPortal() {
  // RVM state
  const [bottleCount, setBottleCount] = useState(4);
  const [upiId, setUpiId] = useState('citizen.chennai@okhdfcbank');
  const [payoutSuccess, setPayoutSuccess] = useState(false);
  const [txnId, setTxnId] = useState('');

  // Violation complaint state
  const [category, setCategory] = useState('Commercial Unsegregated Waste');
  const [ruleCode, setRuleCode] = useState('Rule 15(1)(g)');
  const [location, setLocation] = useState('Ramapuram Market Gate A - Shop #42');
  const [ward, setWard] = useState(154);
  const [fineInr, setFineInr] = useState(500);
  const [evidenceUrl, setEvidenceUrl] = useState('/defaultimage.jpeg');
  const [submittingGrievance, setSubmittingGrievance] = useState(false);
  const [grievanceSubmitted, setGrievanceSubmitted] = useState(false);

  // Cashback math
  const cashbackPerBottle = 1.50; // INR 1.50 per 500ml bottle
  const totalCashback = (bottleCount * cashbackPerBottle).toFixed(2);
  const totalWeightGrams = bottleCount * 22; // 22g per PET bottle

  const handleRvmPayout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (bottleCount <= 0 || !upiId) return;

    const id = `TXN-RVM-${Math.floor(100000 + Math.random() * 900000)}`;
    await recordRvmDeposit({
      id,
      binId: 'IB-RAM-01',
      bottlesDeposited: bottleCount,
      weightGrams: totalWeightGrams,
      cashbackInr: Number(totalCashback),
      upiId,
      payoutStatus: 'COMPLETED',
      createdAt: new Date().toISOString()
    });

    setTxnId(id);
    setPayoutSuccess(true);
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setCategory(val);
    if (val === 'Commercial Unsegregated Waste') {
      setRuleCode('Rule 15(1)(g)');
      setFineInr(500);
    } else if (val === 'Non-Biodegradable Single-Use Plastic Dumping') {
      setRuleCode('Rule 15(2)');
      setFineInr(1000);
    } else if (val === 'Open Street Littering & Secondary Dumping') {
      setRuleCode('Rule 4(1)(a)');
      setFineInr(500);
    } else if (val === 'Construction & Demolition Debris Infiltration') {
      setRuleCode('Rule 15(1)(e)');
      setFineInr(2000);
    }
  };

  const handleGrievanceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingGrievance(true);

    const newId = `GCC-VIO-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    await addViolation({
      id: newId,
      ward: Number(ward),
      zone: 'Zone 11 (Valasaravakkam)',
      location,
      ruleCode,
      category,
      fineInr,
      status: 'PENDING_REVIEW',
      evidenceUrl,
      challanId: null,
      submittedAt: new Date().toISOString(),
      reviewedAt: null
    });

    setSubmittingGrievance(false);
    setGrievanceSubmitted(true);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      {/* 1. Citizen Reverse Vending PWA (Cashback) */}
      <div className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-950 p-5 shadow-xl">
        <div className="border-b border-zinc-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Coins className="h-5 w-5 text-emerald-400" />
            <h2 className="text-base font-bold text-zinc-100">
              Plastic Deposit & Instant UPI Cashback
            </h2>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Reverse Vending Machine (RVM) Civic Incentive: INR 1.50 per crushed PET bottle
          </p>
        </div>

        {payoutSuccess ? (
          <div className="mt-6 flex flex-col items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-950/20 p-6 text-center">
            <CheckCircle2 className="h-10 w-10 text-emerald-400" />
            <h3 className="mt-3 text-base font-bold text-zinc-100">
              Cashback Dispatched Successfully
            </h3>
            <p className="text-xs text-zinc-300 font-mono mt-1">
              INR {totalCashback} transferred to {upiId}
            </p>
            <div className="mt-3 rounded-md bg-zinc-900 px-3 py-1 text-xs font-mono text-zinc-400">
              Ref Hash: {txnId}
            </div>
            <button
              onClick={() => {
                setPayoutSuccess(false);
                setBottleCount(1);
              }}
              className="mt-5 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-100 hover:bg-zinc-700 transition-colors"
            >
              Deposit More Bottles
            </button>
          </div>
        ) : (
          <form onSubmit={handleRvmPayout} className="mt-5 flex flex-col gap-4 text-xs">
            
            {/* Bottle Count Stepper */}
            <div>
              <label className="text-zinc-300 font-medium block mb-1.5">
                Number of Crushed Bottles
              </label>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setBottleCount((p) => Math.max(1, p - 1))}
                  className="h-10 w-10 rounded-lg border border-zinc-700 bg-zinc-900 text-base font-bold text-zinc-200 hover:bg-zinc-800 transition-colors"
                >
                  -
                </button>
                <div className="flex-1 rounded-lg border border-zinc-800 bg-zinc-900/80 py-2.5 text-center font-mono text-base font-bold text-emerald-400">
                  {bottleCount} Bottles
                </div>
                <button
                  type="button"
                  onClick={() => setBottleCount((p) => p + 1)}
                  className="h-10 w-10 rounded-lg border border-zinc-700 bg-zinc-900 text-base font-bold text-zinc-200 hover:bg-zinc-800 transition-colors"
                >
                  +
                </button>
              </div>
            </div>

            {/* Metric Overview */}
            <div className="grid grid-cols-2 gap-3 font-mono">
              <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/50 p-3">
                <span className="text-[10px] text-zinc-500 uppercase">Calculated Weight</span>
                <div className="mt-1 text-sm font-bold text-zinc-200">
                  {totalWeightGrams} grams
                </div>
              </div>
              <div className="rounded-lg border border-zinc-800/80 bg-zinc-900/50 p-3">
                <span className="text-[10px] text-zinc-500 uppercase">Cashback Entitlement</span>
                <div className="mt-1 text-sm font-bold text-emerald-400">
                  INR {totalCashback}
                </div>
              </div>
            </div>

            {/* UPI ID Input */}
            <div>
              <label className="text-zinc-300 font-medium block mb-1.5">
                Recipient UPI VPA / PhonePe / GPay
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={upiId}
                  onChange={(e) => setUpiId(e.target.value)}
                  placeholder="username@okhdfcbank"
                  required
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2.5 font-mono text-xs text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:outline-none"
                />
                <QrCode className="absolute right-3 top-2.5 h-4 w-4 text-zinc-500" />
              </div>
            </div>

            {/* Submit Payout Button */}
            <button
              type="submit"
              className="mt-2 flex items-center justify-center gap-2 rounded-lg border border-emerald-500/40 bg-emerald-600/20 py-3 text-xs font-bold text-emerald-300 hover:bg-emerald-600/30 hover:border-emerald-500 active:scale-[0.99] transition-all"
            >
              <span>Disburse INR {totalCashback} via NPCI UPI</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>

          </form>
        )}
      </div>

      {/* 2. GCC SWM 2016 Civic Grievance Reporting */}
      <div className="flex flex-col rounded-xl border border-zinc-800 bg-zinc-950 p-5 shadow-xl">
        <div className="border-b border-zinc-800/80 pb-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-amber-400" />
            <h2 className="text-base font-bold text-zinc-100">
              GCC SWM 2016 Civic Grievance Portal
            </h2>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Statutory Municipal Enforcement under Tamil Nadu Municipal Acts & SWM Rules 2016
          </p>
        </div>

        {grievanceSubmitted ? (
          <div className="mt-6 flex flex-col items-center justify-center rounded-lg border border-amber-500/30 bg-amber-950/20 p-6 text-center">
            <CheckCircle2 className="h-10 w-10 text-amber-400" />
            <h3 className="mt-3 text-base font-bold text-zinc-100">
              Grievance Registered for Enforcement
            </h3>
            <p className="text-xs text-zinc-300 mt-1">
              Transmitted to Zone 11 Conservancy Inspector queue. Statutory fine of INR {fineInr} under {ruleCode} queued.
            </p>
            <button
              onClick={() => setGrievanceSubmitted(false)}
              className="mt-5 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-xs font-semibold text-zinc-100 hover:bg-zinc-700 transition-colors"
            >
              Report Another Violation
            </button>
          </div>
        ) : (
          <form onSubmit={handleGrievanceSubmit} className="mt-5 flex flex-col gap-4 text-xs">
            
            {/* Category Dropdown (with custom Chevron positioned perfectly 16px from right edge) */}
            <div>
              <label className="text-zinc-300 font-medium block mb-1.5">
                Statutory Violation Category
              </label>
              <div className="relative">
                <select
                  value={category}
                  onChange={handleCategoryChange}
                  className="w-full appearance-none rounded-lg border border-zinc-800 bg-zinc-900 py-2.5 pl-3 pr-10 text-xs font-medium text-zinc-100 focus:border-amber-500 focus:outline-none cursor-pointer"
                >
                  <option value="Commercial Unsegregated Waste">Commercial Unsegregated Waste - Rule 15(1)(g)</option>
                  <option value="Non-Biodegradable Single-Use Plastic Dumping">Non-Biodegradable Single-Use Plastic Dumping - Rule 15(2)</option>
                  <option value="Open Street Littering & Secondary Dumping">Open Street Littering & Secondary Dumping - Rule 4(1)(a)</option>
                  <option value="Construction & Demolition Debris Infiltration">Construction & Demolition Debris - Rule 15(1)(e)</option>
                </select>

                {/* Custom Chevron SVG placed exactly 16px from the right boundary */}
                <div className="pointer-events-none absolute inset-y-0 right-4 flex items-center">
                  <svg className="h-4 w-4 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Location & Ward */}
            <div className="grid grid-cols-3 gap-2">
              <div className="col-span-2">
                <label className="text-zinc-300 font-medium block mb-1.5">
                  Location / Landmark
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  required
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs text-zinc-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-zinc-300 font-medium block mb-1.5">
                  GCC Ward
                </label>
                <input
                  type="number"
                  value={ward}
                  onChange={(e) => setWard(Number(e.target.value))}
                  required
                  className="w-full rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs font-mono text-zinc-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Evidence Image Preview (Preloaded with defaultimage.jpeg) */}
            <div>
              <label className="text-zinc-300 font-medium block mb-1.5 flex justify-between items-center">
                <span>Evidentiary Photograph</span>
                <span className="text-[10px] font-mono text-emerald-400">Pre-loaded: defaultimage.jpeg</span>
              </label>

              <div className="relative flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900/60 p-2.5">
                <div className="relative h-14 w-20 shrink-0 overflow-hidden rounded-md border border-zinc-700 bg-zinc-950">
                  <Image
                    src={evidenceUrl}
                    alt="Evidentiary Proof"
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="flex-1 text-[11px] text-zinc-400">
                  <div className="font-mono text-zinc-200 truncate">defaultimage.jpeg</div>
                  <div className="text-[10px] text-zinc-500 mt-0.5">EXIF Timestamp: GPS 13.0315 N, 80.1815 E</div>
                </div>
              </div>
            </div>

            {/* Fine and Rule summary */}
            <div className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-900/40 p-2.5 font-mono text-xs">
              <span className="text-zinc-400">Statutory Fine Payable:</span>
              <span className="font-bold text-amber-400">INR {fineInr} ({ruleCode})</span>
            </div>

            {/* Submit Grievance */}
            <button
              type="submit"
              disabled={submittingGrievance}
              className="mt-1 flex items-center justify-center gap-2 rounded-lg border border-amber-500/40 bg-amber-600/20 py-2.5 text-xs font-bold text-amber-300 hover:bg-amber-600/30 hover:border-amber-500 active:scale-[0.99] transition-all"
            >
              <span>{submittingGrievance ? 'Transmitting to GCC...' : 'Transmit Grievance to Ward Officer'}</span>
            </button>

          </form>
        )}
      </div>

    </div>
  );
}
