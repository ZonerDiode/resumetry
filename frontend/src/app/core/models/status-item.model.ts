import { ApplicationStatus } from './application-status.enum';

export interface StatusItem {
  occurDate: string;
  status: ApplicationStatus;
}
