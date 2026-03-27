import { Entity, Column, PrimaryColumn, CreateDateColumn } from 'typeorm';
import { CompanyRole, CompanyState, SectoralScope } from '../enums/programme-status.enum';

/**
 * Company Entity - Organizations participating in the carbon registry
 * Includes project developers, certifiers, government bodies
 */
@Entity('companies')
export class Company {
  @PrimaryColumn()
  companyId: number;

  @Column({ unique: true, nullable: true })
  taxId: string;

  @Column({ unique: true, nullable: true })
  paymentId: string;

  @Column()
  name: string;

  @Column({ unique: true, nullable: true })
  email: string;

  @Column({ nullable: true })
  phoneNo: string;

  @Column({ nullable: true })
  website: string;

  @Column({ nullable: true })
  address: string;

  @Column({ nullable: true })
  logo: string;

  @Column({ nullable: true })
  country: string;

  @Column({
    type: 'enum',
    enum: CompanyRole,
  })
  companyRole: CompanyRole;

  @Column({
    type: 'enum',
    enum: CompanyState,
    default: CompanyState.ACTIVE,
  })
  state: CompanyState;

  @Column('decimal', { nullable: true })
  creditBalance: number;

  @Column({
    type: 'jsonb',
    nullable: true,
  })
  secondaryAccountBalance: Record<string, any>;

  @Column('bigint', { nullable: true })
  programmeCount: number;

  @Column({ nullable: true })
  remarks: string;

  @Column({ type: 'bigint', nullable: true })
  createdTime: number;

  @Column({
    type: 'jsonb',
    nullable: true,
  })
  geographicalLocationCordintes: Record<string, any>;

  @Column('varchar', { array: true, nullable: true })
  regions: string[];

  @Column('varchar', { array: true, nullable: true })
  sectoralScope: SectoralScope[];

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;
}
