export default () => ({
  // Railway sets PORT, fallback to REGISTRY_PORT for local dev, then 3001
  port: parseInt(process.env.PORT || process.env.REGISTRY_PORT, 10) || 3001,
  database: {
    type: 'postgres',
    host: process.env.REGISTRY_DB_HOST || 'localhost',
    port: parseInt(process.env.REGISTRY_DB_PORT, 10) || 5432,
    username: process.env.REGISTRY_DB_USER || 'postgres',
    password: process.env.REGISTRY_DB_PASSWORD || '',
    database: process.env.REGISTRY_DB_NAME || 'carbon_registry',
    synchronize: process.env.NODE_ENV !== 'production',
    autoLoadEntities: true,
    logging: process.env.NODE_ENV !== 'production' ? ['error', 'query'] : ['error'],
  },
  systemCountry: process.env.SYSTEM_COUNTRY || 'NG',
  systemCountryName: process.env.SYSTEM_COUNTRY_NAME || 'Nigeria',
  defaultCreditUnit: process.env.DEFAULT_CREDIT_UNIT || 'tCO2e',
});
