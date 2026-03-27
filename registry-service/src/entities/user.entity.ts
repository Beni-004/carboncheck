import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn } from 'typeorm';
import { CompanyRole } from '../enums/programme-status.enum';

/**
 * User Entity - Users within the carbon registry system
 */
export enum Role {
  Root = 'Root',
  Admin = 'Admin',
  Manager = 'Manager',
  ViewOnly = 'ViewOnly',
}

@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @Column({ select: false })
  password: string;

  @Column({
    type: 'enum',
    enum: Role,
    default: Role.ViewOnly,
  })
  role: Role;

  @Column()
  name: string;

  @Column()
  country: string;

  @Column({ nullable: true })
  phoneNo: string;

  @Column({ nullable: true })
  companyId: number;

  @Column({
    type: 'enum',
    enum: CompanyRole,
    default: CompanyRole.PROJECT_DEVELOPER,
  })
  companyRole: CompanyRole;

  @Column({ nullable: true, select: false })
  apiKey: string;

  @Column({ type: 'bigint', nullable: true })
  createdTime: number;

  @Column({ type: 'boolean', default: false })
  isPending: boolean;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;
}
