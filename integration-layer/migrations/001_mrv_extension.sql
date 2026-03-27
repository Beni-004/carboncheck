-- MRV Extension Schema for UNDP Carbon Registry Integration
-- Creates verification_results table and related structures

-- Create verification_results table
CREATE TABLE IF NOT EXISTS verification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(100) NOT NULL,

    -- Verification scores
    predicted_co2 DECIMAL(15, 5) NOT NULL,
    claimed_co2 DECIMAL(15, 5) NOT NULL,
    ndvi_avg DECIMAL(10, 6),
    ndvi_change DECIMAL(10, 6),
    anomaly_score DECIMAL(5, 4) NOT NULL DEFAULT 0,
    trust_score DECIMAL(5, 4) NOT NULL DEFAULT 0.5,

    -- Confidence and verdict
    confidence_low DECIMAL(15, 5),
    confidence_high DECIMAL(15, 5),
    verdict VARCHAR(20) NOT NULL CHECK (verdict IN ('VERIFIED', 'FLAGGED', 'REJECTED')),

    -- Metadata
    data_sources TEXT[] DEFAULT '{}',
    verification_metadata JSONB,

    -- Timestamps
    verification_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign key (if syncing with registry)
    registry_programme_id VARCHAR(100),

    -- Indexes
    CONSTRAINT verification_results_project_id_idx UNIQUE (project_id, verification_timestamp)
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_verification_project_id ON verification_results(project_id);
CREATE INDEX IF NOT EXISTS idx_verification_timestamp ON verification_results(verification_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_verification_verdict ON verification_results(verdict);
CREATE INDEX IF NOT EXISTS idx_verification_trust_score ON verification_results(trust_score DESC);

-- Create registry_sync_log table for tracking sync operations
CREATE TABLE IF NOT EXISTS registry_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_type VARCHAR(50) NOT NULL, -- 'programme', 'credit_issue', 'transfer', 'retire'
    registry_id VARCHAR(100) NOT NULL,
    local_id VARCHAR(100),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'success', 'failed')),
    error_message TEXT,
    request_payload JSONB,
    response_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sync_log_registry_id ON registry_sync_log(registry_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON registry_sync_log(status);

-- Create projects_extended table for additional MRV fields
CREATE TABLE IF NOT EXISTS projects_extended (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id VARCHAR(100) NOT NULL UNIQUE,

    -- Extended fields from UNDP registry
    registry_programme_id VARCHAR(100),
    serial_no VARCHAR(100),
    sectoral_scope VARCHAR(50),
    sector VARCHAR(50),
    country_code VARCHAR(5),

    -- Credit tracking
    credit_est DECIMAL(15, 5),
    credit_issued DECIMAL(15, 5) DEFAULT 0,
    credit_balance DECIMAL(15, 5) DEFAULT 0,
    credit_retired DECIMAL(15, 5) DEFAULT 0,
    credit_transferred DECIMAL(15, 5) DEFAULT 0,
    credit_unit VARCHAR(20) DEFAULT 'tCO2e',

    -- Status tracking
    registry_stage VARCHAR(50),
    is_authorized BOOLEAN DEFAULT FALSE,
    authorized_at TIMESTAMPTZ,

    -- Location data
    geographical_coordinates JSONB,
    project_locations JSONB,
    regions TEXT[],

    -- Company associations
    company_ids INTEGER[],
    proponent_tax_ids TEXT[],

    -- Programme properties (from registry)
    programme_properties JSONB,
    mitigation_actions JSONB,

    -- Timestamps
    registry_created_at TIMESTAMPTZ,
    registry_updated_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_ext_registry_id ON projects_extended(registry_programme_id);
CREATE INDEX IF NOT EXISTS idx_projects_ext_sector ON projects_extended(sector);
CREATE INDEX IF NOT EXISTS idx_projects_ext_country ON projects_extended(country_code);

-- Create view for leaderboard
CREATE OR REPLACE VIEW v_project_leaderboard AS
SELECT
    pe.project_id,
    pe.registry_programme_id,
    pe.credit_est as claimed_co2,
    COALESCE(vr.predicted_co2, pe.credit_est) as predicted_co2,
    COALESCE(vr.trust_score, 0.5) as trust_score,
    COALESCE(vr.anomaly_score, 0) as anomaly_score,
    COALESCE(vr.verdict, 'PENDING') as verdict,
    pe.sector,
    pe.country_code,
    pe.credit_issued,
    pe.credit_balance,
    pe.registry_stage,
    vr.verification_timestamp as last_verified_at,
    RANK() OVER (ORDER BY COALESCE(vr.trust_score, 0.5) DESC) as rank
FROM projects_extended pe
LEFT JOIN LATERAL (
    SELECT *
    FROM verification_results vr2
    WHERE vr2.project_id = pe.project_id
    ORDER BY vr2.verification_timestamp DESC
    LIMIT 1
) vr ON true
ORDER BY trust_score DESC;

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_verification_results_updated_at ON verification_results;
CREATE TRIGGER update_verification_results_updated_at
    BEFORE UPDATE ON verification_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_projects_extended_updated_at ON projects_extended;
CREATE TRIGGER update_projects_extended_updated_at
    BEFORE UPDATE ON projects_extended
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to insert verification result
CREATE OR REPLACE FUNCTION insert_verification_result(
    p_project_id VARCHAR(100),
    p_predicted_co2 DECIMAL(15, 5),
    p_claimed_co2 DECIMAL(15, 5),
    p_ndvi_avg DECIMAL(10, 6) DEFAULT NULL,
    p_ndvi_change DECIMAL(10, 6) DEFAULT NULL,
    p_anomaly_score DECIMAL(5, 4) DEFAULT 0,
    p_trust_score DECIMAL(5, 4) DEFAULT 0.5,
    p_confidence_low DECIMAL(15, 5) DEFAULT NULL,
    p_confidence_high DECIMAL(15, 5) DEFAULT NULL,
    p_verdict VARCHAR(20) DEFAULT 'FLAGGED',
    p_data_sources TEXT[] DEFAULT '{}',
    p_metadata JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO verification_results (
        project_id,
        predicted_co2,
        claimed_co2,
        ndvi_avg,
        ndvi_change,
        anomaly_score,
        trust_score,
        confidence_low,
        confidence_high,
        verdict,
        data_sources,
        verification_metadata
    ) VALUES (
        p_project_id,
        p_predicted_co2,
        p_claimed_co2,
        p_ndvi_avg,
        p_ndvi_change,
        p_anomaly_score,
        p_trust_score,
        p_confidence_low,
        p_confidence_high,
        p_verdict,
        p_data_sources,
        p_metadata
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your Supabase setup)
-- GRANT ALL ON verification_results TO authenticated;
-- GRANT ALL ON projects_extended TO authenticated;
-- GRANT ALL ON registry_sync_log TO service_role;
-- GRANT SELECT ON v_project_leaderboard TO authenticated;
