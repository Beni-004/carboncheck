import {
  Controller,
  Get,
  Post,
  Put,
  Body,
  Param,
  Query,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ProgrammeService } from '../services/programme.service';
import {
  CreateProgrammeDto,
  UpdateProgrammeDto,
  ProgrammeQueryDto,
  IssueCreditDto,
  TransferCreditDto,
  RetireCreditDto,
} from '../dto/programme.dto';

@Controller('programmes')
export class ProgrammeController {
  constructor(private readonly programmeService: ProgrammeService) {}

  /**
   * Create a new programme
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(@Body() dto: CreateProgrammeDto) {
    return this.programmeService.create(dto);
  }

  /**
   * Query programmes with filters
   */
  @Get()
  async query(@Query() dto: ProgrammeQueryDto) {
    return this.programmeService.query(dto);
  }

  /**
   * Get programme statistics
   */
  @Get('statistics')
  async getStatistics() {
    return this.programmeService.getStatistics();
  }

  /**
   * Get programme by ID
   */
  @Get(':id')
  async findById(@Param('id') id: string) {
    return this.programmeService.findById(id);
  }

  /**
   * Get programme by external ID
   */
  @Get('external/:externalId')
  async findByExternalId(@Param('externalId') externalId: string) {
    return this.programmeService.findByExternalId(externalId);
  }

  /**
   * Update programme
   */
  @Put(':id')
  async update(@Param('id') id: string, @Body() dto: UpdateProgrammeDto) {
    return this.programmeService.update(id, dto);
  }

  /**
   * Authorize a programme
   */
  @Post(':id/authorize')
  @HttpCode(HttpStatus.OK)
  async authorize(@Param('id') id: string) {
    return this.programmeService.authorize(id);
  }

  /**
   * Reject a programme
   */
  @Post(':id/reject')
  @HttpCode(HttpStatus.OK)
  async reject(@Param('id') id: string, @Body('reason') reason?: string) {
    return this.programmeService.reject(id, reason);
  }

  /**
   * Issue credits to a programme
   */
  @Post('credits/issue')
  @HttpCode(HttpStatus.OK)
  async issueCredits(@Body() dto: IssueCreditDto) {
    return this.programmeService.issueCredits(dto);
  }

  /**
   * Transfer credits between companies
   */
  @Post('credits/transfer')
  @HttpCode(HttpStatus.OK)
  async transferCredits(@Body() dto: TransferCreditDto) {
    return this.programmeService.transferCredits(dto);
  }

  /**
   * Retire credits
   */
  @Post('credits/retire')
  @HttpCode(HttpStatus.OK)
  async retireCredits(@Body() dto: RetireCreditDto) {
    return this.programmeService.retireCredits(dto);
  }
}
