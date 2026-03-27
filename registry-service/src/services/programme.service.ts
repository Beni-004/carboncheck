import { Injectable, Logger, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository, FindOptionsWhere } from 'typeorm';
import { Programme } from '../entities/programme.entity';
import { ProgrammeStage, TxType } from '../enums/programme-status.enum';
import {
  CreateProgrammeDto,
  UpdateProgrammeDto,
  ProgrammeQueryDto,
  IssueCreditDto,
  TransferCreditDto,
  RetireCreditDto,
} from '../dto/programme.dto';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class ProgrammeService {
  private readonly logger = new Logger(ProgrammeService.name);

  constructor(
    @InjectRepository(Programme)
    private programmeRepo: Repository<Programme>,
  ) {}

  /**
   * Create a new programme/project in the registry
   */
  async create(dto: CreateProgrammeDto): Promise<Programme> {
    const programmeId = `PRG-${uuidv4().substring(0, 8).toUpperCase()}`;
    const now = new Date().getTime();

    const programme = this.programmeRepo.create({
      programmeId,
      ...dto,
      currentStage: ProgrammeStage.AWAITING_AUTHORIZATION,
      txTime: now,
      createdTime: now,
      txType: TxType.CREATE,
      creditBalance: 0,
      creditIssued: 0,
      emissionReductionAchieved: 0,
    });

    return this.programmeRepo.save(programme);
  }

  /**
   * Find programme by ID
   */
  async findById(programmeId: string): Promise<Programme> {
    const programme = await this.programmeRepo.findOne({
      where: { programmeId },
    });
    if (!programme) {
      throw new NotFoundException(`Programme ${programmeId} not found`);
    }
    return programme;
  }

  /**
   * Find programme by external ID
   */
  async findByExternalId(externalId: string): Promise<Programme | null> {
    return this.programmeRepo.findOne({ where: { externalId } });
  }

  /**
   * Query programmes with filters and pagination
   */
  async query(dto: ProgrammeQueryDto): Promise<{ data: Programme[]; total: number }> {
    const { page = 1, size = 10, stage, sector, countryCode, companyId } = dto;
    const skip = (page - 1) * size;

    const where: FindOptionsWhere<Programme> = {};
    if (stage) where.currentStage = stage;
    if (sector) where.sector = sector;
    if (countryCode) where.countryCodeA2 = countryCode;

    const queryBuilder = this.programmeRepo.createQueryBuilder('programme');

    if (stage) queryBuilder.andWhere('programme.currentStage = :stage', { stage });
    if (sector) queryBuilder.andWhere('programme.sector = :sector', { sector });
    if (countryCode) queryBuilder.andWhere('programme.countryCodeA2 = :countryCode', { countryCode });
    if (companyId) queryBuilder.andWhere(':companyId = ANY(programme.companyId)', { companyId });

    const [data, total] = await queryBuilder
      .orderBy('programme.createdTime', 'DESC')
      .skip(skip)
      .take(size)
      .getManyAndCount();

    return { data, total };
  }

  /**
   * Get all programmes (for leaderboard/stats)
   */
  async findAll(): Promise<Programme[]> {
    return this.programmeRepo.find({
      order: { createdTime: 'DESC' },
    });
  }

  /**
   * Update programme details
   */
  async update(programmeId: string, dto: UpdateProgrammeDto): Promise<Programme> {
    const programme = await this.findById(programmeId);

    Object.assign(programme, dto, {
      txTime: new Date().getTime(),
      statusUpdateTime: new Date().getTime(),
    });

    return this.programmeRepo.save(programme);
  }

  /**
   * Authorize a programme
   */
  async authorize(programmeId: string): Promise<Programme> {
    const programme = await this.findById(programmeId);

    if (programme.currentStage !== ProgrammeStage.AWAITING_AUTHORIZATION) {
      throw new BadRequestException(`Programme ${programmeId} cannot be authorized in current state`);
    }

    programme.currentStage = ProgrammeStage.AUTHORIZED;
    programme.authTime = new Date().getTime();
    programme.txType = TxType.AUTH;
    programme.txTime = new Date().getTime();

    return this.programmeRepo.save(programme);
  }

  /**
   * Reject a programme
   */
  async reject(programmeId: string, reason?: string): Promise<Programme> {
    const programme = await this.findById(programmeId);

    programme.currentStage = ProgrammeStage.REJECTED;
    programme.txType = TxType.REJECT;
    programme.txTime = new Date().getTime();
    programme.txRef = reason;

    return this.programmeRepo.save(programme);
  }

  /**
   * Issue credits to a programme
   */
  async issueCredits(dto: IssueCreditDto): Promise<Programme> {
    const programme = await this.findById(dto.programmeId);

    if (programme.currentStage !== ProgrammeStage.AUTHORIZED) {
      throw new BadRequestException('Credits can only be issued to authorized programmes');
    }

    programme.creditIssued = (programme.creditIssued || 0) + dto.creditAmount;
    programme.creditBalance = (programme.creditBalance || 0) + dto.creditAmount;
    programme.currentStage = ProgrammeStage.CREDIT_ISSUED;
    programme.txType = TxType.ISSUE;
    programme.txTime = new Date().getTime();
    programme.creditUpdateTime = new Date().getTime();
    programme.txRef = dto.comment;

    return this.programmeRepo.save(programme);
  }

  /**
   * Transfer credits between companies (simplified version)
   */
  async transferCredits(dto: TransferCreditDto): Promise<Programme> {
    const programme = await this.findById(dto.programmeId);

    if ((programme.creditBalance || 0) < dto.creditAmount) {
      throw new BadRequestException('Insufficient credit balance');
    }

    // Track transferred credits
    const transferred = programme.creditTransferred || [];
    transferred.push(dto.creditAmount);

    programme.creditBalance = (programme.creditBalance || 0) - dto.creditAmount;
    programme.creditTransferred = transferred;
    programme.txType = TxType.TRANSFER;
    programme.txTime = new Date().getTime();
    programme.creditUpdateTime = new Date().getTime();
    programme.txRef = dto.comment;

    if (programme.creditBalance > 0) {
      programme.currentStage = ProgrammeStage.CREDIT_TRANSFERRED;
    }

    return this.programmeRepo.save(programme);
  }

  /**
   * Retire credits
   */
  async retireCredits(dto: RetireCreditDto): Promise<Programme> {
    const programme = await this.findById(dto.programmeId);

    if ((programme.creditBalance || 0) < dto.creditAmount) {
      throw new BadRequestException('Insufficient credit balance');
    }

    const retired = programme.creditRetired || [];
    retired.push(dto.creditAmount);

    programme.creditBalance = (programme.creditBalance || 0) - dto.creditAmount;
    programme.creditRetired = retired;
    programme.txType = TxType.RETIRE;
    programme.txTime = new Date().getTime();
    programme.creditUpdateTime = new Date().getTime();
    programme.txRef = dto.comment;
    programme.currentStage = ProgrammeStage.CREDIT_RETIRED;

    return this.programmeRepo.save(programme);
  }

  /**
   * Get programme statistics
   */
  async getStatistics(): Promise<{
    totalProgrammes: number;
    totalCreditsIssued: number;
    totalCreditsRetired: number;
    totalCreditsTransferred: number;
    byStage: Record<string, number>;
    bySector: Record<string, number>;
  }> {
    const programmes = await this.programmeRepo.find();

    const stats = {
      totalProgrammes: programmes.length,
      totalCreditsIssued: 0,
      totalCreditsRetired: 0,
      totalCreditsTransferred: 0,
      byStage: {} as Record<string, number>,
      bySector: {} as Record<string, number>,
    };

    for (const p of programmes) {
      stats.totalCreditsIssued += Number(p.creditIssued) || 0;
      stats.totalCreditsRetired += (p.creditRetired || []).reduce((a, b) => a + Number(b), 0);
      stats.totalCreditsTransferred += (p.creditTransferred || []).reduce((a, b) => a + Number(b), 0);

      const stage = p.currentStage || 'Unknown';
      stats.byStage[stage] = (stats.byStage[stage] || 0) + 1;

      const sector = p.sector || 'Unknown';
      stats.bySector[sector] = (stats.bySector[sector] || 0) + 1;
    }

    return stats;
  }
}
