-- Additional indexes and optimizations for MRV system
-- Run after 001_mrv_extension.sql

-- Create composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_verification_project_verdict
    ON verification_results(project_id, verdict, verification_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_projects_ext_sector_country
    ON projects_extended(sector, country_code);

-- Create function to get latest verification for a project
CREATE OR REPLACE FUNCTION get_latest_verification(p_project_id VARCHAR(100))
RETURNS TABLE (
    id UUID,
    project_id VARCHAR(100),
    predicted_co2 DECIMAL(15, 5),
    claimed_co2 DECIMAL(15, 5),
    ndvi_avg DECIMAL(10, 6),
    anomaly_score DECIMAL(5, 4),
    trust_score DECIMAL(5, 4),
    verdict VARCHAR(20),
    verification_timestamp TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        vr.id,
        vr.project_id,
        vr.predicted_co2,
        vr.claimed_co2,
        vr.ndvi_avg,
        vr.anomaly_score,
        vr.trust_score,
        vr.verdict,
        vr.verification_timestamp
    FROM verification_results vr
    WHERE vr.project_id = p_project_id
    ORDER BY vr.verification_timestamp DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Create function to get verification history
CREATE OR REPLACE FUNCTION get_verification_history(
    p_project_id VARCHAR(100),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    predicted_co2 DECIMAL(15, 5),
    claimed_co2 DECIMAL(15, 5),
    trust_score DECIMAL(5, 4),
    verdict VARCHAR(20),
    verification_timestamp TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        vr.id,
        vr.predicted_co2,
        vr.claimed_co2,
        vr.trust_score,
        vr.verdict,
        vr.verification_timestamp
    FROM verification_results vr
    WHERE vr.project_id = p_project_id
    ORDER BY vr.verification_timestamp DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Create statistics view
CREATE OR REPLACE VIEW v_verification_statistics AS
SELECT
    COUNT(*) as total_verifications,
    COUNT(DISTINCT project_id) as unique_projects,
    AVG(trust_score) as avg_trust_score,
    AVG(anomaly_score) as avg_anomaly_score,
    SUM(CASE WHEN verdict = 'VERIFIED' THEN 1 ELSE 0 END) as verified_count,
    SUM(CASE WHEN verdict = 'FLAGGED' THEN 1 ELSE 0 END) as flagged_count,
    SUM(CASE WHEN verdict = 'REJECTED' THEN 1 ELSE 0 END) as rejected_count,
    SUM(claimed_co2) as total_claimed_co2,
    SUM(predicted_co2) as total_predicted_co2,
    DATE_TRUNC('day', verification_timestamp) as verification_date
FROM verification_results
GROUP BY DATE_TRUNC('day', verification_timestamp)
ORDER BY verification_date DESC;

-- Create daily aggregation view
CREATE OR REPLACE VIEW v_daily_verification_summary AS
SELECT
    DATE_TRUNC('day', verification_timestamp)::DATE as date,
    COUNT(*) as verifications,
    AVG(trust_score)::DECIMAL(5,4) as avg_trust_score,
    SUM(CASE WHEN verdict = 'VERIFIED' THEN 1 ELSE 0 END)::INTEGER as verified,
    SUM(CASE WHEN verdict = 'FLAGGED' THEN 1 ELSE 0 END)::INTEGER as flagged,
    SUM(CASE WHEN verdict = 'REJECTED' THEN 1 ELSE 0 END)::INTEGER as rejected
FROM verification_results
WHERE verification_timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', verification_timestamp)
ORDER BY date DESC;
