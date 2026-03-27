import { Entity, Column, PrimaryColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { ProgrammeStage, Sector, SectoralScope, TxType } from '../enums/programme-status.enum';

/**
 * Programme Entity - Core carbon credit programme/project representation
 * Mapped from UNDP National Carbon Registry Programme entity
 */
@Entity('programmes')
export class Programme {
  @PrimaryColumn()
  programmeId: string;

  @Column({ nullable: true })
  serialNo: string;

  @Column()
  title: string;

  @Column({ unique: true, nullable: true })
  externalId: string;

  @Column({
    type: 'enum',
    enum: SectoralScope,
    nullable: true,
  })
  sectoralScope: SectoralScope;

  @Column({
    type: 'enum',
    enum: Sector,
    nullable: true,
  })
  sector: Sector;

  @Column({ nullable: true })
  countryCodeA2: string;

  @Column({
    type: 'enum',
    enum: ProgrammeStage,
    default: ProgrammeStage.AWAITING_AUTHORIZATION,
  })
  currentStage: ProgrammeStage;

  @Column({ type: 'bigint', nullable: true })
  startTime: number;

  @Column({ type: 'bigint', nullable: true })
  endTime: number;

  @Column({ type: 'decimal', precision: 15, scale: 5, nullable: true })
  creditEst: number;

  @Column({ type: 'decimal', precision: 15, scale: 5, nullable: true })
  emissionReductionExpected: number;

  @Column({ type: 'decimal', precision: 15, scale: 5, nullable: true })
  emissionReductionAchieved: number;

  @Column({ type: 'decimal', precision: 15, scale: 5, nullable: true })
  creditChange: number;

  @Column({ type: 'decimal', precision: 15, scale: 5, nullable: true })
  creditIssued: number;

  @Column({ type: 'decimal', precision: 15, scale: 5, nullable: true })
  creditBalance: number;

  @Column('decimal', { array: true, nullable: true })
  creditRetired: number[];

  @Column('decimal', { array: true, nullable: true })
  creditFrozen: number[];

  @Column('decimal', { array: true, nullable: true })
  creditTransferred: number[];

  @Column({ nullable: true })
  constantVersion: string;

  @Column('varchar', { array: true, nullable: true })
  proponentTaxVatId: string[];

  @Column('bigint', { array: true, nullable: true })
  companyId: number[];

  @Column({ nullable: true })
  creditUnit: string;

  @Column({
    type: 'jsonb',
    nullable: true,
  })
  programmeProperties: Record<string, any>;

  @Column('jsonb', { nullable: true })
  mitigationActions: Record<string, any>[];

  @Column({ type: 'bigint', nullable: true })
  txTime: number;

  @Column({ type: 'bigint', nullable: true })
  createdTime: number;

  @Column({ type: 'bigint', nullable: true })
  authTime: number;

  @Column({ type: 'bigint', nullable: true })
  creditUpdateTime: number;

  @Column({ type: 'bigint', nullable: true })
  statusUpdateTime: number;

  @Column({ type: 'bigint', nullable: true })
  certifiedTime: number;

  @Column({ nullable: true })
  txRef: string;

  @Column({
    type: 'enum',
    enum: TxType,
    nullable: true,
  })
  txType: TxType;

  @Column({
    type: 'jsonb',
    nullable: true,
  })
  geographicalLocationCordintes: Record<string, any>;

  @Column({
    type: 'jsonb',
    nullable: true,
  })
  projectLocation: Record<string, any>[];

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
