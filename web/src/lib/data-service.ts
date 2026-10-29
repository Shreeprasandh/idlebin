import { supabase } from './supabase/client';
import { BinNode, ViolationReport, RvmTransaction, DispatchRoute } from '@/types/idlebin';

export const DEFAULT_BINS: BinNode[] = [
  { id: 'IB-RAM-01', name: 'Ramapuram Market Gate A', ward: 154, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0315, lng: 80.1815, fillLevel: 92, batteryLevel: 98, status: 'Action Required', strokeCount: 412, lastEmptiedAt: new Date(Date.now() - 48 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-02', name: 'SRM Hospital Transit Junction', ward: 154, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0345, lng: 80.1790, fillLevel: 48, batteryLevel: 95, status: 'Optimal', strokeCount: 188, lastEmptiedAt: new Date(Date.now() - 14 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-03', name: 'Bharathi Nagar Commercial Lane', ward: 154, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0280, lng: 80.1840, fillLevel: 78, batteryLevel: 92, status: 'Action Required', strokeCount: 345, lastEmptiedAt: new Date(Date.now() - 32 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-04', name: 'MGR Nagar Bus Stop Terminal', ward: 155, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0360, lng: 80.1865, fillLevel: 34, batteryLevel: 100, status: 'Optimal', strokeCount: 120, lastEmptiedAt: new Date(Date.now() - 6 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-05', name: 'Rayala Nagar Residential Park', ward: 155, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0295, lng: 80.1760, fillLevel: 18, batteryLevel: 97, status: 'Optimal', strokeCount: 74, lastEmptiedAt: new Date(Date.now() - 8 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-06', name: 'Mount-Poonamallee High Road Junction', ward: 153, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0385, lng: 80.1740, fillLevel: 85, batteryLevel: 91, status: 'Action Required', strokeCount: 510, lastEmptiedAt: new Date(Date.now() - 40 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-07', name: 'Arignar Anna Street Produce Hub', ward: 154, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0330, lng: 80.1835, fillLevel: 62, batteryLevel: 94, status: 'Optimal', strokeCount: 230, lastEmptiedAt: new Date(Date.now() - 22 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-08', name: 'Kalaignar Karunanidhi Salai Corner', ward: 155, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0265, lng: 80.1795, fillLevel: 29, batteryLevel: 96, status: 'Optimal', strokeCount: 95, lastEmptiedAt: new Date(Date.now() - 11 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-09', name: 'Narasimhan Street Community Hall', ward: 154, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0305, lng: 80.1870, fillLevel: 74, batteryLevel: 88, status: 'Action Required', strokeCount: 315, lastEmptiedAt: new Date(Date.now() - 29 * 3600 * 1000).toISOString() },
  { id: 'IB-RAM-10', name: 'Ramapuram Lake Promenade North', ward: 154, zone: 'Zone 11 (Valasaravakkam)', lat: 13.0370, lng: 80.1805, fillLevel: 41, batteryLevel: 99, status: 'Optimal', strokeCount: 160, lastEmptiedAt: new Date(Date.now() - 19 * 3600 * 1000).toISOString() }
];

export const DEFAULT_VIOLATIONS: ViolationReport[] = [
  {
    id: 'GCC-VIO-2026-9041',
    ward: 154,
    zone: 'Zone 11 (Valasaravakkam)',
    location: 'Ramapuram Market Gate A - Shop #42',
    lat: 13.0315,
    lng: 80.1815,
    ruleCode: 'Rule 15(1)(g)',
    category: 'Commercial Unsegregated Waste',
    fineInr: 500,
    status: 'PENDING_REVIEW',
    evidenceUrl: '/defaultimage.jpeg',
    challanId: null,
    submittedAt: new Date(Date.now() - 42 * 60 * 1000).toISOString(),
    reviewedAt: null
  },
  {
    id: 'GCC-VIO-2026-9042',
    ward: 154,
    zone: 'Zone 11 (Valasaravakkam)',
    location: 'SRM Dental College Outer Perimeter',
    lat: 13.0345,
    lng: 80.1790,
    ruleCode: 'Rule 15(2)',
    category: 'Non-Biodegradable Single-Use Plastic Dumping',
    fineInr: 1000,
    status: 'CONFIRMED_FINE_ISSUED',
    evidenceUrl: '/defaultimage.jpeg',
    challanId: 'CHN-Z11-CH-00918',
    submittedAt: new Date(Date.now() - 180 * 60 * 1000).toISOString(),
    reviewedAt: new Date(Date.now() - 95 * 60 * 1000).toISOString()
  },
  {
    id: 'GCC-VIO-2026-9043',
    ward: 155,
    zone: 'Zone 11 (Valasaravakkam)',
    location: 'MGR Nagar 3rd Main Road',
    lat: 13.0360,
    lng: 80.1865,
    ruleCode: 'Rule 4(1)(a)',
    category: 'Open Street Littering & Secondary Dumping',
    fineInr: 500,
    status: 'PENDING_REVIEW',
    evidenceUrl: '/defaultimage.jpeg',
    challanId: null,
    submittedAt: new Date(Date.now() - 65 * 60 * 1000).toISOString(),
    reviewedAt: null
  }
];

const LOCAL_STORAGE_BINS = 'idlebin_bins_cache';
const LOCAL_STORAGE_VIOLATIONS = 'idlebin_violations_cache';

export async function getBins(): Promise<BinNode[]> {
  try {
    const { data, error } = await supabase.from('bins').select('*').order('id', { ascending: true });
    if (!error && data && data.length > 0) {
      return data.map((b: any) => ({
        id: b.id,
        name: b.name,
        ward: b.ward,
        zone: b.zone,
        lat: Number(b.lat),
        lng: Number(b.lng),
        fillLevel: Number(b.fill_level),
        batteryLevel: Number(b.battery_level),
        status: b.status,
        strokeCount: Number(b.stroke_count),
        lastEmptiedAt: b.last_emptied_at
      }));
    }
  } catch (err) {
    // Supabase query fallback
  }

  if (typeof window !== 'undefined') {
    const cached = localStorage.getItem(LOCAL_STORAGE_BINS);
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch (e) {}
    }
    localStorage.setItem(LOCAL_STORAGE_BINS, JSON.stringify(DEFAULT_BINS));
  }
  return DEFAULT_BINS;
}

export async function saveBinUpdate(id: string, updates: Partial<BinNode>): Promise<void> {
  try {
    const payload: any = { updated_at: new Date().toISOString() };
    if (updates.fillLevel !== undefined) payload.fill_level = updates.fillLevel;
    if (updates.batteryLevel !== undefined) payload.battery_level = updates.batteryLevel;
    if (updates.status !== undefined) payload.status = updates.status;
    if (updates.strokeCount !== undefined) payload.stroke_count = updates.strokeCount;
    if (updates.lastEmptiedAt !== undefined) payload.last_emptied_at = updates.lastEmptiedAt;

    await supabase.from('bins').update(payload).eq('id', id);
  } catch (e) {
    // Supabase update error handled gracefully
  }

  if (typeof window !== 'undefined') {
    const cached = localStorage.getItem(LOCAL_STORAGE_BINS);
    let list: BinNode[] = cached ? JSON.parse(cached) : [...DEFAULT_BINS];
    list = list.map(b => b.id === id ? { ...b, ...updates } : b);
    localStorage.setItem(LOCAL_STORAGE_BINS, JSON.stringify(list));
  }
}

export async function getViolations(): Promise<ViolationReport[]> {
  try {
    const { data, error } = await supabase.from('violations').select('*').order('submitted_at', { ascending: false });
    if (!error && data && data.length > 0) {
      return data.map((v: any) => ({
        id: v.id,
        ward: v.ward,
        zone: v.zone,
        location: v.location,
        lat: v.lat ? Number(v.lat) : undefined,
        lng: v.lng ? Number(v.lng) : undefined,
        ruleCode: v.rule_code,
        category: v.category,
        fineInr: Number(v.fine_inr),
        status: v.status,
        evidenceUrl: v.evidence_url,
        challanId: v.challan_id,
        submittedAt: v.submitted_at,
        reviewedAt: v.reviewed_at
      }));
    }
  } catch (err) {
    // Fallback
  }

  if (typeof window !== 'undefined') {
    const cached = localStorage.getItem(LOCAL_STORAGE_VIOLATIONS);
    if (cached) {
      try {
        return JSON.parse(cached);
      } catch (e) {}
    }
    localStorage.setItem(LOCAL_STORAGE_VIOLATIONS, JSON.stringify(DEFAULT_VIOLATIONS));
  }
  return DEFAULT_VIOLATIONS;
}

export async function addViolation(report: ViolationReport): Promise<void> {
  try {
    await supabase.from('violations').insert({
      id: report.id,
      ward: report.ward,
      zone: report.zone,
      location: report.location,
      lat: report.lat,
      lng: report.lng,
      rule_code: report.ruleCode,
      category: report.category,
      fine_inr: report.fineInr,
      status: report.status,
      evidence_url: report.evidenceUrl,
      challan_id: report.challanId,
      submitted_at: report.submittedAt
    });
  } catch (e) {}

  if (typeof window !== 'undefined') {
    const cached = localStorage.getItem(LOCAL_STORAGE_VIOLATIONS);
    const list: ViolationReport[] = cached ? JSON.parse(cached) : [...DEFAULT_VIOLATIONS];
    list.unshift(report);
    localStorage.setItem(LOCAL_STORAGE_VIOLATIONS, JSON.stringify(list));
  }
}

export async function updateViolationStatus(id: string, status: ViolationReport['status'], challanId?: string): Promise<void> {
  const reviewedAt = new Date().toISOString();
  try {
    await supabase.from('violations').update({
      status,
      challan_id: challanId || null,
      reviewed_at: reviewedAt
    }).eq('id', id);
  } catch (e) {}

  if (typeof window !== 'undefined') {
    const cached = localStorage.getItem(LOCAL_STORAGE_VIOLATIONS);
    let list: ViolationReport[] = cached ? JSON.parse(cached) : [...DEFAULT_VIOLATIONS];
    list = list.map(v => v.id === id ? { ...v, status, challanId: challanId || v.challanId, reviewedAt } : v);
    localStorage.setItem(LOCAL_STORAGE_VIOLATIONS, JSON.stringify(list));
  }
}

export async function recordRvmDeposit(tx: RvmTransaction): Promise<void> {
  try {
    await supabase.from('rvm_transactions').insert({
      id: tx.id,
      bin_id: tx.binId,
      bottles_deposited: tx.bottlesDeposited,
      weight_grams: tx.weightGrams,
      cashback_inr: tx.cashbackInr,
      upi_id: tx.upiId,
      payout_status: tx.payoutStatus,
      created_at: tx.createdAt
    });
  } catch (e) {}
}
