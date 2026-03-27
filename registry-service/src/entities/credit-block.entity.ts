import { Entity, Column, PrimaryColumn, BeforeInsert } from 'typeorm';
import { TxType } from '../enums/programme-status.enum';

/**
 * CreditBlock Entity - Represents issued carbon credit blocks
 */
@Entity('credit_blocks')
export class CreditBlock {
  @PrimaryColumn()
  creditBlockId: string;

  @Column()
  txRef: string;

  @Column('jsonb', { nullable: true })
  txData: Record<string, any>;

  @Column({
    type: 'enum',
    enum: TxType,
  })
  txType: TxType;

  @Column({ type: 'bigint' })
  txTime: number;

  @Column('jsonb', { default: [] })
  transactionRecords: Record<string, any>[];

  @Column({ type: 'bigint', nullable: true })
  previousOwnerCompanyId: number;

  @Column({ type: 'bigint' })
  ownerCompanyId: number;

  @Column({ type: 'text' })
  projectRefId: string;

  @Column({ type: 'text' })
  serialNumber: string;

  @Column({ type: 'text' })
  vintage: string;

  @Column()
  creditAmount: number;

  @Column({ type: 'boolean', default: true })
  isNotTransferred: boolean;

  @Column({ default: 0 })
  reservedCreditAmount: number;

  @Column({ type: 'bigint' })
  createTime: number;

  @BeforeInsert()
  async timestampAtInsert() {
    this.createTime = new Date().getTime();
  }
}
