import { IsString, IsNumber, IsOptional, IsEnum, IsArray, ValidateNested } from 'class-validator';
import { Type } from 'class-transformer';
import { ProgrammeStage, Sector, SectoralScope } from '../enums/programme-status.enum';

export class CreateProgrammeDto {
  @IsString()
  title: string;

  @IsOptional()
  @IsString()
  externalId?: string;

  @IsOptional()
  @IsEnum(SectoralScope)
  sectoralScope?: SectoralScope;

  @IsOptional()
  @IsEnum(Sector)
  sector?: Sector;

  @IsOptional()
  @IsString()
  countryCodeA2?: string;

  @IsOptional()
  @IsNumber()
  startTime?: number;

  @IsOptional()
  @IsNumber()
  endTime?: number;

  @IsOptional()
  @IsNumber()
  creditEst?: number;

  @IsOptional()
  @IsNumber()
  emissionReductionExpected?: number;

  @IsOptional()
  @IsString()
  creditUnit?: string;

  @IsOptional()
  @IsArray()
  companyId?: number[];

  @IsOptional()
  programmeProperties?: Record<string, any>;

  @IsOptional()
  geographicalLocationCordintes?: Record<string, any>;

  @IsOptional()
  @IsArray()
  projectLocation?: Record<string, any>[];
}

export class UpdateProgrammeDto {
  @IsOptional()
  @IsString()
  title?: string;

  @IsOptional()
  @IsEnum(ProgrammeStage)
  currentStage?: ProgrammeStage;

  @IsOptional()
  @IsNumber()
  creditEst?: number;

  @IsOptional()
  @IsNumber()
  emissionReductionExpected?: number;

  @IsOptional()
  @IsNumber()
  emissionReductionAchieved?: number;

  @IsOptional()
  @IsNumber()
  creditIssued?: number;

  @IsOptional()
  @IsNumber()
  creditBalance?: number;

  @IsOptional()
  programmeProperties?: Record<string, any>;

  @IsOptional()
  mitigationActions?: Record<string, any>[];
}

export class ProgrammeQueryDto {
  @IsOptional()
  @IsNumber()
  page?: number = 1;

  @IsOptional()
  @IsNumber()
  size?: number = 10;

  @IsOptional()
  @IsEnum(ProgrammeStage)
  stage?: ProgrammeStage;

  @IsOptional()
  @IsEnum(Sector)
  sector?: Sector;

  @IsOptional()
  @IsString()
  countryCode?: string;

  @IsOptional()
  @IsNumber()
  companyId?: number;
}

export class IssueCreditDto {
  @IsString()
  programmeId: string;

  @IsNumber()
  creditAmount: number;

  @IsOptional()
  @IsString()
  comment?: string;
}

export class TransferCreditDto {
  @IsString()
  programmeId: string;

  @IsNumber()
  fromCompanyId: number;

  @IsNumber()
  toCompanyId: number;

  @IsNumber()
  creditAmount: number;

  @IsOptional()
  @IsString()
  comment?: string;
}

export class RetireCreditDto {
  @IsString()
  programmeId: string;

  @IsNumber()
  companyId: number;

  @IsNumber()
  creditAmount: number;

  @IsOptional()
  @IsString()
  retirementType?: string;

  @IsOptional()
  @IsString()
  comment?: string;
}

export class ProgrammeResponseDto {
  programmeId: string;
  serialNo: string;
  title: string;
  externalId: string;
  sectoralScope: SectoralScope;
  sector: Sector;
  countryCodeA2: string;
  currentStage: ProgrammeStage;
  startTime: number;
  endTime: number;
  creditEst: number;
  emissionReductionExpected: number;
  emissionReductionAchieved: number;
  creditIssued: number;
  creditBalance: number;
  creditRetired: number[];
  creditTransferred: number[];
  companyId: number[];
  creditUnit: string;
  programmeProperties: Record<string, any>;
  geographicalLocationCordintes: Record<string, any>;
  projectLocation: Record<string, any>[];
  createdAt: Date;
  updatedAt: Date;
}
