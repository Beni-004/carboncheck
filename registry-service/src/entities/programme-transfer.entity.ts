import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn } from 'typeorm';
import { TransferStatus } from '../enums/programme-status.enum';

/**
 * ProgrammeTransfer Entity - Tracks credit transfers between companies
 */
@Entity('programme_transfers')
export class ProgrammeTransfer {
  @PrimaryGeneratedColumn()
  requestId: number;

  @Column()
  programmeId: string;

  @Column()
  initiator: number;

  @Column()
  initiatorCompanyId: number;

  @Column()
  toCompanyId: number;

  @Column({ nullable: true })
  toAccount: string;

  @Column({
    type: 'jsonb',
    nullable: true,
  })
  toCompanyMeta: Record<string, any>;

  @Column({ nullable: true })
  retirementType: string;

  @Column()
  fromCompanyId: number;

  @Column('decimal')
  creditAmount: number;

  @Column({ nullable: true })
  comment: string;

  @Column({ nullable: true })
  txRef: string;

  @Column({ type: 'bigint' })
  txTime: number;

  @Column({ type: 'bigint', nullable: true })
  createdTime: number;

  @Column({ type: 'bigint', nullable: true })
  authTime: number;

  @Column({
    type: 'enum',
    enum: TransferStatus,
  })
  status: TransferStatus;

  @Column({ nullable: true, default: false })
  isRetirement: boolean;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;
}
