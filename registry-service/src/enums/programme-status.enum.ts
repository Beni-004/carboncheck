/**
 * Programme lifecycle stages in the UNDP Carbon Registry
 */
export enum ProgrammeStage {
  AWAITING_AUTHORIZATION = 'AwaitingAuthorization',
  PENDING = 'Pending',
  AUTHORIZED = 'Authorised',
  REJECTED = 'Rejected',
  CREDIT_ISSUED = 'CreditIssued',
  CREDIT_TRANSFERRED = 'CreditTransferred',
  CREDIT_RETIRED = 'CreditRetired',
}

export enum TransferStatus {
  PENDING = 'Pending',
  APPROVED = 'Approved',
  REJECTED = 'Rejected',
  CANCELLED = 'Cancelled',
  RECOGNISED = 'Recognised',
  NOT_RECOGNISED = 'NotRecognised',
}

export enum Sector {
  Energy = 'Energy',
  Health = 'Health',
  Education = 'Education',
  Transport = 'Transport',
  Manufacturing = 'Manufacturing',
  Hospitality = 'Hospitality',
  Forestry = 'Forestry',
  Waste = 'Waste',
  Agriculture = 'Agriculture',
  Other = 'Other',
}

export enum SectoralScope {
  EnergyIndustries = '1',
  EnergyDistribution = '2',
  EnergyDemand = '3',
  ManufacturingIndustries = '4',
  ChemicalIndustries = '5',
  Construction = '6',
  Transport = '7',
  MiningProduction = '8',
  MetalProduction = '9',
  FugitiveEmissions = '10',
  FugitiveEmissionsHalocarbons = '11',
  SolventsUse = '12',
  WasteHandlingDisposal = '13',
  AfforestationReforestation = '14',
  Agriculture = '15',
}

export enum CompanyRole {
  INDEPENDENT_CERTIFIER = 'IC',
  PROJECT_DEVELOPER = 'PD',
  API = 'API',
  DESIGNATED_NATIONAL_AUTHORITY = 'DNA',
  MINISTRY = 'Ministry',
  CLIMATE_FUND = 'ClimateFund',
  EXECUTIVE_COMMITTEE = 'ExecutiveCommittee',
}

export enum CompanyState {
  SUSPENDED = '0',
  ACTIVE = '1',
  PENDING = '2',
  REJECTED = '3',
}

export enum TxType {
  CREATE = '0',
  AUTH = '1',
  REJECT = '2',
  ISSUE = '3',
  TRANSFER = '4',
  CERTIFY = '5',
  REVOKE = '6',
  RETIRE = '7',
  FREEZE = '8',
  UNFREEZE = '9',
}
