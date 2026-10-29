export type BinStatus = 'Optimal' | 'Action Required' | 'Critical Jam' | 'Off-Grid';

export interface BinNode {
  id: string;
  name: string;
  ward: number;
  zone: string;
  lat: number;
  lng: number;
  fillLevel: number;
  batteryLevel: number;
  status: BinStatus;
  strokeCount: number;
  lastEmptiedAt: string;
}

export interface TelemetryReading {
  id?: number;
  binId: string;
  distanceCm: number;
  fillPercentage: number;
  batteryMv: number;
  jamDetected: boolean;
  recordedAt: string;
}

export type ViolationStatus = 'PENDING_REVIEW' | 'CONFIRMED_FINE_ISSUED' | 'DISMISSED';

export interface ViolationReport {
  id: string;
  ward: number;
  zone: string;
  location: string;
  lat?: number;
  lng?: number;
  ruleCode: string;
  category: string;
  fineInr: number;
  status: ViolationStatus;
  evidenceUrl: string;
  challanId?: string | null;
  submittedAt: string;
  reviewedAt?: string | null;
}

export interface RvmTransaction {
  id: string;
  binId: string;
  bottlesDeposited: number;
  weightGrams: number;
  cashbackInr: number;
  upiId: string;
  payoutStatus: 'COMPLETED' | 'PENDING' | 'FAILED';
  createdAt: string;
}

export interface DispatchRoute {
  id: string;
  vehicleNumber: string;
  driverName: string;
  status: 'SCHEDULED' | 'EN_ROUTE' | 'COMPLETED' | 'CANCELLED';
  assignedBins: string[];
  distanceKm: number;
  fuelSavedLitres: number;
  co2AvoidedKg: number;
  currentBinIndex?: number;
  startedAt: string;
}
