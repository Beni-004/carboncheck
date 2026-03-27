import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import configuration from './config/configuration';
import { Programme, Company, ProgrammeTransfer, User, CreditBlock } from './entities';
import { ProgrammeService } from './services/programme.service';
import { ProgrammeController } from './controllers/programme.controller';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
    }),
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get<string>('database.host'),
        port: configService.get<number>('database.port'),
        username: configService.get<string>('database.username'),
        password: configService.get<string>('database.password'),
        database: configService.get<string>('database.database'),
        entities: [Programme, Company, ProgrammeTransfer, User, CreditBlock],
        synchronize: configService.get<boolean>('database.synchronize'),
        logging: configService.get('database.logging'),
      }),
      inject: [ConfigService],
    }),
    TypeOrmModule.forFeature([Programme, Company, ProgrammeTransfer, User, CreditBlock]),
  ],
  controllers: [ProgrammeController],
  providers: [ProgrammeService],
  exports: [ProgrammeService],
})
export class AppModule {}
