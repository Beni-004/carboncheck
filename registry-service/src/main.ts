import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new Logger('RegistryService');

  const app = await NestFactory.create(AppModule);

  // Enable CORS for integration with FastAPI
  app.enableCors({
    origin: '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
  });

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: true,
    }),
  );

  // Set global prefix
  app.setGlobalPrefix('api/v1');

  const configService = app.get(ConfigService);
  const port = configService.get<number>('port') || 3001;

  await app.listen(port);
  logger.log(`UNDP Registry Service is running on port ${port}`);
  logger.log(`API available at: http://localhost:${port}/api/v1/programmes`);
}

bootstrap();
