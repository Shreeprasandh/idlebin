-- ============================================================================
-- IDLEBIN MUNICIPAL SOLID WASTE COMPACTOR & CIVIC SUITE
-- Schema: PostgreSQL / Supabase
-- Target: Greater Chennai Corporation (GCC) Zone 11 Valasaravakkam & Ramapuram
-- ============================================================================

-- Enable essential extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. BINS (Municipal Compactors & Smart Nodes)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.bins (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    ward INTEGER NOT NULL DEFAULT 154,
    zone VARCHAR(64) NOT NULL DEFAULT 'Zone 11 (Valasaravakkam)',
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    fill_level INTEGER NOT NULL DEFAULT 0 CHECK (fill_level >= 0 AND fill_level <= 100),
    battery_level INTEGER NOT NULL DEFAULT 100 CHECK (battery_level >= 0 AND battery_level <= 100),
    status VARCHAR(32) NOT NULL DEFAULT 'Optimal' CHECK (status IN ('Optimal', 'Action Required', 'Critical Jam', 'Off-Grid')),
    stroke_count INTEGER NOT NULL DEFAULT 0,
    last_emptied_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 2. TELEMETRY READINGS (Ultrasonic HC-SR04 & Reed Switch Events)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.telemetry_readings (
    id BIGSERIAL PRIMARY KEY,
    bin_id VARCHAR(32) NOT NULL REFERENCES public.bins(id) ON DELETE CASCADE,
    distance_cm NUMERIC(6, 2) NOT NULL,
    fill_percentage INTEGER NOT NULL CHECK (fill_percentage >= 0 AND fill_percentage <= 100),
    battery_mv INTEGER NOT NULL,
    jam_detected BOOLEAN NOT NULL DEFAULT FALSE,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_bin_time ON public.telemetry_readings(bin_id, recorded_at DESC);

-- ----------------------------------------------------------------------------
-- 3. VIOLATIONS (SWM 2016 Civic Grievances & GCC Challans)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.violations (
    id VARCHAR(64) PRIMARY KEY,
    ward INTEGER NOT NULL DEFAULT 154,
    zone VARCHAR(64) NOT NULL DEFAULT 'Zone 11 (Valasaravakkam)',
    location VARCHAR(255) NOT NULL,
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    rule_code VARCHAR(64) NOT NULL,
    category VARCHAR(128) NOT NULL,
    fine_inr INTEGER NOT NULL DEFAULT 500,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING_REVIEW' CHECK (status IN ('PENDING_REVIEW', 'CONFIRMED_FINE_ISSUED', 'DISMISSED')),
    evidence_url TEXT,
    challan_id VARCHAR(64),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_violations_status ON public.violations(status);

-- ----------------------------------------------------------------------------
-- 4. RVM TRANSACTIONS (Citizen Plastic Bottle Deposits & UPI Cashback)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.rvm_transactions (
    id VARCHAR(64) PRIMARY KEY,
    bin_id VARCHAR(32) NOT NULL REFERENCES public.bins(id) ON DELETE CASCADE,
    bottles_deposited INTEGER NOT NULL CHECK (bottles_deposited > 0),
    weight_grams NUMERIC(8, 2) NOT NULL DEFAULT 0,
    cashback_inr NUMERIC(8, 2) NOT NULL DEFAULT 0,
    upi_id VARCHAR(128) NOT NULL,
    payout_status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED' CHECK (payout_status IN ('COMPLETED', 'PENDING', 'FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 5. DISPATCHES (Smart Collection Vehicle Routing & Fuel Optimization)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.dispatches (
    id VARCHAR(64) PRIMARY KEY,
    vehicle_number VARCHAR(32) NOT NULL DEFAULT 'TN-09-GCC-4412',
    driver_name VARCHAR(128) NOT NULL DEFAULT 'M. Shanmugam',
    status VARCHAR(32) NOT NULL DEFAULT 'EN_ROUTE' CHECK (status IN ('SCHEDULED', 'EN_ROUTE', 'COMPLETED', 'CANCELLED')),
    assigned_bins JSONB NOT NULL DEFAULT '[]'::JSONB,
    distance_km NUMERIC(6, 2) NOT NULL DEFAULT 0,
    fuel_saved_litres NUMERIC(6, 2) NOT NULL DEFAULT 0,
    co2_avoided_kg NUMERIC(6, 2) NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES (Eta Sentinel Compliance)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.bins ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.telemetry_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rvm_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dispatches ENABLE ROW LEVEL SECURITY;

-- 1. Bins policies
CREATE POLICY "Allow public read access to bins"
    ON public.bins FOR SELECT
    USING (true);

CREATE POLICY "Allow service role full access to bins"
    ON public.bins FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role' OR auth.role() = 'service_role');

CREATE POLICY "Allow anon update to bins telemetry"
    ON public.bins FOR UPDATE
    USING (true);

-- 2. Telemetry readings policies
CREATE POLICY "Allow public read access to telemetry"
    ON public.telemetry_readings FOR SELECT
    USING (true);

CREATE POLICY "Allow public insert to telemetry"
    ON public.telemetry_readings FOR INSERT
    WITH CHECK (true);

-- 3. Violations policies
CREATE POLICY "Allow public read access to violations"
    ON public.violations FOR SELECT
    USING (true);

CREATE POLICY "Allow public insert to violations"
    ON public.violations FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Allow service and officers update violations"
    ON public.violations FOR UPDATE
    USING (true);

-- 4. RVM Transactions policies
CREATE POLICY "Allow public read access to rvm transactions"
    ON public.rvm_transactions FOR SELECT
    USING (true);

CREATE POLICY "Allow public insert to rvm transactions"
    ON public.rvm_transactions FOR INSERT
    WITH CHECK (true);

-- 5. Dispatches policies
CREATE POLICY "Allow public read access to dispatches"
    ON public.dispatches FOR SELECT
    USING (true);

CREATE POLICY "Allow public update and insert to dispatches"
    ON public.dispatches FOR ALL
    USING (true);

-- ============================================================================
-- SEED DATA (GCC Zone 11 Ramapuram & Valasaravakkam)
-- ============================================================================

INSERT INTO public.bins (id, name, ward, zone, lat, lng, fill_level, battery_level, status, stroke_count)
VALUES
    ('IB-RAM-01', 'Ramapuram Market Gate A', 154, 'Zone 11 (Valasaravakkam)', 13.0315, 80.1815, 92, 98, 'Action Required', 412),
    ('IB-RAM-02', 'SRM Hospital Transit Junction', 154, 'Zone 11 (Valasaravakkam)', 13.0345, 80.1790, 48, 95, 'Optimal', 188),
    ('IB-RAM-03', 'Bharathi Nagar Commercial Lane', 154, 'Zone 11 (Valasaravakkam)', 13.0280, 80.1840, 78, 92, 'Action Required', 345),
    ('IB-RAM-04', 'MGR Nagar Bus Stop Terminal', 155, 'Zone 11 (Valasaravakkam)', 13.0360, 80.1865, 34, 100, 'Optimal', 120),
    ('IB-RAM-05', 'Rayala Nagar Residential Park', 155, 'Zone 11 (Valasaravakkam)', 13.0295, 80.1760, 18, 97, 'Optimal', 74),
    ('IB-RAM-06', 'Mount-Poonamallee High Road Junction', 153, 'Zone 11 (Valasaravakkam)', 13.0385, 80.1740, 85, 91, 'Action Required', 510),
    ('IB-RAM-07', 'Arignar Anna Street Produce Hub', 154, 'Zone 11 (Valasaravakkam)', 13.0330, 80.1835, 62, 94, 'Optimal', 230),
    ('IB-RAM-08', 'Kalaignar Karunanidhi Salai Corner', 155, 'Zone 11 (Valasaravakkam)', 13.0265, 80.1795, 29, 96, 'Optimal', 95),
    ('IB-RAM-09', 'Narasimhan Street Community Hall', 154, 'Zone 11 (Valasaravakkam)', 13.0305, 80.1870, 74, 88, 'Action Required', 315),
    ('IB-RAM-10', 'Ramapuram Lake Promenade North', 154, 'Zone 11 (Valasaravakkam)', 13.0370, 80.1805, 41, 99, 'Optimal', 160)
ON CONFLICT (id) DO UPDATE SET
    fill_level = EXCLUDED.fill_level,
    battery_level = EXCLUDED.battery_level,
    status = EXCLUDED.status,
    stroke_count = EXCLUDED.stroke_count;

-- Seed initial violations with default evidence image reference
INSERT INTO public.violations (id, ward, zone, location, lat, lng, rule_code, category, fine_inr, status, evidence_url, challan_id, submitted_at)
VALUES
    ('GCC-VIO-2026-9041', 154, 'Zone 11 (Valasaravakkam)', 'Ramapuram Market Gate A - Shop #42', 13.0315, 80.1815, 'Rule 15(1)(g)', 'Commercial Unsegregated Waste', 500, 'PENDING_REVIEW', '/defaultimage.jpeg', NULL, NOW() - INTERVAL '42 minutes'),
    ('GCC-VIO-2026-9042', 154, 'Zone 11 (Valasaravakkam)', 'SRM Dental College Outer Perimeter', 13.0345, 80.1790, 'Rule 15(2)', 'Non-Biodegradable Single-Use Plastic Dumping', 1000, 'CONFIRMED_FINE_ISSUED', '/defaultimage.jpeg', 'CHN-Z11-CH-00918', NOW() - INTERVAL '3 hours'),
    ('GCC-VIO-2026-9043', 155, 'Zone 11 (Valasaravakkam)', 'MGR Nagar 3rd Main Road', 13.0360, 80.1865, 'Rule 4(1)(a)', 'Open Street Littering & Secondary Dumping', 500, 'PENDING_REVIEW', '/defaultimage.jpeg', NULL, NOW() - INTERVAL '1 hour')
ON CONFLICT (id) DO NOTHING;
