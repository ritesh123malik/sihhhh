-- ============================================================================
-- SONARIS Underwater Anomaly Detection System - Supabase PostgreSQL Schema
-- ============================================================================

-- 1. Enable PostGIS Extension for Underwater Georeferencing
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Scan Runs Table
CREATE TABLE IF NOT EXISTS public.runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_path TEXT,
    annotated_path TEXT,
    detection_count INT DEFAULT 0,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326),
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Detections Table
CREATE TABLE IF NOT EXISTS public.detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES public.runs(run_id) ON DELETE CASCADE,
    mission_id TEXT,
    filename TEXT,
    class_label TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    risk_level TEXT NOT NULL,
    bbox_x DOUBLE PRECISION,
    bbox_y DOUBLE PRECISION,
    bbox_w DOUBLE PRECISION,
    bbox_h DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    depth_m DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Reports Table
CREATE TABLE IF NOT EXISTS public.reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES public.runs(run_id) ON DELETE CASCADE,
    mission_id TEXT NOT NULL,
    mission_name TEXT NOT NULL,
    scan_date TEXT,
    anomaly_count INT DEFAULT 0,
    confidence DOUBLE PRECISION,
    high_risk_count INT DEFAULT 0,
    medium_risk_count INT DEFAULT 0,
    low_risk_count INT DEFAULT 0,
    kind TEXT DEFAULT 'original',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Spatial & Performance Indices
CREATE INDEX IF NOT EXISTS idx_runs_geom ON public.runs USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_detections_run_id ON public.detections (run_id);
CREATE INDEX IF NOT EXISTS idx_reports_run_id ON public.reports (run_id);

-- 6. Storage Buckets Setup (Public)
INSERT INTO storage.buckets (id, name, public)
VALUES ('sonar-scans', 'sonar-scans', true),
       ('sonar-outputs', 'sonar-outputs', true)
ON CONFLICT (id) DO NOTHING;

-- Storage Policies for Public Access
CREATE POLICY "Public Read Scans" ON storage.objects FOR SELECT USING (bucket_id = 'sonar-scans');
CREATE POLICY "Public Upload Scans" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'sonar-scans');
CREATE POLICY "Public Read Outputs" ON storage.objects FOR SELECT USING (bucket_id = 'sonar-outputs');
CREATE POLICY "Public Upload Outputs" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'sonar-outputs');
