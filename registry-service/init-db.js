// Database initialization script for Railway
// Run this ONCE to create tables: railway run node init-db.js

const { DataSource } = require('typeorm');

const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.REGISTRY_DB_HOST || process.env.PGHOST,
  port: parseInt(process.env.REGISTRY_DB_PORT || process.env.PGPORT || '5432', 10),
  username: process.env.REGISTRY_DB_USER || process.env.PGUSER,
  password: process.env.REGISTRY_DB_PASSWORD || process.env.PGPASSWORD,
  database: process.env.REGISTRY_DB_NAME || process.env.PGDATABASE,
  entities: ['dist/entities/*.entity.js'],
  synchronize: true, // Only for initialization
  logging: true,
});

async function initializeDatabase() {
  try {
    console.log('🔌 Connecting to database...');
    await AppDataSource.initialize();

    console.log('✅ Database connected!');
    console.log('📊 Tables created/synchronized successfully');

    await AppDataSource.destroy();
    console.log('✨ Initialization complete!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error during initialization:', error);
    process.exit(1);
  }
}

initializeDatabase();
