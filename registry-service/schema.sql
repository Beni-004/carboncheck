-- UNDP Carbon Registry Database Schema
-- Run this ONCE on PostgreSQL before deploying the app

-- Create enum types
CREATE TYPE programme_stage AS ENUM (
  'AwaitingAuthorization',
  'Pending',
  'Authorised',
  'Rejected',
  'CreditIssued',
  'CreditTransferred',
  'CreditRetired'
);

CREATE TYPE sector AS ENUM (
  'Energy',
  'Health',
  'Education',
  'Transport',
  'Manufacturing',
  'Hospitality',
  'Forestry',
  'Waste',
  'Agriculture',
  'Other'
);

CREATE TYPE sectoral_scope AS ENUM (
  '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
  '11', '12', '13', '14', '15'
);

CREATE TYPE company_role AS ENUM (
  'IC',
  'PD',
  'API',
  'DNA',
  'Ministry',
  'ClimateFund',
  'ExecutiveCommittee'
);

CREATE TYPE company_state AS ENUM (
  '0', '1', '2', '3'
);

CREATE TYPE tx_type AS ENUM (
  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
);

CREATE TYPE transfer_status AS ENUM (
  'Pending',
  'Approved',
  'Rejected',
  'Cancelled',
  'Recognised',
  'NotRecognised'
);

CREATE TYPE user_role AS ENUM (
  'Root',
  'Admin',
  'Manager',
  'ViewOnly',
  'GovernmentUser',
  'AgencyAdmin',
  'AgencyViewOnly'
);

-- Create tables
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  role user_role NOT NULL DEFAULT 'ViewOnly',
  country VARCHAR,
  company_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS companies (
  company_id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  tax_id VARCHAR UNIQUE,
  email VARCHAR,
  phone_number VARCHAR,
  website VARCHAR,
  address VARCHAR,
  country VARCHAR,
  company_role company_role NOT NULL,
  state company_state DEFAULT '2',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS programmes (
  programme_id VARCHAR PRIMARY KEY,
  serial_no VARCHAR,
  title VARCHAR NOT NULL,
  external_id VARCHAR UNIQUE,
  sectoral_scope sectoral_scope,
  sector sector,
  country_code_a2 VARCHAR,
  current_stage programme_stage DEFAULT 'AwaitingAuthorization',
  start_time BIGINT,
  end_time BIGINT,
  credit_est DOUBLE PRECISION,
  emission_reduction_expected DOUBLE PRECISION,
  emission_reduction_achieved DOUBLE PRECISION,
  credit_issued DOUBLE PRECISION,
  credit_balance DOUBLE PRECISION,
  credit_retired DOUBLE PRECISION[],
  credit_transferred DOUBLE PRECISION[],
  company_id INTEGER[],
  credit_unit VARCHAR DEFAULT 'tCO2e',
  programme_properties JSONB,
  geographical_location_cordinates JSONB,
  project_location JSONB[],
  mitigation_actions JSONB[],
  tx_time BIGINT NOT NULL,
  tx_ref VARCHAR NOT NULL,
  credit_update_time BIGINT,
  tx_type tx_type NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS programme_transfers (
  request_id SERIAL PRIMARY KEY,
  programme_id VARCHAR NOT NULL REFERENCES programmes(programme_id),
  from_company_id INTEGER NOT NULL,
  to_company_id INTEGER NOT NULL,
  credit_amount DOUBLE PRECISION NOT NULL,
  comment VARCHAR,
  status transfer_status DEFAULT 'Pending',
  tx_id VARCHAR,
  tx_ref VARCHAR,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_blocks (
  credit_block_id VARCHAR PRIMARY KEY,
  programme_id VARCHAR NOT NULL REFERENCES programmes(programme_id),
  serial_number_start VARCHAR NOT NULL,
  serial_number_end VARCHAR NOT NULL,
  unit_count INTEGER NOT NULL,
  status VARCHAR DEFAULT 'Available',
  vintage_year INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_programmes_sector ON programmes(sector);
CREATE INDEX IF NOT EXISTS idx_programmes_stage ON programmes(current_stage);
CREATE INDEX IF NOT EXISTS idx_programmes_external_id ON programmes(external_id);
CREATE INDEX IF NOT EXISTS idx_transfers_programme ON programme_transfers(programme_id);
CREATE INDEX IF NOT EXISTS idx_transfers_status ON programme_transfers(status);
CREATE INDEX IF NOT EXISTS idx_credit_blocks_programme ON credit_blocks(programme_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;
